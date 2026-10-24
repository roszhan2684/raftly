#!/usr/bin/env python3
"""Raftly single entry point used by the /raftly skill.

  engine.py context [--root DIR] [--json]   first call on every /raftly invocation: repo inspection +
                                           Raftly state + validation + next action, compact
  engine.py doctor  [--root DIR] [--json]   deterministic health report (no changes made)
  engine.py <command> [args...]             dispatch to a script:
      init       -> init_project.py        inspect  -> inspect_repo.py
      state      -> state.py               validate -> validate_project.py
      graph      -> build_graph.py         evidence -> evidence.py
      records    -> records.py             decisions-> decisions.py
      gate       -> gate.py                learning -> learning.py
      blueprint  -> render_blueprint.py    deck     -> render_deck.py
      handoff    -> generate_handoff.py    migrate  -> migrate_schema.py
      import, export -> bundle.py      (project as one zip, for hosts without a repository)
  engine.py version
"""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from forgelib import FORGE_VERSION, SCHEMA_VERSION, cli, graph  # noqa: E402
from forgelib.brand import brand  # noqa: E402
from forgelib import evidence as ev  # noqa: E402
from forgelib import gate as gatelib  # noqa: E402
from forgelib.checks import blueprint_gaps, validate  # noqa: E402
from forgelib.project import ForgeError, Project  # noqa: E402

COMMANDS = {
    "init": "init_project", "inspect": "inspect_repo", "state": "state", "validate": "validate_project",
    "graph": "build_graph", "evidence": "evidence", "records": "records", "decisions": "decisions", "gate": "gate",
    "learning": "learning", "blueprint": "render_blueprint", "deck": "render_deck", "handoff": "generate_handoff",
    "migrate": "migrate_schema", "export": "bundle", "import": "bundle",
}


PROJECT_MARKERS = (".git", "package.json", "pyproject.toml", "go.mod", "Cargo.toml", "pom.xml", "Gemfile",
                   "composer.json", "pubspec.yaml", ".raftly", ".forge")
GENERAL_FOLDERS = {"Desktop", "Documents", "Downloads", "Projects", "projects", "Developer", "dev", "code", "src",
                   "repos", "workspace", "Workspace", "GitHub", "git"}


def location_hint(root: Path) -> str | None:
    """Why this folder is not a project folder, or None if it may be one."""
    root = root.resolve()
    if any((root / m).exists() for m in PROJECT_MARKERS):
        return None
    home = Path.home().resolve()
    if root == home:
        return "your home folder"
    if root == Path(root.anchor):
        return "the filesystem root"
    if root.parent == home and root.name in GENERAL_FOLDERS:
        return f"your {root.name} folder"
    try:
        children = [c for c in root.iterdir() if c.is_dir() and not c.name.startswith(".")]
    except OSError:
        return None
    projects = [c for c in children[:200] if any((c / m).exists() for m in PROJECT_MARKERS)]
    if len(projects) >= 2:
        return f"a folder holding {len(projects)} separate projects"
    return None


def recommend(ctx: dict) -> str:
    f = ctx["state"]
    if not f["present"] and ctx["repo"].get("not_a_project"):
        return (f"This is {ctx['repo']['not_a_project']}, not a project folder. Don't write here: create a new folder "
                "named after the product (e.g. ./my-product) and run `init --root <folder>`; its documents go in "
                "<folder>/docs/ and its state in <folder>/.raftly/.")
    if not f["present"]:
        mode = ctx["repo"]["suggested_mode"]
        if mode == "GREENFIELD":
            return "No Raftly project. Treat as GREENFIELD: capture the idea, classify the product, then init_project.py."
        return ("Existing code without Raftly state. Do NOT rewrite. Inspect, infer the product and architecture, "
                "initialise in REVIEW/RECOVERY (stage ASSESSMENT) without changing code, and summarise findings.")
    if f.get("needs_migration"):
        return "Schema is older than this Raftly: run migrate_schema.py --dry-run, then migrate."
    if f.get("validation_errors"):
        return "Raftly state has integrity errors: fix them (validate_project.py) before planning or building."
    st = f["stage"]
    if f["blueprint_status"] != "COMPLETE":
        gaps = f.get("blueprint_gaps", [])
        return "Continue the blueprint. Next gaps: " + "; ".join(gaps[:4]) if gaps else "Blueprint gate passes: mark BLUEPRINT_COMPLETE and generate deliverables."
    if f.get("all_done"):
        return "All build nodes are done. Run the production gate (/raftly launch)."
    if f.get("next"):
        n = f["next"]
        return f"{n['action'].upper()} {n['id']} {n['name']} using {', '.join(Path(p).name for p in n['prompts']) or 'a new prompt'}."
    if st in ("LAUNCHED", "OPERATING"):
        return "Operating: ask for feedback, metrics or incidents to process (OPERATE mode)."
    return "No unblocked work: resolve blockers or verify IMPLEMENTED_UNVERIFIED nodes."


