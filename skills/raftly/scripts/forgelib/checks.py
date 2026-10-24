"""Project integrity checks shared by validate_project.py, state.py and CI."""

from __future__ import annotations

import re
from pathlib import Path

from . import SCHEMA_VERSION, docs, graph, model, yamlio
from . import evidence as ev
from . import gate as gatelib
from .fsutil import SKILL_ROOT, read_text
from .project import RECORD_DIRS, REGISTRIES, ForgeError, Project, parse_frontmatter
from .schema import validate_named

CORE_DOCS = ["PRODUCT.md", "ARCHITECTURE.md", "DECISIONS.md", "BUILD.md", "EXECUTIVE.md"]
DESIGN_DOCS = ["DESIGN.md", "DESIGN_SYSTEM.md"]

CERT_CLAIM_RE = re.compile(
    r"\b(?:(?:HIPAA|GDPR|CCPA|PCI(?:[- ]DSS)?|SOC ?2|ISO ?27001)[- ](?:compliant|certified)|"
    r"fully compliant|guaranteed (?:secure|compliant)|100% secure|unhackable|legally compliant)\b",
    re.I,
)
NEGATION_RE = re.compile(r"(not|never|no|cannot|can't|does not|doesn't|isn't|without|claim|claims|claiming|“|\")\W*(\w+\W+){0,4}$", re.I)
PLACEHOLDER_RE = re.compile(r"\{\{[^}]+\}\}|\bTODO\b|\bTBD\b|\bFIXME\b")


def role_ids() -> set[str]:
    data = yamlio.load_file(SKILL_ROOT / "core" / "roles.yaml")
    return {r["id"] for r in data["roles"]}


def blueprint_gaps(project: Project) -> list[str]:
    """Blueprint Completion Gate (spec section 66). Empty list == gate passes."""
    gaps: list[str] = []
    state = project.state()
    bp = state.get("blueprint", {})
    for section in model.BLUEPRINT_SECTIONS:
        if bp.get(section) not in ("COMPLETE", "NOT_APPLICABLE"):
            gaps.append(f"blueprint.{section} is {bp.get(section)} (needs COMPLETE or NOT_APPLICABLE)")
    required = list(CORE_DOCS)
    if bp.get("design") != "NOT_APPLICABLE":
        required += DESIGN_DOCS
    if bp.get("security") != "NOT_APPLICABLE":
        required.append("SECURITY.md")
    if bp.get("data") not in ("NOT_APPLICABLE", None) and (state["project"].get("profile") or {}).get("backend"):
        required.append("DATA_MODEL.md")
    for d in required:
        if not (project.forge / d).exists():
            gaps.append(f"missing document {d}")
    reqs = [r for r in project.registry("requirements.yaml") if r.get("status") == "ACTIVE"]
    musts = [r for r in reqs if r.get("priority") == "MUST"]
    if not musts:
        gaps.append("no ACTIVE MUST requirements recorded")
    features = {fm["id"]: fm for _, fm, _ in project.records("feature")}
    if not features:
        gaps.append("no feature specifications")
    for r in musts:
        mapped = set(r.get("features") or []) | {f for f, fm in features.items() if r["id"] in (fm.get("requirements") or [])}
        if not mapped:
            gaps.append(f"{r['id']} (MUST) is not mapped to any feature")
    if not project.records("decision"):
        gaps.append("no decision records (ADRs)")
    if not project.registry("assumptions.yaml"):
        gaps.append("no assumptions recorded (key assumptions must be explicit)")
    nodes = project.registry("build-graph.yaml")
    if not nodes:
        gaps.append("build graph is empty")
    else:
        gp = graph.problems(nodes)
        gaps.extend(f"build graph: {p}" for p in gp)
        prompt_names = {p.name for p in project.prompts()}
        for n in nodes:
            if n["status"] == "DROPPED":
                continue
            if not n.get("prompts"):
                gaps.append(f"{n['id']} has no implementation prompt")
            for pr in n.get("prompts", []):
                if pr not in prompt_names:
                    gaps.append(f"{n['id']} references missing prompt {pr}")
    build = project.forge / "BUILD.md"
    if build.exists() and not re.search(r"^#{2,3} .*test", read_text(build), re.I | re.M):
        gaps.append("BUILD.md has no test strategy section")
    if project.gate() is None:
        gaps.append("production gate not initialised (gate.py init)")
    return gaps


