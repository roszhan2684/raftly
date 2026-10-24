#!/usr/bin/env python3
"""Build graph: validate the DAG, compute phases, find next unblocked work.

Commands:
  validate                       structural checks (unknown deps, cycles)
  phases                         topological phases
  next [--allow-unverified]      next unblocked node(s) with their prompt files
  add --name N --type T [--depends N001,N002] [--features F001] [--prompts 001-x.md] [--dod "a;b"]
  set-status <NODE> <STATUS> [--blocker TEXT]
                                 status change with evidence rules (VERIFIED/COMPLETE need
                                 passing verification evidence; BLOCKED needs a blocker)
  render                         write the graph section of .raftly/BUILD.md and refresh
                                 state.execution.next_nodes
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from forgelib import cli, docs, graph, model  # noqa: E402
from forgelib import evidence as ev  # noqa: E402
from forgelib.fsutil import read_text  # noqa: E402
from forgelib.project import ForgeError  # noqa: E402


def render_section(nodes: list[dict]) -> str:
    phase = graph.phase_of(nodes)
    rows = ["| Phase | Node | Name | Type | Depends on | Status | Prompts |", "|---|---|---|---|---|---|---|"]
    for n in sorted(nodes, key=lambda n: (phase[n["id"]], n["id"])):
        rows.append(
            f"| {phase[n['id']]} | {n['id']} | {n['name']} | {n['type']} | {', '.join(n.get('depends_on', [])) or '—'} "
            f"| {n['status']} | {', '.join(n.get('prompts', [])) or '—'} |"
        )
    prog = graph.progress(nodes)
    return (
        "```text\n" + graph.ascii_tree(nodes) + "\n```\n\n"
        "Legend: `[x]` complete · `[v]` verified · `[?]` implemented, unverified · `[>]` in progress · "
        "`[~]` partial · `[!]` blocked · `[-]` dropped\n\n"
        + "\n".join(rows)
        + f"\n\n**Progress:** {prog['complete_pct']}% complete, {prog['verified_pct']}% verified "
        f"({prog['total']} active nodes). Derived from `build-graph.yaml`; do not edit this block by hand."
    )


def main(argv: list[str]) -> int:
    p = cli.parser("build_graph.py", "Build graph operations")
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("validate")
    sub.add_parser("phases")
    nx = sub.add_parser("next")
    nx.add_argument("--allow-unverified", action="store_true")
    nx.add_argument("--all", action="store_true", help="list every unblocked node, not just the first")
    a = sub.add_parser("add")
    a.add_argument("--name", required=True)
    a.add_argument("--type", required=True, choices=["foundation", "feature", "security", "data", "ops", "quality",
                                                    "design", "integration", "launch", "migration", "research"])
    a.add_argument("--depends", default="")
    a.add_argument("--features", default="")
    a.add_argument("--prompts", default="")
    a.add_argument("--dod", default="", help="definition-of-done items separated by ';'")
    ss = sub.add_parser("set-status")
    ss.add_argument("node")
    ss.add_argument("status", choices=model.WORK_STATUSES)
    ss.add_argument("--blocker", action="append", default=[])
    sub.add_parser("render")
    args = p.parse_args(argv)
    proj = cli.project(args).require()
    nodes = proj.registry("build-graph.yaml")
    cmd = args.cmd or "validate"

    if cmd == "validate":
        probs = graph.problems(nodes)
        cli.emit(args, {"ok": not probs, "problems": probs, "nodes": len(nodes)},
                 lambda d: "Build graph OK (%d nodes)" % d["nodes"] if d["ok"] else "\n".join(d["problems"]))
        return 0 if not probs else 1
    if graph.problems(nodes):
        raise ForgeError("build graph invalid: " + "; ".join(graph.problems(nodes)))

    if cmd == "phases":
        layers = graph.phases(nodes)
        cli.emit(args, layers, lambda d: "\n".join(f"Phase {i}: {', '.join(layer)}" for i, layer in enumerate(d)))
        return 0
    if cmd == "next":
        ready = graph.unblocked(nodes, allow_unverified=args.allow_unverified)
        prompts_dir = proj.forge / "prompts"
        out = []
        for n in ready if args.all else ready[:1]:
            out.append({
                "id": n["id"], "name": n["name"], "status": n["status"],
                "action": "verify" if n["status"] == "IMPLEMENTED_UNVERIFIED" else "complete" if n["status"] == "VERIFIED" else (
                    "continue" if n["status"] in ("IN_PROGRESS", "PARTIAL") else "start"),
                "prompts": [str(prompts_dir / pr) for pr in n.get("prompts", [])],
                "features": n.get("features", []),
                "definition_of_done": n.get("definition_of_done", []),
            })
        blocked = [n["id"] for n in nodes if n["status"] == "BLOCKED"]
        remaining = [n for n in nodes if n["status"] not in model.TERMINAL_STATUSES]
        data = {"next": out, "blocked": blocked, "all_done": not remaining}

        def text(d):
            if d["all_done"]:
                return "All build-graph nodes are COMPLETE or DROPPED. Next: run the production gate (/raftly launch)."
            if not d["next"]:
                return "No unblocked work. Blocked nodes: " + (", ".join(d["blocked"]) or "none") + \
                       " (dependencies may be IMPLEMENTED_UNVERIFIED: verify them first)."
            lines = []
            for n in d["next"]:
                lines.append(f"{n['action'].upper()} {n['id']} {n['name']} ({n['status']})")
                lines += [f"  prompt: {pp}" for pp in n["prompts"]]
            return "\n".join(lines)
        cli.emit(args, data, text)
        return 0
    if cmd == "add":
        nid = proj.next_id("node")
        deps = cli.split_csv(args.depends)
        known = {n["id"] for n in nodes}
        unknown = [d for d in deps if d not in known]
        if unknown:
            raise ForgeError(f"unknown dependencies: {', '.join(unknown)}")
        node = {
            "id": nid, "name": args.name, "type": args.type, "depends_on": deps, "status": "PLANNED",
            "features": cli.split_csv(args.features), "prompts": cli.split_csv(args.prompts),
            "definition_of_done": [x.strip() for x in args.dod.split(";") if x.strip()],
            "blockers": [], "evidence": [], "files": [],
        }
        nodes.append(node)
        if graph.problems(nodes):
            raise ForgeError("; ".join(graph.problems(nodes)))
        proj.save_registry("build-graph.yaml", nodes)
        cli.emit(args, node, lambda d: f"Added {d['id']} {d['name']}")
        return 0
    if cmd == "set-status":
        node = next((n for n in nodes if n["id"] == args.node), None)
        if node is None:
            raise ForgeError(f"unknown node {args.node}")
        evidence = proj.evidence()
        verified = ev.verified_subjects(evidence)
        has_ver = node["id"] in verified or (bool(node.get("features")) and all(f in verified for f in node["features"]))
        if args.blocker:
            node["blockers"] = list(dict.fromkeys(node.get("blockers", []) + args.blocker))
        problem = model.work_transition_problem(node["status"], args.status, has_verification=has_ver,
                                                has_blockers=bool(node.get("blockers")))
        if problem:
            raise ForgeError(f"{node['id']}: {problem}")
        if args.status == "COMPLETE":
            feats = {fm["id"]: fm for _, fm, _ in proj.records("feature")}
            open_feats = [f for f in node.get("features", []) if feats.get(f, {}).get("status") not in ("COMPLETE", "DROPPED")]
            if open_feats:
                raise ForgeError(f"{node['id']}: features not COMPLETE: {', '.join(open_feats)}")
        old = node["status"]
        node["status"] = args.status
        if args.status not in ("BLOCKED",) and old == "BLOCKED" and not args.blocker:
            node["blockers"] = []
        proj.save_registry("build-graph.yaml", nodes)
        st = proj.state()
        if args.status == "IN_PROGRESS":
            st["execution"]["current_node"] = node["id"]
        elif st["execution"].get("current_node") == node["id"] and args.status in model.TERMINAL_STATUSES | {"VERIFIED"}:
            st["execution"]["current_node"] = None
        st["execution"]["next_nodes"] = [n["id"] for n in graph.unblocked(nodes)][:5]
        proj.save_state(st, event=f"{node['id']} {old} -> {args.status}")
        cli.emit(args, node, lambda d: f"{d['id']} -> {d['status']}")
        return 0
    if cmd == "render":
        build = proj.forge / "BUILD.md"
        text = read_text(build) if build.exists() else "# Product Build Document\n"
        text = docs.replace_section(text, "graph", render_section(nodes), heading="Build graph")
        proj.write_text("BUILD.md", text)
        st = proj.state()
        st["execution"]["next_nodes"] = [n["id"] for n in graph.unblocked(nodes)][:5]
        for i, layer in enumerate(graph.phases(nodes)):
            for n in nodes:
                if n["id"] in layer:
                    n["phase"] = i
        proj.save_registry("build-graph.yaml", nodes)
        proj.save_state(st)
        cli.emit(args, {"written": str(build)}, lambda d: f"Rendered build graph into {d['written']}")
        return 0
    return 0


if __name__ == "__main__":
    cli.run(main)
