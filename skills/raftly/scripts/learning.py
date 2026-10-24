#!/usr/bin/env python3
"""Learning Firewall: classify observations, keep project memory, propose (never apply) core changes.

Commands:
  classify --kind K [--quality Q] [--authority A] [--repeats N] [--cross-project] [--objective]
           [--contradicted] [--private]
                     deterministic outcome: REJECT / PROJECT_ONLY / CANDIDATE / CORE_PROPOSAL
  record --title T --kind K [classification flags...] [--related F001]
                     classify and store: L1 learning (learnings/L-xxx) always for non-REJECT;
                     CANDIDATE/CORE_PROPOSAL also create a learning-candidates/LC-xxx file
  propose <LC-ID> --pattern "generalized statement" --rule "proposed Raftly rule" [--source URL]...
                     write a sanitized proposal for the Raftly maintainers into
                     .raftly/learning-candidates/proposals/. Refuses if the text contains project
                     identifiers, paths, emails, secrets or private URLs. Never modifies Raftly.
  list               list learnings and candidates

Kinds: preference, local_fact, implementation_finding, engineering_failure, pattern, outcome, override
Quality: none, anecdotal, observed, reproduced, tested
Authority: none, user, project, community, official_docs, standard
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from forgelib import cli  # noqa: E402
from forgelib.brand import name as brand_name  # noqa: E402
from forgelib import learning as lf  # noqa: E402
from forgelib.fsutil import SKILL_ROOT, assert_not_plugin_core, read_text, slugify  # noqa: E402
from forgelib.project import ForgeError, today  # noqa: E402

KINDS = ["preference", "local_fact", "implementation_finding", "engineering_failure", "pattern", "outcome", "override"]


class _Keep(dict):
    def __missing__(self, key):
        return "{" + key + "}"


def add_flags(sp):
    sp.add_argument("--kind", required=True, choices=KINDS)
    sp.add_argument("--quality", default="none", choices=list(lf.QUALITY))
    sp.add_argument("--authority", default="none", choices=list(lf.AUTHORITY))
    sp.add_argument("--repeats", type=int, default=0)
    sp.add_argument("--cross-project", action="store_true")
    sp.add_argument("--objective", action="store_true")
    sp.add_argument("--contradicted", action="store_true")
    sp.add_argument("--private", action="store_true", help="observation contains project-private detail")


def obs_from(args) -> dict:
    return {"kind": args.kind, "evidence_quality": args.quality, "source_authority": args.authority,
            "repeat_count": args.repeats, "cross_project": args.cross_project, "objective": args.objective,
            "contradicted": args.contradicted, "contains_private": args.private}


def main(argv: list[str]) -> int:
    p = cli.parser("learning.py", "Learning Firewall")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("classify")
    add_flags(c)
    r = sub.add_parser("record")
    r.add_argument("--title", required=True)
    r.add_argument("--related", default="")
    add_flags(r)
    pr = sub.add_parser("propose")
    pr.add_argument("candidate")
    pr.add_argument("--pattern", required=True)
    pr.add_argument("--rule", required=True)
    pr.add_argument("--source", action="append", default=[])
    sub.add_parser("list")
    args = p.parse_args(argv)

    if args.cmd == "classify":
        res = lf.classify(obs_from(args))
        cli.emit(args, res, lambda d: f"{d['outcome']} (credibility {d['credibility']}): " + "; ".join(d["reasons"]))
        return 0

    proj = cli.project(args).require()
    if args.cmd == "record":
        obs = obs_from(args)
        res = lf.classify(obs)
        if res["outcome"] == "REJECT":
            cli.emit(args, {"stored": False, **res}, lambda d: "REJECTED — not stored: " + "; ".join(d["reasons"]))
            return 0
        lid = proj.next_id("learning")
        fm = {"id": lid, "title": args.title, "outcome": res["outcome"], **obs,
              "related": cli.split_csv(args.related), "candidate": None, "created_at": today()}
        cand_id = None
        if res["outcome"] in ("CANDIDATE", "CORE_PROPOSAL"):
            cand_id = proj.next_id("candidate")
            fm["candidate"] = cand_id
        body = read_text(SKILL_ROOT / "templates/records/learning.md").format_map(_Keep(
            {**fm, "credibility": res["credibility"], "reasons": "\n".join(f"- {x}" for x in res["reasons"])}))
        path = proj.write_record("learning", fm, body)
        out = {"stored": True, "learning": lid, "path": str(path), **res}
        if cand_id:
            cfm = {"id": cand_id, "title": args.title, "outcome": res["outcome"], "domain_scope": "TBD",
                   "confidence": res["credibility"], **obs, "sources": [], "from_learnings": [lid],
                   "proposal": None, "created_at": today()}
            cbody = read_text(SKILL_ROOT / "templates/records/learning-candidate.md").format_map(_Keep(cfm))
            out["candidate"] = cand_id
            out["candidate_path"] = str(proj.write_record("candidate", cfm, cbody))
        st = proj.state()
        st.setdefault("learning", {})
        st["learning"]["project_learnings"] = len(proj.records("learning"))
        st["learning"]["candidates"] = len(proj.records("candidate"))
        proj.save_state(st, event=f"Learning {lid} recorded as {res['outcome']}")
        cli.emit(args, out, lambda d: f"Stored {d['learning']} as {d['outcome']}"
                 + (f"; candidate {d['candidate']} created (project-local, never auto-applied)" if d.get("candidate") else ""))
        return 0

    if args.cmd == "propose":
        path, fm, body = proj.find_record("candidate", args.candidate)
        if fm["outcome"] != "CORE_PROPOSAL":
            raise ForgeError(f"{args.candidate} is {fm['outcome']}; only CORE_PROPOSAL candidates can be proposed")
        st = proj.state()
        terms = [st["project"]["name"], st["project"].get("slug", ""), proj.root.name]
        text = "\n".join([args.pattern, args.rule, *args.source])
        hits = lf.leak_scan(text, terms)
        if hits:
            raise ForgeError("proposal contains project-private content (rule 20); rewrite it generically:\n  - "
                             + "\n  - ".join(hits))
        prop_rel = f"learning-candidates/proposals/{args.candidate}-{slugify(args.pattern, 40)}.md"
        target = proj.path(prop_rel)
        assert_not_plugin_core(target)
        content = (
            f"# {brand_name()} core proposal: {args.pattern}\n\n"
            "> Generated by `learning.py propose`. Sanitized: contains no project names, paths, data or code.\n"
            f"> Submit as a pull request to the {brand_name()} repository for maintainer review. {brand_name()} never applies\n"
            "> this automatically (Constitution rules 19–21).\n\n"
            f"## Generalized pattern\n{args.pattern}\n\n"
            f"## Proposed rule / change\n{args.rule}\n\n"
            f"## Evidence class\n- Quality: {fm.get('evidence_quality')}\n- Source authority: {fm.get('source_authority')}\n"
            f"- Repeat count: {fm.get('repeat_count', 0)}\n- Cross-project: {fm.get('cross_project')}\n"
            f"- Contradicted: {fm.get('contradicted')}\n\n"
            "## External sources\n" + ("\n".join(f"- {s}" for s in args.source) or "- None provided") + "\n\n"
            "## Maintainer checklist\n- [ ] Generally applicable beyond one project\n- [ ] No private information\n"
            "- [ ] No conflict with the Constitution\n- [ ] Tests/evals added for the new behaviour\n"
            "- [ ] Reviewed by a maintainer\n"
        )
        proj.write_text(prop_rel, content)
        fm["proposal"] = prop_rel
        proj.update_record(path, fm, body, "candidate")
        proj.save_state(proj.state(), event=f"Core proposal drafted from {args.candidate} (not applied)")
        cli.emit(args, {"proposal": str(target)}, lambda d: f"Sanitized proposal written to {d['proposal']}. "
                 "Review it, then open a PR against the Raftly repository if you want to share it.")
        return 0

    if args.cmd == "list":
        out = {"learnings": [{"id": fm["id"], "title": fm["title"], "outcome": fm["outcome"]} for _, fm, _ in proj.records("learning")],
               "candidates": [{"id": fm["id"], "title": fm["title"], "outcome": fm["outcome"]} for _, fm, _ in proj.records("candidate")]}
        cli.emit(args, out, lambda d: "\n".join([f"{x['id']} [{x['outcome']}] {x['title']}" for x in d["learnings"] + d["candidates"]]) or "No learnings yet.")
        return 0
    return 0


if __name__ == "__main__":
    cli.run(main)