def validate(project: Project) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    project.require()

    # 1. state + schema version
    try:
        state = project.state()
    except (ForgeError, yamlio.YAMLError) as exc:
        return {"ok": False, "errors": [f"state.yaml: {exc}"], "warnings": []}
    sv = (state.get("engine") or {}).get("schema_version")
    if isinstance(sv, int) and sv < SCHEMA_VERSION:
        errors.append(f"state.yaml schema_version {sv} < {SCHEMA_VERSION}: run migrate_schema.py")
    elif isinstance(sv, int) and sv > SCHEMA_VERSION:
        errors.append(f"state.yaml schema_version {sv} is newer than this version ({SCHEMA_VERSION}): upgrade the skill")
    errors += [f"state.yaml {e}" for e in validate_named(state, "state")]

    # 2. registries
    for filename, (_key, schema) in REGISTRIES.items():
        p = project.forge / filename
        if p.exists():
            try:
                data = yamlio.load_file(p)
            except yamlio.YAMLError as exc:
                errors.append(f"{filename}: {exc}")
                continue
            errors += [f"{filename} {e}" for e in validate_named(data or {}, schema)]
    if (project.forge / "evidence.yaml").exists():
        errors += [f"evidence.yaml {e}" for e in validate_named(project.evidence(), "evidence")]
    gate = project.gate()
    if gate is not None:
        errors += [f"gate.yaml {e}" for e in validate_named(gate, "gate")]
    if errors:
        return {"ok": False, "errors": errors, "warnings": warnings}

    # 3. markdown records
    records: dict[str, dict[str, tuple[Path, dict, str]]] = {k: {} for k in RECORD_DIRS}
    for kind, (directory, schema) in RECORD_DIRS.items():
        d = project.forge / directory
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.md")):
            if p.name.lower() == "readme.md":
                continue
            try:
                fm, body = parse_frontmatter(read_text(p))
            except (ForgeError, yamlio.YAMLError) as exc:
                errors.append(f"{directory}/{p.name}: frontmatter: {exc}")
                continue
            if not fm:
                errors.append(f"{directory}/{p.name}: missing YAML frontmatter")
                continue
            errors += [f"{directory}/{p.name} {e}" for e in validate_named(fm, schema)]
            rid = fm.get("id")
            if rid:
                if not p.name.startswith(f"{rid}-") and p.stem != rid:
                    warnings.append(f"{directory}/{p.name}: filename should start with {rid}-")
                if rid in records[kind]:
                    errors.append(f"duplicate {kind} id {rid}")
                records[kind][rid] = (p, fm, body)

    known = project.all_known_ids()
    roles = role_ids()
    features = {k: v[1] for k, v in records["feature"].items()}
    decisions = records["decision"]
    reqs = {r["id"]: r for r in project.registry("requirements.yaml")}
    nodes = project.registry("build-graph.yaml")
    node_ids = {n["id"] for n in nodes}
    evidence = project.evidence()
    ev_ids = {r["id"] for r in evidence["records"]}
    prompt_names = {p.name for p in project.prompts()}

    # 4. reference integrity
    for n in nodes:
        for f in n.get("features", []):
            if f not in features:
                errors.append(f"build-graph {n['id']}: unknown feature {f}")
        for pr in n.get("prompts", []):
            if pr not in prompt_names:
                errors.append(f"build-graph {n['id']}: prompt file prompts/{pr} not found")
        for e in n.get("evidence", []):
            if e not in ev_ids:
                errors.append(f"build-graph {n['id']}: unknown evidence {e}")
    for fid, fm in features.items():
        if fm.get("node") and fm["node"] not in node_ids:
            errors.append(f"feature {fid}: unknown node {fm['node']}")
        for r in fm.get("requirements", []):
            if r not in reqs:
                errors.append(f"feature {fid}: unknown requirement {r}")
        for d in fm.get("decisions", []):
            if d not in decisions:
                errors.append(f"feature {fid}: unknown decision {d}")
        for d in fm.get("depends_on", []):
            if d not in features:
                errors.append(f"feature {fid}: depends on unknown feature {d}")
    for rid, r in reqs.items():
        for f in r.get("features", []) or []:
            if f not in features:
                errors.append(f"requirement {rid}: unknown feature {f}")
        if r.get("superseded_by") and r["superseded_by"] not in reqs:
            errors.append(f"requirement {rid}: superseded_by unknown {r['superseded_by']}")
        if r.get("status") == "SUPERSEDED" and not r.get("superseded_by"):
            errors.append(f"requirement {rid}: SUPERSEDED requires superseded_by")
        for d in r.get("decisions", []) or []:
            if d not in decisions:
                errors.append(f"requirement {rid}: unknown decision {d}")
    for did, (_p, fm, body) in decisions.items():
        if fm.get("owner_role") not in roles:
            errors.append(f"{did}: owner_role '{fm.get('owner_role')}' is not a known role (core/roles.yaml)")
        for s in fm.get("supersedes", []):
            if s not in decisions:
                errors.append(f"{did}: supersedes unknown {s}")
        if fm.get("superseded_by") and fm["superseded_by"] not in decisions:
            errors.append(f"{did}: superseded_by unknown {fm['superseded_by']}")
        if fm.get("status") == "SUPERSEDED" and not fm.get("superseded_by"):
            errors.append(f"{did}: SUPERSEDED requires superseded_by")
        type1 = fm.get("type1") or fm.get("reversibility") == "low" or fm.get("impact") == "high"
        if type1 and fm.get("status") == "ACCEPTED" and not fm.get("revisit_trigger"):
            errors.append(f"{did}: Type-1 decision needs a revisit_trigger (rule 24)")
        if type1 and not docs.find_section(body, "Options considered", "Options"):
            warnings.append(f"{did}: Type-1 decision should list options considered")
        if fm.get("override") and not fm["override"].get("consequences"):
            warnings.append(f"{did}: override recorded without consequences")
        for e in fm.get("evidence", []):
            if e not in ev_ids and not e.startswith(("http", "RESEARCH", "research/")):
                warnings.append(f"{did}: evidence reference '{e}' is not an EV id, URL or research note")
    for risk in project.registry("risks.yaml"):
        if risk.get("owner_role") not in roles:
            errors.append(f"risk {risk['id']}: owner_role '{risk.get('owner_role')}' is not a known role")
    for a in project.registry("assumptions.yaml"):
        for rel in a.get("related", []) or []:
            if rel not in known:
                warnings.append(f"assumption {a['id']}: related id {rel} not found")
    for _, (_p, fm, _b) in records["debt"].items():
        if fm.get("owner_role") not in roles:
            errors.append(f"{fm['id']}: owner_role '{fm.get('owner_role')}' is not a known role")
    for link in evidence["links"]:
        for end in (link["from"], link["to"]):
            if end not in known:
                errors.append(f"evidence link {link['from']} -{link['relation']}-> {link['to']}: unknown id {end}")
    for rec in evidence["records"]:
        if rec["subject"] not in known and not gate_has(gate, rec["subject"]):
            errors.append(f"evidence {rec['id']}: unknown subject {rec['subject']}")
    for dep in project.registry("dependencies.yaml"):
        for c in dep.get("chosen_by", []) or []:
            if c not in known:
                warnings.append(f"dependency {dep['name']}: chosen_by {c} not found")
        if dep.get("status") == "ADOPTED" and str(dep.get("license", "")).upper() in ("", "UNKNOWN", "UNVERIFIED"):
            warnings.append(f"dependency {dep['name']}: ADOPTED with unverified license")
    ex = state.get("execution") or {}
    if ex.get("current_node") and ex["current_node"] not in node_ids:
        errors.append(f"state.execution.current_node {ex['current_node']} not in build graph")
    for nn in ex.get("next_nodes") or []:
        if nn not in node_ids:
            errors.append(f"state.execution.next_nodes: {nn} not in build graph")
    for docname, meta in (state.get("documents") or {}).items():
        if meta.get("status") != "NOT_APPLICABLE" and not (project.forge / docname).exists():
            errors.append(f"state.documents lists {docname} but the file does not exist")

    # 5. graph
    errors += [f"build-graph: {p}" for p in graph.problems(nodes)]

    # 6. status integrity (Constitution 13-15)
    verified = ev.verified_subjects(evidence)
    for fid, (_p, fm, body) in records["feature"].items():
        st = fm.get("status")
        if st in model.DONE_STATUSES and fid not in verified:
            errors.append(f"feature {fid} is {st} without passing verification evidence")
        if st == "COMPLETE":
            dod = docs.find_section(body, "Definition of Done")
            items = docs.checklist(dod or "")
            open_items = [i for s, i in items if s == "open"]
            if not items:
                errors.append(f"feature {fid} is COMPLETE but has no Definition of Done checklist")
            elif open_items:
                errors.append(f"feature {fid} is COMPLETE with {len(open_items)} unchecked DoD item(s)")
    for n in nodes:
        if n["status"] in model.DONE_STATUSES and n["id"] not in verified and not (
            n.get("features") and all(f in verified for f in n["features"])
        ):
            errors.append(f"node {n['id']} is {n['status']} without passing verification evidence")
        if n["status"] == "COMPLETE":
            for f in n.get("features", []):
                if f in features and features[f].get("status") not in ("COMPLETE", "DROPPED"):
                    errors.append(f"node {n['id']} is COMPLETE but feature {f} is {features[f].get('status')}")

    # 7. gate integrity
    if gate is not None:
        for c in gate["checks"]:
            if c["status"] in ("PASS", "WARNING") and not c.get("evidence"):
                errors.append(f"gate {c['id']} is {c['status']} without evidence")
            for e in c.get("evidence", []):
                if e not in ev_ids:
                    errors.append(f"gate {c['id']}: unknown evidence {e}")
        sc = gatelib.score(gate["checks"])
        claimed = (state.get("production") or {}).get("readiness")
        if claimed and claimed != sc["readiness"] and claimed != "UNVERIFIED":
            errors.append(f"state.production.readiness is {claimed} but gate evidence says {sc['readiness']}")

    # 8. blueprint completeness claim
    if (state.get("blueprint") or {}).get("status") == "COMPLETE":
        for g in blueprint_gaps(project):
            errors.append(f"blueprint marked COMPLETE but: {g}")

    # 9. document language (rule 17) and placeholders (quality rules)
    for p in sorted(project.forge.rglob("*.md")):
        rel = p.relative_to(project.forge)
        text = read_text(p)
        for m in CERT_CLAIM_RE.finditer(text):
            before = text[max(0, m.start() - 60): m.start()]
            if not NEGATION_RE.search(before):
                warnings.append(f"{rel}: possible certification/compliance claim '{m.group(0)}' (rule 17)")
        if rel.parts[0] not in ("prompts",):
            ph = PLACEHOLDER_RE.findall(text)
            if ph:
                warnings.append(f"{rel}: {len(ph)} unresolved placeholder(s) e.g. {ph[0]!r}")

    return {"ok": not errors, "errors": errors, "warnings": warnings}


def gate_has(gate: dict | None, cid: str) -> bool:
    return bool(gate) and any(c["id"] == cid for c in gate["checks"])
