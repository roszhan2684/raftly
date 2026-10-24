#!/usr/bin/env python3
"""Decision records (ADRs), founder overrides and the Decision Book.

Commands:
  new --title T --owner architect --type RECOMMEND --impact high --reversibility low --confidence 75
      [--category architecture] [--affects REQ-001,F002] [--revisit "..."] [--status ACCEPTED]
                         create ADR-xxx from the template (body sections to fill in)
  override <ADR> --chosen "MongoDB" --reason "team expertise" [--consequences "..."] [--by founder]
                         Founder overrides Raftly's recommendation: writes a NEW accepted ADR that
                         supersedes the original, keeping Raftly's recommendation, the choice, the
                         reason and consequences (Constitution rule 12). The original is preserved.
  supersede <ADR> --by <ADR>       mark an ADR superseded by another
  status <ADR> <STATUS>            PROPOSED / ACCEPTED / REJECTED / DEPRECATED
  list [--type1]                   list decisions
  book                             regenerate the summary table in .raftly/DECISIONS.md
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from forgelib import cli, docs, model  # noqa: E402
from forgelib.checks import role_ids  # noqa: E402
from forgelib.fsutil import SKILL_ROOT, read_text, slugify  # noqa: E402
from forgelib.project import ForgeError, now_iso, today  # noqa: E402

TEMPLATE = SKILL_ROOT / "templates" / "records" / "adr.md"


class _Keep(dict):
    def __missing__(self, key):
        return "{" + key + "}"


def is_type1(fm: dict) -> bool:
    return bool(fm.get("type1")) or fm.get("reversibility") == "low" or fm.get("impact") == "high"


def book_table(records) -> str:
    rows = ["| ID | Decision | Why (short) | Owner | Type | Confidence | Reversibility | Status |",
            "|---|---|---|---|---|---|---|---|"]
    for p, fm, body in sorted(records, key=lambda r: model.id_number(r[1]["id"])):
        why = docs.first_paragraph(docs.find_section(body, "Rationale") or docs.find_section(body, "Decision"), 120)
        why = why.replace("|", "\\|") or "—"
        status = fm["status"]
        if fm.get("superseded_by"):
            status += f" → {fm['superseded_by']}"
        if fm.get("override"):
            status += " (founder override)"
        t1 = " · Type-1" if is_type1(fm) else ""
        rows.append(f"| [{fm['id']}](decisions/{p.name}) | {fm['title']} | {why} | {fm['owner_role']} | "
                    f"{fm['decision_type']}{t1} | {fm['confidence']} | {fm['reversibility']} | {status} |")
    return "\n".join(rows) + "\n\nGenerated from `decisions/` by `decisions.py book`. Edit the ADRs, not this table."


def main(argv: list[str]) -> int:
    p = cli.parser("decisions.py", "ADRs, overrides and the Decision Book")
    sub = p.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new")
    n.add_argument("--title", required=True)
    n.add_argument("--owner", required=True)
    n.add_argument("--type", required=True, choices=model.DECISION_TYPES)
    n.add_argument("--impact", required=True, choices=model.LEVELS)
    n.add_argument("--reversibility", required=True, choices=model.LEVELS)
    n.add_argument("--confidence", type=int, required=True)
    n.add_argument("--category", default=None)
    n.add_argument("--affects", default="")
    n.add_argument("--revisit", default=None)
    n.add_argument("--status", default="ACCEPTED", choices=model.DECISION_STATUSES)
    o = sub.add_parser("override")
    o.add_argument("adr")
    o.add_argument("--chosen", required=True)
    o.add_argument("--reason", required=True)
    o.add_argument("--consequences", default=None)
    o.add_argument("--by", default="founder")
    s = sub.add_parser("supersede")
    s.add_argument("adr")
    s.add_argument("--by", required=True)
    stt = sub.add_parser("status")
    stt.add_argument("adr")
    stt.add_argument("status", choices=model.DECISION_STATUSES)
    ls = sub.add_parser("list")
    ls.add_argument("--type1", action="store_true")
    sub.add_parser("book")
    args = p.parse_args(argv)
    proj = cli.project(args).require()
    roles = role_ids()

    if args.cmd == "new":
        if args.owner not in roles:
            raise ForgeError(f"unknown owner role {args.owner}; see core/roles.yaml")
        did = proj.next_id("decision")
        fm = {"id": did, "title": args.title, "owner_role": args.owner, "date": today(), "status": args.status,
              "decision_type": args.type, "impact": args.impact, "reversibility": args.reversibility,
              "type1": args.reversibility == "low" or args.impact == "high", "confidence": args.confidence,
              "affects": cli.split_csv(args.affects), "supersedes": [], "superseded_by": None, "evidence": []}
        if args.category:
            fm["category"] = args.category
        if args.revisit:
            fm["revisit_trigger"] = args.revisit
        body = read_text(TEMPLATE).format_map(_Keep({**fm, "confidence": fm["confidence"]}))
        path = proj.write_record("decision", fm, body, filename=f"{did}-{slugify(args.title)}.md")
        cli.emit(args, {"id": did, "path": str(path), "type1": fm["type1"]},
                 lambda d: f"Created {d['id']} ({'Type-1: research thoroughly, needs revisit trigger' if d['type1'] else 'reversible'}) at {d['path']}")
        return 0

    if args.cmd == "override":
        path, fm, body = proj.find_record("decision", args.adr)
        if fm["status"] == "SUPERSEDED":
            raise ForgeError(f"{args.adr} is already superseded by {fm.get('superseded_by')}; override that decision")
        new_id = proj.next_id("decision")
        recommendation = docs.first_paragraph(docs.find_section(body, "Decision"), 300) or fm["title"]
        consequences = args.consequences or (
            "TBD — Raftly must spell out the consequences of this override (risk, cost, migration, "
            "affected features) before continuing.")
        new_fm = {
            "id": new_id, "title": f"{fm['title']} — founder override: {args.chosen}", "owner_role": "founder",
            "date": today(), "status": "ACCEPTED", "decision_type": "FOUNDER", "impact": fm["impact"],
            "reversibility": fm["reversibility"], "type1": is_type1(fm), "confidence": fm["confidence"],
            "category": fm.get("category", "override"), "affects": fm.get("affects", []), "supersedes": [args.adr],
            "superseded_by": None, "evidence": fm.get("evidence", []),
            "revisit_trigger": fm.get("revisit_trigger") or "New evidence that materially changes the risk of this override.",
            "override": {"forge_recommendation": recommendation, "chosen": args.chosen, "reason": args.reason,
                         "by": args.by, "at": now_iso(), "consequences": consequences},
        }
        new_body = (
            f"# {new_id} — {new_fm['title']}\n\n"
            f"## Context\nFounder override of [{args.adr}]({path.name}) — \"{fm['title']}\".\n\n"
            f"## Raftly recommendation (preserved)\n{recommendation}\n\n"
            f"## Decision\n{args.chosen}\n\n"
            f"## Rationale\nFounder's reason: {args.reason}\n\n"
            f"## Consequences\n{consequences}\n\n"
            "## Follow-up\n- Update affected features, architecture and build prompts to follow this decision consistently.\n"
            "- Record any new risk or debt this creates (`records.py add risk`, `records.py new debt`).\n"
            "- Raftly will not re-argue this override unless new evidence materially changes the risk (rule 12 / spec §53).\n\n"
            f"## Revisit trigger\n{new_fm['revisit_trigger']}\n"
        )
        new_path = proj.write_record("decision", new_fm, new_body, filename=f"{new_id}-override-{slugify(args.chosen)}.md")
        fm["status"] = "SUPERSEDED"
        fm["superseded_by"] = new_id
        proj.update_record(path, fm, body, "decision")
        proj.save_state(proj.state(), event=f"Founder override: {args.adr} -> {new_id} ({args.chosen}): {args.reason}")
        _refresh_book(proj)
        cli.emit(args, {"original": args.adr, "override": new_id, "path": str(new_path),
                        "consequences_recorded": bool(args.consequences)},
                 lambda d: f"Recorded founder override {d['override']} superseding {d['original']}."
                           + ("" if d["consequences_recorded"] else " Consequences still need to be written."))
        return 0

    if args.cmd == "supersede":
        path, fm, body = proj.find_record("decision", args.adr)
        npath, nfm, nbody = proj.find_record("decision", args.by)
        fm["status"] = "SUPERSEDED"
        fm["superseded_by"] = args.by
        if args.adr not in nfm.get("supersedes", []):
            nfm.setdefault("supersedes", []).append(args.adr)
        proj.update_record(path, fm, body, "decision")
        proj.update_record(npath, nfm, nbody, "decision")
        proj.save_state(proj.state(), event=f"{args.adr} superseded by {args.by}")
        _refresh_book(proj)
        cli.emit(args, {"superseded": args.adr, "by": args.by}, lambda d: f"{d['superseded']} superseded by {d['by']}")
        return 0

    if args.cmd == "status":
        path, fm, body = proj.find_record("decision", args.adr)
        if args.status == "ACCEPTED" and is_type1(fm) and not fm.get("revisit_trigger"):
            raise ForgeError(f"{args.adr} is Type-1: set revisit_trigger in its frontmatter before accepting (rule 24)")
        fm["status"] = args.status
        proj.update_record(path, fm, body, "decision")
        _refresh_book(proj)
        cli.emit(args, fm, lambda d: f"{d['id']} -> {d['status']}")
        return 0

    if args.cmd == "list":
        recs = proj.records("decision")
        out = [{"id": fm["id"], "title": fm["title"], "status": fm["status"], "type1": is_type1(fm),
                "type": fm["decision_type"], "confidence": fm["confidence"]} for _, fm, _ in recs
               if not args.type1 or is_type1(fm)]
        cli.emit(args, out, lambda o: "\n".join(
            f"{d['id']} [{d['status']}] {'T1 ' if d['type1'] else ''}{d['title']} ({d['type']}, {d['confidence']})" for d in o) or "No decisions yet.")
        return 0

    if args.cmd == "book":
        path = _refresh_book(proj)
        cli.emit(args, {"written": str(path)}, lambda d: f"Decision Book updated: {d['written']}")
        return 0
    return 0


def _refresh_book(proj):
    book = proj.path("DECISIONS.md")
    text = read_text(book) if book.exists() else (
        "# Decision Book\n\nMajor product, design and architecture decisions. Each row links to its ADR, "
        "which holds context, options, evidence, consequences and revisit triggers.\n")
    text = docs.replace_section(text, "decisions", book_table(proj.records("decision")), heading="Decisions")
    proj.write_text("DECISIONS.md", text)
    st = proj.state()
    st.setdefault("documents", {})["DECISIONS.md"] = {"status": "CURRENT", "updated_at": now_iso()}
    proj.save_state(st)
    return book


if __name__ == "__main__":
    cli.run(main)
