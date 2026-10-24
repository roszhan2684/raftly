#!/usr/bin/env python3
"""Deterministically grade a project's .raftly/ directory against an eval scenario.

Use it after a live `/raftly` run (or on the shipped examples, as CI does):

  python3 evals/grade.py --scenario calculator --root examples/calculator
  python3 evals/grade.py --scenario recovery --root /tmp/run --fixture evals/cases/04-recovery-broken-repo/fixture
  python3 evals/grade.py --examples          # grade every scenario that names an example

Exit code 0 when every assertion passes (SKIPPED assertions don't fail).
These checks complement, not replace, the behavioural graders in evals/cases/ (claude plugin eval).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(next(iter(sorted((REPO / "skills").glob("*/core/brand.yaml")))).parents[1] / "scripts"))

from forgelib import graph  # noqa: E402
from forgelib.checks import blueprint_gaps, validate  # noqa: E402
from forgelib.fsutil import read_text  # noqa: E402
from forgelib.project import Project  # noqa: E402


def docs_text(proj: Project) -> dict[str, str]:
    return {p.relative_to(proj.forge).as_posix(): read_text(p) for p in proj.forge.rglob("*.md")}


def dotted(data: dict, path: str):
    cur = data
    for part in path.split("."):
        cur = cur.get(part) if isinstance(cur, dict) else None
    return cur


def check(a: dict, proj: Project, fixture: Path | None) -> tuple[str, str]:
    t = a["type"]
    st = proj.state()
    prof = st["project"].get("profile") or {}
    gate = proj.gate() or {"checks": []}
    gstat = {c["id"]: c for c in gate["checks"]}
    decisions = proj.records("decision")
    deps = proj.registry("dependencies.yaml")
    nodes = proj.registry("build-graph.yaml")
    ok = lambda cond, msg: ("PASS" if cond else "FAIL", msg)  # noqa: E731

    if t == "validate_ok":
        res = validate(proj)
        return ok(res["ok"], "; ".join(res["errors"][:3]) or "valid")
    if t == "blueprint_gate":
        gaps = blueprint_gaps(proj)
        return ok(not gaps, "; ".join(gaps[:3]) or "gate passes")
    if t == "profile_equals":
        return ok(prof.get(a["key"]) == a["value"], f"profile.{a['key']} = {prof.get(a['key'])!r}")
    if t == "profile_contains":
        return ok(a["value"] in (prof.get(a["key"]) or []), f"profile.{a['key']} = {prof.get(a['key'])!r}")
    if t == "gate_status":
        s = gstat.get(a["check"], {}).get("status")
        return ok(s == a["status"], f"{a['check']} = {s}")
    if t == "gate_status_in":
        s = gstat.get(a["check"], {}).get("status")
        return ok(s in a["statuses"], f"{a['check']} = {s}")
    if t == "no_adopted_dependency_matching":
        bad = [d["name"] for d in deps if d.get("status") == "ADOPTED" and re.search(a["pattern"], d["name"] + " " + d.get("purpose", ""))]
        return ok(not bad, f"adopted: {bad}" if bad else "none")
    if t == "no_node_matching":
        bad = [n["name"] for n in nodes if re.search(a["pattern"], n["name"])]
        return ok(not bad, f"nodes: {bad}" if bad else "none")
    if t == "node_matches":
        hit = [n["name"] for n in nodes if re.search(a["pattern"], n["name"])]
        return ok(bool(hit), f"nodes: {hit}")
    if t == "adr_title_matches":
        hit = [fm["id"] for _, fm, _ in decisions if re.search(a["pattern"], fm["title"])]
        return ok(bool(hit), f"ADRs: {hit}")
    if t == "adr_status":
        fm = next((fm for _, fm, _ in decisions if fm["id"] == a["id"]), None)
        return ok(fm is not None and fm["status"] == a["status"], f"{a['id']} = {fm and fm['status']}")
    if t == "override_recorded":
        hit = [fm["id"] for _, fm, _ in decisions if fm.get("override") and re.search(a["pattern"], json.dumps(fm["override"]))
               and fm["override"].get("consequences") and not fm["override"]["consequences"].startswith("TBD")]
        return ok(bool(hit), f"override ADRs with consequences: {hit}")
    if t == "doc_exists":
        return ok((proj.forge / a["file"]).exists(), a["file"])
    if t == "doc_contains":
        p = proj.forge / a["file"]
        return ok(p.exists() and re.search(a["pattern"], read_text(p)) is not None, f"{a['file']} ~ {a['pattern']}")
    if t == "any_doc_contains":
        hit = [k for k, v in docs_text(proj).items() if re.search(a["pattern"], v)]
        return ok(bool(hit), f"found in {hit[:3]}")
    if t == "no_doc_contains":
        hit = [k for k, v in docs_text(proj).items() if re.search(a["pattern"], v)]
        return ok(not hit, f"found in {hit[:3]}" if hit else "none")
    if t == "min_count":
        n = {"prompts": len(proj.prompts()), "features": len(proj.records("feature")), "decisions": len(decisions),
             "nodes": len(nodes), "requirements": len(proj.registry("requirements.yaml"))}[a["kind"]]
        return ok(n >= a["value"], f"{a['kind']} = {n}")
    if t in ("learning_outcome", "learning_outcome_not"):
        recs = [fm for _, fm, _ in proj.records("learning") if re.search(a.get("title_pattern", "."), fm["title"])]
        if t == "learning_outcome":
            return ok(any(fm["outcome"] == a["outcome"] for fm in recs), f"learnings: {[(fm['id'], fm['outcome']) for fm in recs]}")
        return ok(not any(fm["outcome"] == a["outcome"] for fm in recs), f"learnings: {[(fm['id'], fm['outcome']) for fm in recs]}")
    if t == "no_learning_candidates":
        return ok(not proj.records("candidate"), f"{len(proj.records('candidate'))} candidates")
    if t == "open_founder_decision_matches":
        lst = st["blueprint"].get("open_founder_decisions") or []
        return ok(any(re.search(a["pattern"], x) for x in lst), f"open: {lst}")
    if t == "no_open_founder_decision_matching":
        lst = st["blueprint"].get("open_founder_decisions") or []
        return ok(not any(re.search(a["pattern"], x) for x in lst), f"open: {lst}")
    if t == "state_in":
        v = dotted(st, a["path"])
        return ok(v in a["values"], f"{a['path']} = {v}")
    if t == "requirement_superseded":
        r = next((r for r in proj.registry("requirements.yaml") if r["id"] == a["id"]), None)
        return ok(bool(r) and r["status"] == "SUPERSEDED" and bool(r.get("superseded_by")), f"{a['id']} = {r and r['status']}")
    if t == "no_pass_without_evidence":
        bad = [c["id"] for c in gate["checks"] if c["status"] in ("PASS", "WARNING") and not c.get("evidence")]
        return ok(bool(gate["checks"]) and not bad, f"bad: {bad}" if bad else f"{len(gate['checks'])} checks, none unsupported")
    if t == "file_unchanged":
        if fixture is None:
            return "SKIPPED", "needs --fixture"
        cur, orig = proj.root / a["file"], fixture / a["file"]
        h = lambda p: hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None  # noqa: E731
        return ok(h(cur) == h(orig) and h(cur) is not None, a["file"])
    if t == "graph_valid":
        return ok(not graph.problems(nodes), "graph")
    return "FAIL", f"unknown assertion type {t}"


def grade(scenario: dict, root: Path, fixture: Path | None) -> list[dict]:
    proj = Project(root)
    if not proj.exists:
        return [{"assertion": {"type": "forge_exists"}, "result": "FAIL", "detail": f"no .raftly/state.yaml in {root}"}]
    out = []
    for a in scenario["structural_assertions"]:
        try:
            res, detail = check(a, proj, fixture)
        except Exception as exc:  # report, don't crash the whole run
            res, detail = "FAIL", f"error: {exc}"
        out.append({"assertion": a, "result": res, "detail": detail})
    return out


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--scenario")
    p.add_argument("--root")
    p.add_argument("--fixture")
    p.add_argument("--examples", action="store_true", help="grade all scenarios with a shipped example")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    spec = json.loads((HERE / "evals.json").read_text())
    scenarios = {e["id"]: e for e in spec["evals"]}
    runs = []
    if args.examples:
        runs = [(s, REPO / s["example"], None) for s in spec["evals"] if s.get("example")]
    else:
        if not args.scenario or not args.root:
            p.error("--scenario and --root are required (or use --examples)")
        runs = [(scenarios[args.scenario], Path(args.root), Path(args.fixture) if args.fixture else None)]
    failed = 0
    report = []
    for s, root, fixture in runs:
        results = grade(s, root, fixture)
        report.append({"scenario": s["id"], "root": str(root), "results": results})
        if not args.json:
            print(f"== {s['name']} ({root})")
            for r in results:
                print(f"  [{r['result']:7}] {r['assertion']['type']}: {r['detail']}")
        failed += sum(1 for r in results if r["result"] == "FAIL")
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("ALL PASS" if not failed else f"{failed} assertion(s) failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
