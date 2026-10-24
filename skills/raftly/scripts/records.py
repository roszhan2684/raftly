#!/usr/bin/env python3
"""Create and update Raftly records with deterministic IDs.

Registry records (YAML):
  add requirement  --statement S --priority MUST [--rationale R] [--features F001,F002] [--source S]
  add assumption   --statement S --confidence 40 --impact-if-false T --validation V [--impact high] [--gate G]
  add risk         --category security --statement S --probability medium --impact high --mitigation M --owner security [--trigger T]
  add dependency   --name N --purpose P --license MIT [--version V] [--kind library] [--chosen-by ADR-002] [--lock-in LOW]
  add experiment   --hypothesis H --success S --failure F --window W --on-success A --on-failure B [--metric M]
  update <ID> KEY=VALUE...                 update fields of any registry record (schema-validated)

Markdown records (frontmatter + body from templates/records):
  new feature     --name N [--priority MUST] [--node N001] [--requirements REQ-001] [--owner product-director]
  new debt        --title T --type intentional_shortcut --risk medium --owner backend [--introduced-by X] [--fix-trigger T]
  new prompt      --title T --node N001 [--role "Staff Frontend Engineer"]   (also links the prompt to the node)
  new postmortem  --title T --severity SEV2
  feature-status <F001> <STATUS>          feature status change with evidence/DoD rules

Requirement Change Engine:
  change-requirement <REQ-ID> --statement S [--priority MUST] --reason R
      records the new requirement, supersedes the old one (history preserved), computes the impact
      across product/UX/architecture/data/API/security/billing/testing/ops/legal/docs, marks affected
      documents STALE and reports the follow-up work.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from forgelib import cli, docs, model  # noqa: E402
from forgelib import evidence as ev  # noqa: E402
from forgelib.fsutil import SKILL_ROOT, read_text, slugify  # noqa: E402
from forgelib.project import ForgeError, now_iso, parse_frontmatter, today  # noqa: E402

TEMPLATES = SKILL_ROOT / "templates" / "records"
REGISTRY_FOR = {
    "requirement": ("requirements.yaml", "REQ-"),
    "assumption": ("assumptions.yaml", "A-"),
    "risk": ("risks.yaml", "R-"),
    "experiment": ("experiments.yaml", "EXP-"),
}


class _Keep(dict):
    def __missing__(self, key):
        return "{" + key + "}"


def render_template(template: str, **values) -> str:
    return read_text(TEMPLATES / f"{template}.md").format_map(_Keep({k: ("" if v is None else v) for k, v in values.items()}))


def severity(prob: str, impact: str) -> str:
    score = {"low": 1, "medium": 2, "high": 3}
    s = score[prob] * score[impact]
    return "critical" if s >= 9 else "high" if s >= 6 else "medium" if s >= 3 else "low"


def registry_file_for_id(rid: str) -> str:
    for kind, (filename, prefix) in REGISTRY_FOR.items():
        if rid.startswith(prefix) and model.kind_of_id(rid) == kind:
            return filename
    raise ForgeError(f"{rid} is not a registry record id (REQ-/A-/R-/EXP-)")


def add_registry(proj, kind: str, args) -> dict:
    filename = REGISTRY_FOR[kind][0] if kind != "dependency" else "dependencies.yaml"
    items = proj.registry(filename)
    if kind == "requirement":
        rec = {"id": proj.next_id("requirement"), "statement": args.statement, "priority": args.priority,
               "status": "ACTIVE", "features": cli.split_csv(args.features), "decisions": [],
               "supersedes": [], "superseded_by": None, "created_at": today()}
        if args.rationale:
            rec["rationale"] = args.rationale
        if args.source:
            rec["source"] = args.source
    elif kind == "assumption":
        rec = {"id": proj.next_id("assumption"), "statement": args.statement, "confidence": args.confidence,
               "impact_if_false": args.impact_if_false, "impact": args.impact, "validation_method": args.validation,
               "state": "UNTESTED", "updated_at": today()}
        if args.evidence:
            rec["evidence"] = args.evidence
        if args.gate:
            rec["validation_gate"] = args.gate
    elif kind == "risk":
        rec = {"id": proj.next_id("risk"), "category": args.category, "statement": args.statement,
               "probability": args.probability, "impact": args.impact,
               "severity": severity(args.probability, args.impact), "mitigation": args.mitigation,
               "owner_role": args.owner, "status": "OPEN", "updated_at": today()}
        if args.trigger:
            rec["trigger"] = args.trigger
    elif kind == "dependency":
        if any(d["name"] == args.name for d in items):
            raise ForgeError(f"dependency {args.name} already recorded; use 'update' semantics by editing dependencies.yaml")
        rec = {"name": args.name, "version": args.version, "purpose": args.purpose, "license": args.license,
               "kind": args.kind, "chosen_by": cli.split_csv(args.chosen_by), "status": args.status,
               "lock_in": args.lock_in, "last_review": today()}
        if args.source:
            rec["source"] = args.source
    elif kind == "experiment":
        rec = {"id": proj.next_id("experiment"), "hypothesis": args.hypothesis, "success_threshold": args.success,
               "failure_threshold": args.failure, "window": args.window, "on_success": args.on_success,
               "on_failure": args.on_failure, "status": "PLANNED"}
        if args.metric:
            rec["metric"] = args.metric
    else:
        raise ForgeError(kind)
    items.append(rec)
    proj.save_registry(filename, items)
    return rec


def change_requirement(proj, old_id: str, statement: str, priority: str | None, reason: str) -> dict:
    reqs = proj.registry("requirements.yaml")
    old = next((r for r in reqs if r["id"] == old_id), None)
    if old is None:
        raise ForgeError(f"unknown requirement {old_id}")
    if old["status"] != "ACTIVE":
        raise ForgeError(f"{old_id} is {old['status']}; change the requirement that superseded it instead")
    new_id = proj.next_id("requirement")
    new = {"id": new_id, "statement": statement, "priority": priority or old["priority"], "status": "ACTIVE",
           "rationale": reason, "features": list(old.get("features") or []), "decisions": list(old.get("decisions") or []),
           "supersedes": [old_id], "superseded_by": None, "created_at": today()}
    old["status"] = "SUPERSEDED"
    old["superseded_by"] = new_id
    old["changed_at"] = today()
    reqs.append(new)
    proj.save_registry("requirements.yaml", reqs)

    # impact
    features = {fm["id"]: (p, fm) for p, fm, _ in proj.records("feature")}
    affected_features = sorted(set(old.get("features") or []) | {
        fid for fid, (_, fm) in features.items() if old_id in (fm.get("requirements") or [])})
    decisions = {fm["id"]: fm for _, fm, _ in proj.records("decision")}
    affected_decisions = sorted(set(old.get("decisions") or []) | {
        did for did, fm in decisions.items() if old_id in (fm.get("affects") or [])} | {
        d for fid in affected_features for d in (features[fid][1].get("decisions") or [])})
    nodes = proj.registry("build-graph.yaml")
    affected_nodes = sorted({n["id"] for n in nodes if set(n.get("features", [])) & set(affected_features)})
    downstream = ev.impact(proj.evidence(), old_id)
    for fid in affected_features:
        downstream += ev.impact(proj.evidence(), fid)
    downstream = sorted(set(downstream))
    risks = [r["id"] for r in proj.registry("risks.yaml") if set(r.get("related") or []) & ({old_id} | set(affected_features))]
    assumptions = [a["id"] for a in proj.registry("assumptions.yaml") if set(a.get("related") or []) & ({old_id} | set(affected_features))]

    # link new requirement into the features' frontmatter and evidence
    for fid in affected_features:
        p, fm = features[fid]
        fm_full, body = parse_frontmatter(read_text(p))
        reqs_list = [r for r in (fm_full.get("requirements") or []) if r != old_id]
        if new_id not in reqs_list:
            reqs_list.append(new_id)
        fm_full["requirements"] = reqs_list
        proj.update_record(p, fm_full, body, "feature")
    data = proj.evidence()
    data["links"].append({"from": new_id, "to": old_id, "relation": "supersedes", "note": reason, "at": now_iso()})
    proj.save_evidence(data)

    entities = {e["id"] for e in proj.evidence()["entities"]}
    by_prefix = lambda pre: sorted(x for x in downstream if x.startswith(pre))  # noqa: E731
    stale = ["PRODUCT.md", "BUILD.md", "EXECUTIVE.md"]
    if affected_decisions:
        stale += ["ARCHITECTURE.md", "DECISIONS.md"]
    if by_prefix("SCR-") or by_prefix("CMP-"):
        stale.append("DESIGN.md")
    if by_prefix("TBL-"):
        stale.append("DATA_MODEL.md")
    st = proj.state()
    for d in stale:
        if (proj.forge / d).exists():
            st.setdefault("documents", {})[d] = {"status": "STALE", "updated_at": now_iso(),
                                                 "reason": f"{old_id} superseded by {new_id}"}
    proj.save_state(st, event=f"Requirement change: {old_id} superseded by {new_id} ({reason})")
    report = {
        "new_requirement": new_id,
        "superseded": old_id,
        "impact": {
            "product": {"features": affected_features, "assumptions": assumptions},
            "ux": by_prefix("SCR-") + by_prefix("CMP-"),
            "architecture": affected_decisions,
            "data": by_prefix("TBL-"),
            "api": by_prefix("API-") + by_prefix("SVC-") + by_prefix("JOB-"),
            "security_privacy": [r for r in risks],
            "testing": by_prefix("TEST-"),
            "ops_metrics": by_prefix("MET-"),
            "integrations_billing": by_prefix("INT-"),
            "build_graph_nodes": affected_nodes,
            "documents_marked_stale": [d for d in stale if (proj.forge / d).exists()],
        },
        "assess_manually": [
            "legal/compliance implications (pricing, terms, data processing)",
            "migration and rollback needs for existing data/customers",
            "billing changes and customer communication",
            "new acceptance criteria and tests for " + (", ".join(affected_features) or "new features"),
        ],
        "next_steps": [
            f"Update feature specs {', '.join(affected_features) or '(none mapped)'} to satisfy {new_id}",
            "Create ADRs for any decision that must change (decisions.py new / supersede)",
            "Add build-graph nodes and prompts for new work; re-render BUILD.md",
            "Regenerate stale documents, then state.py doc <FILE> CURRENT",
        ],
        "known_entities_checked": len(entities),
    }
    return report


def main(argv: list[str]) -> int:
    p = cli.parser("records.py", "Create/update Raftly records")
    sub = p.add_subparsers(dest="cmd", required=True)
    add = sub.add_parser("add")
    addsub = add.add_subparsers(dest="record_type", required=True)
    rq = addsub.add_parser("requirement")
    rq.add_argument("--statement", required=True)
    rq.add_argument("--priority", default="MUST", choices=model.REQUIREMENT_PRIORITIES)
    rq.add_argument("--rationale", default=None)
    rq.add_argument("--features", default="")
    rq.add_argument("--source", default=None)
    asn = addsub.add_parser("assumption")
    asn.add_argument("--statement", required=True)
    asn.add_argument("--confidence", type=int, required=True)
    asn.add_argument("--impact-if-false", required=True)
    asn.add_argument("--impact", default="medium", choices=model.LEVELS)
    asn.add_argument("--validation", required=True)
    asn.add_argument("--evidence", default=None)
    asn.add_argument("--gate", default=None)
    rk = addsub.add_parser("risk")
    rk.add_argument("--category", required=True, choices=model.RISK_CATEGORIES)
    rk.add_argument("--statement", required=True)
    rk.add_argument("--probability", required=True, choices=model.LEVELS)
    rk.add_argument("--impact", required=True, choices=model.LEVELS)
    rk.add_argument("--mitigation", required=True)
    rk.add_argument("--owner", required=True)
    rk.add_argument("--trigger", default=None)
    dp = addsub.add_parser("dependency")
    dp.add_argument("--name", required=True)
    dp.add_argument("--purpose", required=True)
    dp.add_argument("--license", required=True)
    dp.add_argument("--version", default=None)
    dp.add_argument("--kind", default="library", choices=["library", "service", "tool", "framework", "runtime", "dataset", "model"])
    dp.add_argument("--chosen-by", default="")
    dp.add_argument("--status", default="PROPOSED", choices=model.DEPENDENCY_STATUSES)
    dp.add_argument("--lock-in", default="LOW", choices=["LOW", "MEDIUM", "HIGH"])
    dp.add_argument("--source", default=None)
    ex = addsub.add_parser("experiment")
    ex.add_argument("--hypothesis", required=True)
    ex.add_argument("--success", required=True)
    ex.add_argument("--failure", required=True)
    ex.add_argument("--window", required=True)
    ex.add_argument("--on-success", required=True)
    ex.add_argument("--on-failure", required=True)
    ex.add_argument("--metric", default=None)
    up = sub.add_parser("update")
    up.add_argument("id")
    up.add_argument("pairs", nargs="+")
    new = sub.add_parser("new")
    newsub = new.add_subparsers(dest="record_type", required=True)
    nf = newsub.add_parser("feature")
    nf.add_argument("--name", required=True)
    nf.add_argument("--priority", default="MUST", choices=model.REQUIREMENT_PRIORITIES)
    nf.add_argument("--node", default=None)
    nf.add_argument("--requirements", default="")
    nf.add_argument("--owner", default="product-director")
    nd = newsub.add_parser("debt")
    nd.add_argument("--title", required=True)
    nd.add_argument("--type", required=True, choices=model.DEBT_TYPES)
    nd.add_argument("--risk", required=True, choices=model.LEVELS)
    nd.add_argument("--owner", required=True)
    nd.add_argument("--introduced-by", default="")
    nd.add_argument("--fix-trigger", default="")
    npr = newsub.add_parser("prompt")
    npr.add_argument("--title", required=True)
    npr.add_argument("--node", required=True)
    npr.add_argument("--role", default="Staff Software Engineer")
    npm = newsub.add_parser("postmortem")
    npm.add_argument("--title", required=True)
    npm.add_argument("--severity", required=True, choices=["SEV1", "SEV2", "SEV3", "SEV4"])
    fs = sub.add_parser("feature-status")
    fs.add_argument("id")
    fs.add_argument("status", choices=model.WORK_STATUSES)
    cr = sub.add_parser("change-requirement")
    cr.add_argument("id")
    cr.add_argument("--statement", required=True)
    cr.add_argument("--priority", default=None, choices=model.REQUIREMENT_PRIORITIES)
    cr.add_argument("--reason", required=True)
    args = p.parse_args(argv)
    proj = cli.project(args).require()

    if args.cmd == "add":
        rec = add_registry(proj, args.record_type, args)
        cli.emit(args, rec, lambda d: f"Added {args.record_type} {d.get('id', d.get('name'))}")
        return 0
    if args.cmd == "update":
        filename = registry_file_for_id(args.id)
        items = proj.registry(filename)
        rec = next((r for r in items if r.get("id") == args.id), None)
        if rec is None:
            raise ForgeError(f"{args.id} not found in {filename}")
        changes = cli.parse_kv(args.pairs)
        if "id" in changes:
            raise ForgeError("ids are immutable")
        rec.update(changes)
        if filename == "risks.yaml" and ({"probability", "impact"} & set(changes)):
            rec["severity"] = severity(rec["probability"], rec["impact"])
        if "updated_at" in rec or filename in ("assumptions.yaml", "risks.yaml"):
            rec["updated_at"] = today()
        proj.save_registry(filename, items)
        cli.emit(args, rec, lambda d: f"Updated {args.id}")
        return 0
    if args.cmd == "new":
        if args.record_type == "feature":
            fid = proj.next_id("feature")
            fm = {"id": fid, "name": args.name, "status": "PLANNED", "priority": args.priority,
                  "owner_role": args.owner, "node": args.node, "requirements": cli.split_csv(args.requirements),
                  "decisions": [], "depends_on": [], "screens": [], "evidence_status": "NONE", "updated_at": today()}
            path = proj.write_record("feature", fm, render_template("feature", id=fid, name=args.name),
                                     filename=f"{fid}-{slugify(args.name)}.md")
            if fm["requirements"]:
                reqs = proj.registry("requirements.yaml")
                for r in reqs:
                    if r["id"] in fm["requirements"] and fid not in (r.get("features") or []):
                        r.setdefault("features", []).append(fid)
                proj.save_registry("requirements.yaml", reqs)
            if args.node:
                nodes = proj.registry("build-graph.yaml")
                for n in nodes:
                    if n["id"] == args.node and fid not in n.get("features", []):
                        n.setdefault("features", []).append(fid)
                proj.save_registry("build-graph.yaml", nodes)
        elif args.record_type == "debt":
            did = proj.next_id("debt")
            fm = {"id": did, "title": args.title, "type": args.type, "risk": args.risk, "status": "OPEN",
                  "owner_role": args.owner, "introduced_by": args.introduced_by, "fix_trigger": args.fix_trigger,
                  "affects": [], "created_at": today()}
            path = proj.write_record("debt", fm, render_template("debt", **fm))
        elif args.record_type == "postmortem":
            pid = proj.next_id("postmortem")
            fm = {"id": pid, "title": args.title, "severity": args.severity, "status": "DRAFT", "date": today(),
                  "affects": [], "learning": None}
            path = proj.write_record("postmortem", fm, render_template("postmortem", **fm))
        elif args.record_type == "prompt":
            nodes = proj.registry("build-graph.yaml")
            node = next((n for n in nodes if n["id"] == args.node), None)
            if node is None:
                raise ForgeError(f"unknown node {args.node}")
            number = len(proj.prompts()) + 1
            name = f"{number:03d}-{slugify(args.title)}.md"
            body = render_template("prompt", number=f"{number:03d}", title=args.title, node=args.node,
                                   features=", ".join(node.get("features", [])) or "—", role=args.role)
            path = proj.write_text(f"prompts/{name}", body)
            node.setdefault("prompts", []).append(name)
            proj.save_registry("build-graph.yaml", nodes)
        cli.emit(args, {"path": str(path)}, lambda d: f"Created {d['path']}")
        return 0
    if args.cmd == "feature-status":
        path, fm, body = proj.find_record("feature", args.id)
        verified = ev.verified_subjects(proj.evidence())
        problem = model.work_transition_problem(fm["status"], args.status, has_verification=args.id in verified,
                                                has_blockers=True)  # feature blockers live on the build-graph node
        if problem:
            raise ForgeError(f"{args.id}: {problem}")
        if args.status == "COMPLETE":
            items = docs.checklist(docs.find_section(body, "Definition of Done") or "")
            open_items = [i for s, i in items if s == "open"]
            if not items or open_items:
                raise ForgeError(f"{args.id}: Definition of Done incomplete ({len(open_items)} open item(s))")
        old = fm["status"]
        fm["status"] = args.status
        fm["evidence_status"] = "SUFFICIENT" if args.id in verified else ("PARTIAL" if args.status in (
            "IMPLEMENTED_UNVERIFIED", "PARTIAL") else fm.get("evidence_status", "NONE"))
        fm["updated_at"] = today()
        proj.update_record(path, fm, body, "feature")
        proj.save_state(proj.state(), event=f"{args.id} {old} -> {args.status}")
        cli.emit(args, fm, lambda d: f"{d['id']} -> {d['status']}")
        return 0
    if args.cmd == "change-requirement":
        report = change_requirement(proj, args.id, args.statement, args.priority, args.reason)

        def text(r):
            lines = [f"{r['superseded']} superseded by {r['new_requirement']} (history preserved).", "Impact:"]
            for k, v in r["impact"].items():
                if isinstance(v, dict):
                    v = [f"{kk}: {', '.join(vv) or '—'}" for kk, vv in v.items()]
                lines.append(f"  {k}: {', '.join(v) if v else '— (none recorded)'}")
            lines.append("Assess manually: " + "; ".join(r["assess_manually"]))
            lines.append("Next: " + "; ".join(r["next_steps"]))
            return "\n".join(lines)
        cli.emit(args, report, text)
        return 0
    return 0


if __name__ == "__main__":
    cli.run(main)