def context(root: str | None) -> dict:
    import inspect_repo

    proj = Project(root)
    hint = None if proj.exists else location_hint(proj.root)
    # a home or workspace folder can be huge: don't walk it
    repo = inspect_repo.inspect(proj.root, 300 if hint else 20000)
    out = {"forge_version": FORGE_VERSION, "repo": {k: repo[k] for k in (
        "root", "file_count", "code_files", "is_empty", "docs_only", "languages", "frameworks", "data", "services",
        "tests", "ci", "infra", "migrations", "boundaries", "signals", "suggested_mode")}, "state": {"present": False}}
    if hint:
        out["repo"]["not_a_project"] = hint
    if proj.exists:
        f = {"present": True}
        try:
            raw = proj.load_yaml("state.yaml") or {}
            meta = raw.get("engine") or {}
            sv = meta.get("schema_version", 0) if meta else 0
            if proj.legacy_dir is not None or "forge" in raw:
                f["needs_migration"] = True  # legacy state folder or legacy "forge" key
                f["legacy_dir"] = proj.legacy_dir.name if proj.legacy_dir else None
            f["schema_version"] = sv
            if sv < SCHEMA_VERSION:
                f["needs_migration"] = True
            if f.get("needs_migration"):
                out["state"] = f
                out["recommendation"] = recommend(out)
                return out
            st = proj.state()
            f.update({"name": st["project"]["name"], "mode": st["project"]["mode"], "stage": st["project"]["stage"],
                      "documents_dir": str(proj.docs.relative_to(proj.root)),
                      "outputs_dir": str(proj.artifacts.relative_to(proj.root)),
                      "product_type": st["project"].get("product_type"), "profile": st["project"].get("profile", {}),
                      "blueprint_status": st["blueprint"]["status"],
                      "blueprint": {k: v for k, v in st["blueprint"].items() if k not in ("status", "completed_at")},
                      "documents": {k: v.get("status") for k, v in (st.get("documents") or {}).items()},
                      "counts": st.get("counts", {}), "recent_history": (st.get("history") or [])[-6:]})
            res = validate(proj)
            f["validation_errors"] = res["errors"][:15]
            f["validation_warnings"] = len(res["warnings"])
            if st["blueprint"]["status"] != "COMPLETE":
                f["blueprint_gaps"] = blueprint_gaps(proj)[:12]
            nodes = proj.registry("build-graph.yaml")
            if nodes and not graph.problems(nodes):
                ready = graph.unblocked(nodes)
                f["progress"] = graph.progress(nodes)
                f["all_done"] = all(n["status"] in ("COMPLETE", "DROPPED") for n in nodes)
                if ready:
                    n = ready[0]
                    f["next"] = {"id": n["id"], "name": n["name"], "status": n["status"],
                                 "action": "verify" if n["status"] == "IMPLEMENTED_UNVERIFIED" else "complete" if n["status"] == "VERIFIED" else (
                                     "continue" if n["status"] in ("IN_PROGRESS", "PARTIAL") else "start"),
                                 "prompts": [str(proj.path("prompts") / p) for p in n.get("prompts", [])]}
                f["blocked"] = [n["id"] for n in nodes if n["status"] == "BLOCKED"]
            gate = proj.gate()
            if gate:
                sc = gatelib.score(gate["checks"])
                f["readiness"] = {k: sc[k] for k in ("readiness", "coverage", "score", "blocker_failures", "blocker_unverified")}
            f["open_founder_decisions"] = st["blueprint"].get("open_founder_decisions", [])
        except ForgeError as exc:
            f["validation_errors"] = [str(exc)]
        out["state"] = f
    out["recommendation"] = recommend(out)
    return out


