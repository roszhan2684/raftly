#!/usr/bin/env python3
"""Production gate and Forgotten-20% audit: evidence-gated launch readiness.

Commands:
  raftly gate init                      instantiate checks for the project profile (re-run after profile
                                        changes; recorded statuses/evidence are preserved)
  raftly gate set <CHECK> <STATUS> [--evidence EV-001,EV-002] [--note N] [--na-reason "decision: ADR-004 ..."]
                                        PASS/WARNING require evidence ids; blocker N/A requires a decision
  raftly gate add --id G-CUSTOM-X --title T --category C --severity major   project-specific check
  raftly gate score [--group production|forgotten-20]
  raftly gate report [--group ...] [--write]   markdown report; --write updates the gate section of LAUNCH.md
                                               and state.production
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from forgelib import cli, docs  # noqa: E402
from forgelib import gate as gatelib  # noqa: E402
from forgelib.fsutil import read_text  # noqa: E402
from forgelib.project import ForgeError, now_iso  # noqa: E402

ICON = {"PASS": "PASS", "WARNING": "WARN", "FAIL": "FAIL", "UNVERIFIED": "UNVERIFIED", "NOT_APPLICABLE": "N/A"}


def report_md(gate: dict, group: str) -> str:
    sc = gatelib.score(gate["checks"], group)
    title = "Production gate" if group == "production" else "Forgotten 20% audit"
    lines = [f"**{title}: {sc['readiness']}**" if group == "production" else f"**{title}**", ""]
    cov = f"{round(sc['coverage'] * 100)}%" if sc["coverage"] is not None else "—"
    score = f"{round(sc['score'] * 100)}%" if sc["score"] is not None else "UNVERIFIED (insufficient evidence)"
    lines.append(f"- Evidence coverage: {cov} of applicable weight · Score: {score}")
    lines.append("- Counts: " + ", ".join(f"{k} {v}" for k, v in sorted(sc["counts"].items())))
    if sc["blocker_failures"]:
        lines.append("- **Blocker failures:** " + ", ".join(sc["blocker_failures"]))
    if sc["blocker_unverified"]:
        lines.append("- Blockers without evidence: " + ", ".join(sc["blocker_unverified"]))
    lines += ["", "| Check | Category | Severity | Status | Evidence / note |", "|---|---|---|---|---|"]
    order = {"FAIL": 0, "UNVERIFIED": 1, "WARNING": 2, "PASS": 3, "NOT_APPLICABLE": 4}
    for c in sorted([c for c in gate["checks"] if c["group"] == group], key=lambda c: (order[c["status"]], c["id"])):
        note = ", ".join(c.get("evidence", []))
        extra = c.get("note") or c.get("na_reason") or ""
        note = f"{note} — {extra}" if note and extra else (note or extra)
        lines.append(f"| {c['id']} — {c['title']} | {c['category']} | {c['severity']} | {ICON[c['status']]} | {note.replace('|', '/')} |")
    lines.append("")
    lines.append("Scores are derived from gate statuses (weights: blocker 3, major 2, minor 1; PASS 1, WARNING 0.5, "
                 "FAIL 0; UNVERIFIED and N/A excluded). No evidence means no PASS.")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    p = cli.parser("gate.py", "Production gate")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    s = sub.add_parser("set")
    s.add_argument("check")
    s.add_argument("status", choices=["PASS", "WARNING", "FAIL", "UNVERIFIED", "NOT_APPLICABLE"])
    s.add_argument("--evidence", default="")
    s.add_argument("--note", default=None)
    s.add_argument("--na-reason", default=None)
    a = sub.add_parser("add")
    a.add_argument("--id", required=True)
    a.add_argument("--title", required=True)
    a.add_argument("--category", required=True)
    a.add_argument("--severity", required=True, choices=["blocker", "major", "minor"])
    for name in ("score", "report"):
        q = sub.add_parser(name)
        q.add_argument("--group", default="production", choices=["production", "forgotten-20"])
        if name == "report":
            q.add_argument("--write", action="store_true")
    args = p.parse_args(argv)
    proj = cli.project(args).require()
    state = proj.state()

    if args.cmd == "init":
        profile = state["project"].get("profile") or {}
        existing = (proj.gate() or {}).get("checks", [])
        checks = gatelib.instantiate(profile, existing, now=now_iso())
        proj.save_gate({"generated_at": now_iso(), "evaluated_at": None, "profile": profile, "checks": checks})
        prod = [c for c in checks if c["group"] == "production"]
        na = [c for c in prod if c["status"] == "NOT_APPLICABLE"]
        cli.emit(args, {"checks": len(checks), "production_applicable": len(prod) - len(na), "not_applicable": len(na)},
                 lambda d: f"Gate initialised: {d['production_applicable']} applicable production checks, "
                           f"{d['not_applicable']} not applicable to this product profile.")
        return 0
    gate = proj.gate()
    if gate is None:
        raise ForgeError("gate not initialised: run gate.py init")

    if args.cmd == "set":
        check = next((c for c in gate["checks"] if c["id"] == args.check), None)
        if check is None:
            raise ForgeError(f"unknown check {args.check}")
        evidence = cli.split_csv(args.evidence)
        known = {r["id"] for r in proj.evidence()["records"]}
        problem = gatelib.set_status_problem(check, args.status, evidence, args.na_reason, known)
        if problem:
            raise ForgeError(f"{args.check}: {problem}")
        recs = {r["id"]: r for r in proj.evidence()["records"]}
        if args.status == "PASS" and any(recs[e]["result"] == "FAIL" for e in evidence):
            raise ForgeError(f"{args.check}: cannot PASS on failing evidence")
        check["status"] = args.status
        check["evidence"] = evidence if args.status != "NOT_APPLICABLE" else []
        if args.note:
            check["note"] = args.note
        if args.status == "NOT_APPLICABLE":
            check["na_reason"] = args.na_reason
        else:
            check.pop("na_reason", None)
        check["updated_at"] = now_iso()
        gate["evaluated_at"] = now_iso()
        proj.save_gate(gate)
        cli.emit(args, check, lambda c: f"{c['id']} -> {c['status']}")
        return 0
    if args.cmd == "add":
        if not args.id.startswith("G-"):
            raise ForgeError("check ids start with G-")
        if any(c["id"] == args.id for c in gate["checks"]):
            raise ForgeError(f"{args.id} exists")
        gate["checks"].append({"id": args.id, "group": "production", "category": args.category, "title": args.title,
                               "severity": args.severity, "status": "UNVERIFIED", "evidence": [], "updated_at": now_iso()})
        proj.save_gate(gate)
        cli.emit(args, {"added": args.id}, lambda d: f"Added {d['added']}")
        return 0
    if args.cmd == "score":
        sc = gatelib.score(gate["checks"], args.group)
        cli.emit(args, sc, lambda d: f"{d['readiness']} · coverage {d['coverage']} · score {d['score'] if d['score'] is not None else 'UNVERIFIED'}")
        return 0
    if args.cmd == "report":
        md = report_md(gate, args.group)
        if args.write:
            launch = proj.path("LAUNCH.md")
            text = read_text(launch) if launch.exists() else "# Launch Readiness\n"
            key = "gate" if args.group == "production" else "forgotten20"
            heading = "Production gate" if args.group == "production" else "Forgotten 20% audit"
            proj.write_text("LAUNCH.md", docs.replace_section(text, key, md, heading=heading))
            if args.group == "production":
                sc = gatelib.score(gate["checks"])
                state["production"] = {"readiness": sc["readiness"], "last_gate_at": now_iso(),
                                       "score": sc["score"], "coverage": sc["coverage"]}
                state.setdefault("documents", {})["LAUNCH.md"] = {"status": "CURRENT", "updated_at": now_iso()}
                proj.save_state(state, event=f"Production gate evaluated: {sc['readiness']}")
        cli.emit(args, {"markdown": md}, lambda d: d["markdown"])
        return 0
    return 0


if __name__ == "__main__":
    cli.run(main)
