"""Build-graph logic: DAG validation, cycle detection, phases, next work."""

from __future__ import annotations

from collections import defaultdict

from .model import DONE_STATUSES, TERMINAL_STATUSES


def index(nodes: list[dict]) -> dict[str, dict]:
    return {n["id"]: n for n in nodes}


def problems(nodes: list[dict]) -> list[str]:
    """Structural problems: duplicate ids, unknown dependencies, self-loops, cycles."""
    errs: list[str] = []
    seen: set[str] = set()
    for n in nodes:
        if n["id"] in seen:
            errs.append(f"duplicate node id {n['id']}")
        seen.add(n["id"])
    for n in nodes:
        for d in n.get("depends_on", []):
            if d == n["id"]:
                errs.append(f"{n['id']} depends on itself")
            elif d not in seen:
                errs.append(f"{n['id']} depends on unknown node {d}")
    cyc = find_cycle(nodes)
    if cyc:
        errs.append("dependency cycle: " + " -> ".join(cyc))
    return errs


def find_cycle(nodes: list[dict]) -> list[str] | None:
    graph = {n["id"]: [d for d in n.get("depends_on", []) if d != n["id"]] for n in nodes}
    WHITE, GREY, BLACK = 0, 1, 2
    color = {k: WHITE for k in graph}
    stack: list[str] = []

    def visit(u: str) -> list[str] | None:
        color[u] = GREY
        stack.append(u)
        for v in graph.get(u, []):
            if v not in color:
                continue
            if color[v] == GREY:
                return stack[stack.index(v):] + [v]
            if color[v] == WHITE:
                found = visit(v)
                if found:
                    return found
        stack.pop()
        color[u] = BLACK
        return None

    for k in sorted(graph):
        if color[k] == WHITE:
            found = visit(k)
            if found:
                return found
    return None


def phases(nodes: list[dict]) -> list[list[str]]:
    """Topological layers (Kahn). Phase N contains nodes whose deps are all in < N.

    Raises ValueError on a cycle.
    """
    deps = {n["id"]: set(n.get("depends_on", [])) for n in nodes}
    remaining = dict(deps)
    layers: list[list[str]] = []
    done: set[str] = set()
    while remaining:
        layer = sorted(k for k, d in remaining.items() if d <= done)
        if not layer:
            raise ValueError("dependency cycle prevents phase ordering")
        layers.append(layer)
        done.update(layer)
        for k in layer:
            del remaining[k]
    return layers


def phase_of(nodes: list[dict]) -> dict[str, int]:
    return {nid: i for i, layer in enumerate(phases(nodes)) for nid in layer}


def unblocked(nodes: list[dict], allow_unverified: bool = False) -> list[dict]:
    """Nodes ready to work on: not finished, not blocked, all dependencies satisfied.

    A dependency is satisfied when VERIFIED/COMPLETE (or DROPPED). With
    ``allow_unverified`` IMPLEMENTED_UNVERIFIED also counts (explicit opt-in).
    """
    idx = index(nodes)
    ok = set(DONE_STATUSES) | {"DROPPED"}
    if allow_unverified:
        ok.add("IMPLEMENTED_UNVERIFIED")
    order = phase_of(nodes)
    ready = []
    for n in nodes:
        if n["status"] in TERMINAL_STATUSES or n["status"] == "BLOCKED":
            continue
        if n["status"] in ("IMPLEMENTED_UNVERIFIED", "VERIFIED"):
            # verification / Definition-of-Done close-out is itself the next piece of work
            ready.append(n)
            continue
        if all(idx[d]["status"] in ok for d in n.get("depends_on", []) if d in idx):
            ready.append(n)
    # in-progress work first, then verification debt, then phase order, then id
    rank = {"IN_PROGRESS": 0, "PARTIAL": 1, "IMPLEMENTED_UNVERIFIED": 2, "VERIFIED": 4}
    ready.sort(key=lambda n: (rank.get(n["status"], 3), order.get(n["id"], 99), n["id"]))
    return ready


def dependents(nodes: list[dict]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = defaultdict(list)
    for n in nodes:
        for d in n.get("depends_on", []):
            out[d].append(n["id"])
    return out


def ascii_tree(nodes: list[dict]) -> str:
    """Human-readable layered rendering used in BUILD.md."""
    idx = index(nodes)
    lines = []
    for i, layer in enumerate(phases(nodes)):
        lines.append(f"Phase {i}")
        for nid in layer:
            n = idx[nid]
            deps = n.get("depends_on", [])
            arrow = f"  <- {', '.join(deps)}" if deps else ""
            lines.append(f"  [{_mark(n['status'])}] {nid} {n['name']}{arrow}")
    return "\n".join(lines)


def _mark(status: str) -> str:
    return {
        "COMPLETE": "x",
        "VERIFIED": "v",
        "IMPLEMENTED_UNVERIFIED": "?",
        "IN_PROGRESS": ">",
        "PARTIAL": "~",
        "BLOCKED": "!",
        "DROPPED": "-",
    }.get(status, " ")


def progress(nodes: list[dict]) -> dict:
    total = len([n for n in nodes if n["status"] != "DROPPED"])
    counts: dict[str, int] = defaultdict(int)
    for n in nodes:
        counts[n["status"]] += 1
    complete = counts["COMPLETE"]
    verified = counts["VERIFIED"] + complete
    return {
        "total": total,
        "by_status": dict(counts),
        "complete_pct": round(100 * complete / total, 1) if total else None,
        "verified_pct": round(100 * verified / total, 1) if total else None,
    }
