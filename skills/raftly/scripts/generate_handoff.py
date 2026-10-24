#!/usr/bin/env python3
"""Deterministically assemble a handoff document skeleton from Raftly state.

Writes .raftly/HANDOFF.md with: purpose, architecture, critical (Type-1) decisions,
current phase, build status, setup/deploy pointers, known debt, constraints,
priorities and dangerous areas. Sections Raftly cannot derive are marked for the
Raftly Director to complete; nothing is invented.

  generate_handoff.py [--root DIR] [--stdout]
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from forgelib import cli, docs, graph  # noqa: E402
from forgelib.brand import name as brand_name  # noqa: E402
from forgelib import gate as gatelib  # noqa: E402
from forgelib.fsutil import read_text  # noqa: E402
from forgelib.project import now_iso  # noqa: E402

import inspect_repo  # noqa: E402

NEEDS = "_Needs input: Raftly could not derive this from recorded state._"


def handoff(proj) -> str:
    st = proj.state()
    p = st["project"]
    doc = lambda n: read_text(proj.forge / n) if (proj.forge / n).exists() else ""  # noqa: E731
    executive, arch, launch = doc("EXECUTIVE.md"), doc("ARCHITECTURE.md"), doc("LAUNCH.md")
    purpose = docs.first_paragraph(docs.find_section(executive, "What", "Summary")) or p.get("summary") or NEEDS
    overview = docs.find_section(arch, "System overview", "Overview") or NEEDS
    decisions = [fm for _, fm, _ in proj.records("decision")]
    t1 = [fm for fm in decisions if fm["status"] == "ACCEPTED" and (fm.get("type1") or fm.get("reversibility") == "low" or fm.get("impact") == "high")]
    nodes = proj.registry("build-graph.yaml")
    prog = graph.progress(nodes) if nodes else None
    nxt = graph.unblocked(nodes)[:5] if nodes and not graph.problems(nodes) else []
    debt = [fm for _, fm, _ in proj.records("debt") if fm["status"] in ("OPEN", "SCHEDULED")]
    risks = [r for r in proj.registry("risks.yaml") if r["status"] in ("OPEN", "MITIGATING") and r["severity"] in ("high", "critical")]
    untested = [a for a in proj.registry("assumptions.yaml") if a["state"] == "UNTESTED" and a.get("impact") == "high"]
    gate = proj.gate()
    sc = gatelib.score(gate["checks"]) if gate else None
    repo = inspect_repo.inspect(proj.root, 5000)

    out = [f"# Handoff — {p['name']}", "",
           f"> Generated {now_iso()} by `generate_handoff.py` from `.raftly/` state. Mode {p['mode']}, stage {p['stage']}.",
           "> Sections marked _Needs input_ must be completed by the Raftly Director before handing over.", "",
           "## Project purpose", purpose, "",
           "## Architecture", overview, "",
           "## Critical decisions (Type-1, accepted)"]
    out += [f"- **{fm['id']}** {fm['title']} — confidence {fm['confidence']}, reversibility {fm['reversibility']}. "
            f"Revisit when: {fm.get('revisit_trigger', 'not recorded')}" for fm in t1] or ["- None recorded."]
    out += ["", "## Current phase", f"- Stage: **{p['stage']}** · Blueprint: **{st['blueprint']['status']}**"]
    if prog:
        out.append(f"- Build: {prog['total']} nodes · {prog['complete_pct']}% complete · {prog['verified_pct']}% verified")
    out.append(f"- Production readiness: **{sc['readiness'] if sc else 'UNVERIFIED'}**")
    out += ["", "## Setup"]
    stack = ", ".join(repo["frameworks"] + repo["data"]) or "no stack detected"
    out.append(f"- Detected stack: {stack}")
    out.append(f"- Package managers: {', '.join(repo['package_managers']) or 'none detected'}")
    out.append(f"- Tests: {', '.join(repo['tests']) or 'none detected'} · CI: {', '.join(repo['ci']) or 'none detected'}")
    out.append("- Setup steps: see README" if repo["docs"]["readme"] else f"- Setup steps: {NEEDS}")
    out += ["", "## Deploy", docs.find_section(launch, "Deploy", "Rollback", "Launch plan") or NEEDS, "",
            "## Known debt"]
    out += [f"- **{fm['id']}** ({fm['type']}, risk {fm['risk']}) {fm['title']} — fix when: {fm.get('fix_trigger') or 'not set'}" for fm in debt] or ["- None recorded."]
    out += ["", "## Constraints", f"- Constitution: `core/CONSTITUTION.md` in the {brand_name()} skill (simplicity, evidence, no false certification)."]
    out += [f"- {fm['id']}: {fm['title']}" for fm in t1[:5]]
    out += ["", "## Priorities (next unblocked work)"]
    out += [f"1. **{n['id']}** {n['name']} ({n['status']}) — prompts: {', '.join(n.get('prompts', [])) or 'none'}" for n in nxt] or ["- Nothing unblocked; see blocked nodes in BUILD.md."]
    out += ["", "## Dangerous areas"]
    danger = [f"- Risk **{r['id']}** ({r['severity']}): {r['statement']}" for r in risks]
    danger += [f"- Untested high-impact assumption **{a['id']}**: {a['statement']}" for a in untested]
    danger += [f"- Low-reversibility decision **{fm['id']}**: {fm['title']} — do not change without a superseding ADR" for fm in t1 if fm["reversibility"] == "low"]
    if sc and sc["blocker_failures"]:
        danger.append(f"- Failing launch blockers: {', '.join(sc['blocker_failures'])}")
    out += danger or ["- None recorded."]
    out += ["", "## Where to look", "- `.raftly/state.yaml` — mode, stage, progress", "- `.raftly/DECISIONS.md` — why things are the way they are",
            "- `.raftly/BUILD.md` and `prompts/` — what to build next and how", "- `/raftly explain <question>` — ask Raftly using recorded evidence", ""]
    return "\n".join(out)


def main(argv: list[str]) -> int:
    p = cli.parser("generate_handoff.py", "Assemble HANDOFF.md from Raftly state")
    p.add_argument("--stdout", action="store_true")
    args = p.parse_args(argv)
    proj = cli.project(args).require()
    text = handoff(proj)
    if args.stdout:
        print(text)
        return 0
    path = proj.write_text("HANDOFF.md", text)
    st = proj.state()
    st.setdefault("documents", {})["HANDOFF.md"] = {"status": "DRAFT", "updated_at": now_iso()}
    proj.save_state(st, event="Handoff skeleton generated")
    cli.emit(args, {"written": str(path)}, lambda d: f"Handoff skeleton written to {d['written']}")
    return 0


if __name__ == "__main__":
    cli.run(main)
