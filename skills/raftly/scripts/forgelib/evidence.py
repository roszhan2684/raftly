"""Evidence graph queries: why, impact, untested requirements, UI-only features."""

from __future__ import annotations

from collections import defaultdict, deque

from .model import VERIFICATION_KINDS, kind_of_id

# Relations whose direction is "from depends on / serves to". We normalise
# every edge into an undirected-but-labelled adjacency for traversal, then
# interpret direction per query.
UPSTREAM_RELATIONS = {"implements", "verifies", "measures", "renders", "persists", "exposes", "validates", "depends_on", "mitigates"}
DOWNSTREAM_RELATIONS = {"justifies"}


def _edges(evidence: dict) -> list[tuple[str, str, str]]:
    """Return edges as (upstream, downstream, relation): upstream is the 'why'."""
    out = []
    for link in evidence.get("links", []):
        f, t, r = link["from"], link["to"], link["relation"]
        if r in DOWNSTREAM_RELATIONS:
            out.append((f, t, r))  # requirement justifies feature: requirement is upstream
        elif r == "supersedes":
            out.append((t, f, r))
        else:
            out.append((t, f, r))  # test verifies feature: feature is upstream of the test
    return out


def why(evidence: dict, identifier: str, extra_edges: list[tuple[str, str, str]] | None = None) -> list[list[str]]:
    """All upstream chains explaining why ``identifier`` exists (to requirements/decisions)."""
    edges = _edges(evidence) + (extra_edges or [])
    parents = defaultdict(list)
    for up, down, rel in edges:
        parents[down].append((up, rel))
    chains: list[list[str]] = []

    def walk(node: str, path: list[str], seen: set[str]) -> None:
        ups = parents.get(node, [])
        if not ups:
            if len(path) > 1:
                chains.append(path)
            return
        for up, rel in ups:
            if up in seen:
                continue
            walk(up, path + [f"{up} ({rel})"], seen | {up})

    walk(identifier, [identifier], {identifier})
    return chains


def impact(evidence: dict, identifier: str, extra_edges: list[tuple[str, str, str]] | None = None) -> list[str]:
    """Everything downstream that would be affected if ``identifier`` changed or was removed."""
    edges = _edges(evidence) + (extra_edges or [])
    children = defaultdict(list)
    for up, down, _ in edges:
        children[up].append(down)
    seen: list[str] = []
    q = deque([identifier])
    while q:
        cur = q.popleft()
        for nxt in children.get(cur, []):
            if nxt not in seen and nxt != identifier:
                seen.append(nxt)
                q.append(nxt)
    return seen


def passing_verification(evidence: dict) -> set[str]:
    return {r["subject"] for r in evidence.get("records", []) if r["result"] == "PASS" and r["kind"] in VERIFICATION_KINDS}


def failing_latest(evidence: dict) -> set[str]:
    """Subjects whose most recent verification record failed."""
    latest: dict[str, dict] = {}
    for r in evidence.get("records", []):
        if r["kind"] in VERIFICATION_KINDS:
            latest[r["subject"]] = r
    return {s for s, r in latest.items() if r["result"] == "FAIL"}


def verified_subjects(evidence: dict) -> set[str]:
    """Subjects with passing verification whose latest verification did not fail.

    Also counts subjects verified through a TEST- entity that ``verifies`` them
    and has a passing record.
    """
    passing = passing_verification(evidence) - failing_latest(evidence)
    out = set(passing)
    for link in evidence.get("links", []):
        if link["relation"] == "verifies" and link["from"] in passing:
            out.add(link["to"])
    return out


def untested_requirements(requirements: list[dict], features: dict[str, dict], evidence: dict) -> list[str]:
    """Active requirements with no verification path (directly or via a verified feature)."""
    verified = verified_subjects(evidence)
    out = []
    for req in requirements:
        if req.get("status") != "ACTIVE" or req.get("priority") == "WONT":
            continue
        rid = req["id"]
        if rid in verified:
            continue
        feats = set(req.get("features") or [])
        feats |= {fid for fid, fm in features.items() if rid in (fm.get("requirements") or [])}
        if feats and any(f in verified for f in feats):
            continue
        out.append(rid)
    return out


def ui_only_features(features: dict[str, dict], evidence: dict) -> list[str]:
    """Features that have screens/components linked but no API/service/table/test linkage.

    Only meaningful for products with a backend; callers decide whether to ask.
    """
    linked = defaultdict(set)
    for link in evidence.get("links", []):
        for a, b in ((link["from"], link["to"]), (link["to"], link["from"])):
            k = kind_of_id(b)
            if k:
                linked[a].add(k)
    out = []
    for fid in features:
        kinds = linked.get(fid, set())
        if kinds & {"screen", "component"} and not kinds & {"api", "service", "table", "test", "job"}:
            out.append(fid)
    return out
