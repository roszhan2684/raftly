#!/usr/bin/env python3
"""Evidence graph: attach verification evidence and query intent -> implementation -> verification.

Commands:
  record --subject F001 --kind test --result PASS --summary "..." [--ref path] [--command "npm test"]
                                  attach an evidence record (never fabricate: only record what ran)
  entity --id API-calls-create --name "POST /calls" [--path src/api/calls.ts]
  link FROM TO --rel implements|verifies|justifies|...  [--note]
  why <ID>                        upstream chains: why does this exist?
  impact <ID>                     downstream: what breaks if this changes/is removed?
  for <ID>                        evidence records and links touching an id
  untested                        active requirements without a verification path
  ui-only                         features with screens but no API/service/table/test linkage
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from forgelib import cli, model  # noqa: E402
from forgelib import evidence as ev  # noqa: E402
from forgelib.project import ForgeError, now_iso  # noqa: E402


def implicit_edges(proj) -> list[tuple[str, str, str]]:
    """Edges implied by registries (requirement->feature, feature->node, decision->feature)."""
    edges = []
    for r in proj.registry("requirements.yaml"):
        for f in r.get("features") or []:
            edges.append((r["id"], f, "justifies"))
        for d in r.get("decisions") or []:
            edges.append((r["id"], d, "justifies"))
    for _, fm, _ in proj.records("feature"):
        for r in fm.get("requirements") or []:
            edges.append((r, fm["id"], "justifies"))
        for d in fm.get("decisions") or []:
            edges.append((d, fm["id"], "justifies"))
        if fm.get("node"):
            edges.append((fm["id"], fm["node"], "implemented_in"))
    for n in proj.registry("build-graph.yaml"):
        for d in n.get("depends_on", []):
            edges.append((d, n["id"], "enables"))
    return list(dict.fromkeys(edges))


def main(argv: list[str]) -> int:
    p = cli.parser("evidence.py", "Evidence graph operations")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("record")
    r.add_argument("--subject", required=True)
    r.add_argument("--kind", required=True, choices=model.EVIDENCE_KINDS)
    r.add_argument("--result", required=True, choices=model.EVIDENCE_RESULTS)
    r.add_argument("--summary", required=True)
    r.add_argument("--ref", default=None)
    r.add_argument("--command", default=None)
    r.add_argument("--by", default="skill")
    e = sub.add_parser("entity")
    e.add_argument("--id", required=True)
    e.add_argument("--name", required=True)
    e.add_argument("--path", default=None)
    e.add_argument("--status", default="PLANNED", choices=["PLANNED", "EXISTS", "REMOVED"])
    lk = sub.add_parser("link")
    lk.add_argument("source")
    lk.add_argument("target")
    lk.add_argument("--rel", required=True, choices=model.LINK_RELATIONS)
    lk.add_argument("--note", default=None)
    for name in ("why", "impact", "for"):
        q = sub.add_parser(name)
        q.add_argument("id")
    sub.add_parser("untested")
    sub.add_parser("ui-only")
    args = p.parse_args(argv)
    proj = cli.project(args).require()
    data = proj.evidence()

    if args.cmd == "record":
        known = proj.all_known_ids()
        gate = proj.gate() or {"checks": []}
        if args.subject not in known and args.subject not in {c["id"] for c in gate["checks"]}:
            raise ForgeError(f"unknown subject {args.subject}; register it first (feature/requirement/entity/gate check)")
        rec = {"id": proj.next_id("evidence"), "subject": args.subject, "kind": args.kind, "result": args.result,
               "summary": args.summary, "at": now_iso(), "by": args.by}
        if args.ref:
            rec["ref"] = args.ref
        if args.command:
            rec["command"] = args.command
        data["records"].append(rec)
        proj.save_evidence(data)
        cli.emit(args, rec, lambda d: f"Recorded {d['id']}: {d['kind']} {d['result']} for {d['subject']}")
        return 0
    if args.cmd == "entity":
        if model.kind_of_id(args.id) not in model.ENTITY_PREFIXES.values():
            raise ForgeError("entity id must start with SCR-/CMP-/API-/SVC-/TBL-/TEST-/MET-/JOB-/INT-")
        existing = next((x for x in data["entities"] if x["id"] == args.id), None)
        ent = {"id": args.id, "name": args.name, "path": args.path, "status": args.status}
        if existing:
            existing.update(ent)
        else:
            data["entities"].append(ent)
        proj.save_evidence(data)
        cli.emit(args, ent, lambda d: f"Entity {d['id']} saved")
        return 0
    if args.cmd == "link":
        known = proj.all_known_ids()
        for end in (args.source, args.target):
            if end not in known:
                raise ForgeError(f"unknown id {end}; register entities with 'evidence.py entity' first")
        link = {"from": args.source, "to": args.target, "relation": args.rel, "at": now_iso()}
        if args.note:
            link["note"] = args.note
        if not any(x["from"] == link["from"] and x["to"] == link["to"] and x["relation"] == link["relation"] for x in data["links"]):
            data["links"].append(link)
            proj.save_evidence(data)
        cli.emit(args, link, lambda d: f"Linked {d['from']} -{d['relation']}-> {d['to']}")
        return 0

    extra = implicit_edges(proj)
    if args.cmd == "why":
        chains = ev.why(data, args.id, extra)
        cli.emit(args, chains, lambda c: "\n".join(" <- ".join(ch) for ch in c) or f"No recorded rationale chain for {args.id}.")
    elif args.cmd == "impact":
        hit = ev.impact(data, args.id, extra)
        cli.emit(args, hit, lambda h: (f"Changing {args.id} affects: " + ", ".join(h)) if h else f"Nothing recorded depends on {args.id}.")
    elif args.cmd == "for":
        recs = [x for x in data["records"] if x["subject"] == args.id]
        links = [x for x in data["links"] if args.id in (x["from"], x["to"])]
        cli.emit(args, {"records": recs, "links": links})
    elif args.cmd == "untested":
        feats = {fm["id"]: fm for _, fm, _ in proj.records("feature")}
        out = ev.untested_requirements(proj.registry("requirements.yaml"), feats, data)
        cli.emit(args, out, lambda o: ("Requirements without verification: " + ", ".join(o)) if o else "Every active requirement has a verification path.")
    elif args.cmd == "ui-only":
        feats = {fm["id"]: fm for _, fm, _ in proj.records("feature")}
        out = ev.ui_only_features(feats, data)
        cli.emit(args, out, lambda o: ("UI-only features: " + ", ".join(o)) if o else "No UI-only features detected.")
    return 0


if __name__ == "__main__":
    cli.run(main)