def context_text(c: dict) -> str:
    r, f = c["repo"], c["state"]
    lines = [f"{brand()['display_name']} {c['forge_version']} context", "",
             f"Repo: {r['root']} · {r['file_count']} files ({r['code_files']} code) · suggested mode {r['suggested_mode']}"]
    if r["languages"]:
        lines.append("Languages: " + ", ".join(f"{k} {v}" for k, v in list(r["languages"].items())[:6]))
    stack = r["frameworks"] + r["data"] + r["services"]
    if stack:
        lines.append("Stack: " + ", ".join(stack))
    if r["tests"] or r["ci"]:
        lines.append(f"Tests: {', '.join(r['tests']) or 'none'} · CI: {len(r['ci'])} workflow(s)")
    for s in r["signals"]:
        lines.append(f"Signal: {s}")
    if r.get("not_a_project"):
        lines.append(f"Location: {r['not_a_project']} (not a project folder)")
    lines.append("")
    if not f["present"]:
        lines.append("Raftly state: none (.raftly/ absent)")
    elif f.get("needs_migration"):
        lines.append(f"Raftly state: schema v{f['schema_version']} needs migration")
    else:
        lines.append(f"Raftly project: {f.get('name')} · {f.get('mode')} · stage {f.get('stage')} · blueprint {f.get('blueprint_status')}")
        lines.append(f"Documents: {f.get('documents_dir')}/ · outputs: {f.get('outputs_dir')}/")
        if f.get("blueprint"):
            lines.append("Blueprint sections: " + ", ".join(f"{k}={v}" for k, v in f["blueprint"].items() if k != "open_founder_decisions"))
        if f.get("progress"):
            p = f["progress"]
            lines.append(f"Build: {p['total']} nodes · {p['complete_pct']}% complete · {p['verified_pct']}% verified · blocked: {', '.join(f.get('blocked', [])) or 'none'}")
        if f.get("readiness"):
            rd = f["readiness"]
            lines.append(f"Readiness: {rd['readiness']} (coverage {rd['coverage']}, score {rd['score']})")
        if f.get("open_founder_decisions"):
            lines.append("Open founder decisions: " + "; ".join(f["open_founder_decisions"]))
        stale = [k for k, v in (f.get("documents") or {}).items() if v == "STALE"]
        if stale:
            lines.append("Stale documents: " + ", ".join(stale))
        for e in f.get("validation_errors") or []:
            lines.append(f"Integrity error: {e}")
        for h in f.get("recent_history") or []:
            lines.append(f"History {h['at'][:10]}: {h['event']}")
    lines += ["", f"Recommended next action: {c['recommendation']}"]
    return "\n".join(lines)


def doctor(root: str | None) -> dict:
    proj = Project(root).require()
    ctx = context(root)
    res = validate(proj)
    feats = {fm["id"]: fm for _, fm, _ in proj.records("feature")}
    data = proj.evidence()
    untested = ev.untested_requirements(proj.registry("requirements.yaml"), feats, data)
    profile = proj.state()["project"].get("profile") or {}
    ui_only = ev.ui_only_features(feats, data) if profile.get("backend") else []
    gate = proj.gate()
    sc = gatelib.score(gate["checks"]) if gate else None
    debt = [fm for _, fm, _ in proj.records("debt") if fm["status"] == "OPEN"]
    issues = []
    issues += [{"severity": "high", "area": "integrity", "issue": e} for e in res["errors"]]
    if sc and sc["blocker_failures"]:
        issues.append({"severity": "high", "area": "production", "issue": "failing launch blockers: " + ", ".join(sc["blocker_failures"])})
    if untested:
        issues.append({"severity": "medium", "area": "verification", "issue": "requirements without verification: " + ", ".join(untested)})
    if ui_only:
        issues.append({"severity": "medium", "area": "completeness", "issue": "UI-only features: " + ", ".join(ui_only)})
    for d in debt:
        if d["risk"] == "high":
            issues.append({"severity": "medium", "area": "debt", "issue": f"{d['id']} {d['title']}"})
    for s in ctx["repo"]["signals"]:
        issues.append({"severity": "low", "area": "repository", "issue": s})
    issues += [{"severity": "low", "area": "documents", "issue": w} for w in res["warnings"][:10]]
    return {"healthy": not any(i["severity"] == "high" for i in issues), "issues": issues,
            "readiness": sc["readiness"] if sc else "UNVERIFIED",
            "verdict": "No change recommended." if not issues else "Address the issues in severity order; do not create work beyond them."}


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd, rest = argv[0], argv[1:]
    if cmd == "version":
        print(json.dumps({"forge_version": FORGE_VERSION, "schema_version": SCHEMA_VERSION, "brand": brand()}))
        return 0
    if cmd in ("context", "doctor"):
        p = cli.parser(f"forge.py {cmd}", cmd)
        args = p.parse_args(rest)
        if cmd == "context":
            cli.emit(args, context(args.root), context_text)
        else:
            d = doctor(args.root)
            cli.emit(args, d, lambda x: "\n".join([f"Health: {'OK' if x['healthy'] else 'ATTENTION'} · readiness {x['readiness']}"]
                                                  + [f"[{i['severity']}] {i['area']}: {i['issue']}" for i in x["issues"]] + [x["verdict"]]))
        return 0
    if cmd not in COMMANDS:
        print(f"{brand()['skill_command']}: unknown command {cmd!r}. Run engine.py --help.", file=sys.stderr)
        return 2
    module = importlib.import_module(COMMANDS[cmd])
    if cmd in ("export", "import"):
        rest = [cmd] + rest
    return module.main(rest) or 0


if __name__ == "__main__":
    cli.run(main)
