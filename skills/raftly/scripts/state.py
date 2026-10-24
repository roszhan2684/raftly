#!/usr/bin/env python3
"""Read and update Raftly project state with validated transitions and atomic writes.

Commands:
  show                         summary of mode, stage, blueprint, progress, readiness
  get <dotted.path>            print one value (e.g. project.mode)
  set <dotted.path> <value>    set a value (YAML-parsed); schema-validated on save
  mode <MODE> [--reason R]     change operating mode
  stage <STAGE> [--override-reason R]
                               change lifecycle stage. BLUEPRINT_COMPLETE requires the
                               Blueprint Completion Gate; LAUNCHED requires gate readiness
                               (READY / READY_WITH_WARNINGS) unless a founder override reason
                               is given, which is recorded in history.
  blueprint <section> <status> set a blueprint section (product/design/...); 'status' sets overall
  doc <FILE.md> <status> [--reason R]   register a document as CURRENT/STALE/DRAFT/NOT_APPLICABLE
  profile KEY=VALUE...         update the product profile (drives gate applicability)
  event <text>                 append a history event (used by /raftly replay)
  recount                      recompute counts from registries
  founder-decision add|resolve <text>
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from forgelib import cli, graph, model, yamlio  # noqa: E402
from forgelib import gate as gatelib  # noqa: E402
from forgelib.checks import blueprint_gaps  # noqa: E402
from forgelib.project import ForgeError, now_iso, recount  # noqa: E402


def summary(proj) -> dict:
    st = proj.state()
    nodes = proj.registry("build-graph.yaml")
    try:
        nxt = [n["id"] for n in graph.unblocked(nodes)][:5] if nodes and not graph.problems(nodes) else []
    except ValueError:
        nxt = []
    gate = proj.gate()
    sc = gatelib.score(gate["checks"]) if gate else None
    stale = [d for d, m in (st.get("documents") or {}).items() if m.get("status") == "STALE"]
    return {
        "name": st["project"]["name"],
        "mode": st["project"]["mode"],
        "stage": st["project"]["stage"],
        "product_type": st["project"].get("product_type"),
        "forge_version": st["engine"]["version"],
        "schema_version": st["engine"]["schema_version"],
        "blueprint": {k: v for k, v in st["blueprint"].items()},
        "progress": graph.progress(nodes) if nodes else None,
        "next_nodes": nxt,
        "readiness": sc["readiness"] if sc else st["production"].get("readiness", "UNVERIFIED"),
        "gate_coverage": sc["coverage"] if sc else None,
        "counts": st.get("counts", {}),
        "stale_documents": stale,
        "open_founder_decisions": st["blueprint"].get("open_founder_decisions", []),
        "last_events": (st.get("history") or [])[-5:],
    }


def text_summary(s: dict) -> str:
    bp = s["blueprint"]
    lines = [
        f"{s['name']} — {s['mode']} · stage {s['stage']} · Raftly {s['forge_version']} (schema v{s['schema_version']})",
        "Blueprint: " + ", ".join(f"{k}={bp.get(k)}" for k in ["status", *model.BLUEPRINT_SECTIONS]),
    ]
    if s["progress"]:
        p = s["progress"]
        lines.append(f"Build: {p['total']} nodes, {p['complete_pct']}% complete, {p['verified_pct']}% verified")
    lines.append(f"Next unblocked: {', '.join(s['next_nodes']) or '—'}")
    cov = f" (evidence coverage {round(s['gate_coverage'] * 100)}%)" if s["gate_coverage"] is not None else ""
    lines.append(f"Production readiness: {s['readiness']}{cov}")
    if s["open_founder_decisions"]:
        lines.append("Open founder decisions: " + "; ".join(s["open_founder_decisions"]))
    if s["stale_documents"]:
        lines.append("Stale documents: " + ", ".join(s["stale_documents"]))
    return "\n".join(lines)


def set_dotted(data: dict, dotted: str, value) -> None:
    parts = dotted.split(".")
    cur = data
    for part in parts[:-1]:
        if part not in cur or not isinstance(cur[part], dict):
            cur[part] = {}
        cur = cur[part]
    cur[parts[-1]] = value


def get_dotted(data: dict, dotted: str):
    cur = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            raise ForgeError(f"no such field: {dotted}")
        cur = cur[part]
    return cur


def main(argv: list[str]) -> int:
    p = cli.parser("state.py", "Read/update .raftly/state.yaml")
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("show")
    g = sub.add_parser("get")
    g.add_argument("path")
    s = sub.add_parser("set")
    s.add_argument("path")
    s.add_argument("value")
    m = sub.add_parser("mode")
    m.add_argument("mode", choices=model.MODES)
    m.add_argument("--reason", default="")
    stg = sub.add_parser("stage")
    stg.add_argument("stage", choices=model.STAGES)
    stg.add_argument("--override-reason", default=None)
    b = sub.add_parser("blueprint")
    b.add_argument("section", choices=["status", *model.BLUEPRINT_SECTIONS])
    b.add_argument("status")
    d = sub.add_parser("doc")
    d.add_argument("name")
    d.add_argument("status", choices=["CURRENT", "STALE", "DRAFT", "NOT_APPLICABLE"])
    d.add_argument("--reason", default=None)
    pr = sub.add_parser("profile")
    pr.add_argument("pairs", nargs="+")
    e = sub.add_parser("event")
    e.add_argument("text")
    sub.add_parser("recount")
    fd = sub.add_parser("founder-decision")
    fd.add_argument("action", choices=["add", "resolve"])
    fd.add_argument("text")
    args = p.parse_args(argv)
    proj = cli.project(args).require()
    cmd = args.cmd or "show"

    if cmd == "show":
        cli.emit(args, summary(proj), text_summary)
        return 0
    st = proj.state()
    if cmd == "get":
        val = get_dotted(st, args.path)
        cli.emit(args, val, lambda v: yamlio.dumps(v).rstrip() if isinstance(v, (dict, list)) else str(v))
        return 0
    if cmd == "set":
        if args.path.startswith(("forge.", "history")) or args.path in ("project.stage", "project.mode", "blueprint.status"):
            raise ForgeError(f"'{args.path}' is managed; use the dedicated command (stage/mode/blueprint) or migrate_schema.py")
        set_dotted(st, args.path, yamlio.loads(args.value))
        proj.save_state(st)
    elif cmd == "mode":
        old = st["project"]["mode"]
        st["project"]["mode"] = args.mode
        proj.save_state(st, event=f"Mode {old} -> {args.mode}" + (f": {args.reason}" if args.reason else ""))
    elif cmd == "stage":
        cur = st["project"]["stage"]
        problem = model.stage_transition_problem(cur, args.stage)
        if problem:
            raise ForgeError(problem)
        note = ""
        if args.stage == "BLUEPRINT_COMPLETE":
            gaps = blueprint_gaps(proj)
            if gaps:
                raise ForgeError("Blueprint Completion Gate not met:\n  - " + "\n  - ".join(gaps))
            st["blueprint"]["status"] = "COMPLETE"
            st["blueprint"]["completed_at"] = now_iso()
        if args.stage == "LAUNCHED":
            gate = proj.gate()
            readiness = gatelib.score(gate["checks"])["readiness"] if gate else "UNVERIFIED"
            if readiness not in ("READY", "READY_WITH_WARNINGS"):
                if not args.override_reason:
                    raise ForgeError(
                        f"production readiness is {readiness}. Fix blockers, or record a founder override with "
                        "--override-reason (it is written to history and must also be captured as an ADR)."
                    )
                note = f" (FOUNDER OVERRIDE at readiness {readiness}: {args.override_reason})"
        st["project"]["stage"] = args.stage
        proj.save_state(st, event=f"Stage {cur} -> {args.stage}{note}")
    elif cmd == "blueprint":
        allowed = model.BLUEPRINT_STATUSES if args.section == "status" else model.BLUEPRINT_SECTION_STATUSES
        if args.status not in allowed:
            raise ForgeError(f"{args.section} must be one of {allowed}")
        if args.section == "status" and args.status == "COMPLETE":
            gaps = blueprint_gaps(proj)
            if gaps:
                raise ForgeError("Blueprint Completion Gate not met:\n  - " + "\n  - ".join(gaps))
            st["blueprint"]["completed_at"] = now_iso()
        st["blueprint"][args.section] = args.status
        if args.section != "status" and st["blueprint"]["status"] == "NOT_STARTED":
            st["blueprint"]["status"] = "IN_PROGRESS"
        proj.save_state(st, event=f"Blueprint {args.section} -> {args.status}")
    elif cmd == "doc":
        if args.status != "NOT_APPLICABLE" and not (proj.forge / args.name).exists():
            raise ForgeError(f".raftly/{args.name} does not exist")
        entry = {"status": args.status, "updated_at": now_iso()}
        if args.reason:
            entry["reason"] = args.reason
        st.setdefault("documents", {})[args.name] = entry
        proj.save_state(st)
    elif cmd == "profile":
        prof = st["project"].setdefault("profile", {})
        prof.update(cli.parse_kv(args.pairs))
        proj.save_state(st, event="Profile updated: " + ", ".join(args.pairs))
        if proj.gate() is not None:
            print("note: profile changed; run gate.py init to refresh applicable checks", file=sys.stderr)
    elif cmd == "event":
        proj.save_state(st, event=args.text)
    elif cmd == "recount":
        recount(proj, st)
        proj.save_state(st)
    elif cmd == "founder-decision":
        lst = st["blueprint"].setdefault("open_founder_decisions", [])
        if args.action == "add":
            if args.text not in lst:
                lst.append(args.text)
            proj.save_state(st, event=f"Founder decision required: {args.text}")
        else:
            if args.text not in lst:
                raise ForgeError(f"not an open founder decision: {args.text}")
            lst.remove(args.text)
            proj.save_state(st, event=f"Founder decision resolved: {args.text}")
    cli.emit(args, summary(proj), text_summary)
    return 0


if __name__ == "__main__":
    cli.run(main)
