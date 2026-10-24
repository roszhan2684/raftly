#!/usr/bin/env python3
"""Validate a Raftly project: schemas, ID references, graph, evidence integrity, gate, language.

Exit codes: 0 valid (warnings allowed), 1 errors found, 2 usage/IO error.

  validate_project.py [--root DIR] [--json] [--strict]   (--strict: warnings fail too)
  validate_project.py --blueprint-gate                   only the Blueprint Completion Gate
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from forgelib import cli  # noqa: E402
from forgelib.checks import blueprint_gaps, validate  # noqa: E402


def main(argv: list[str]) -> int:
    p = cli.parser("validate_project.py", "Validate .raftly/ integrity")
    p.add_argument("--strict", action="store_true")
    p.add_argument("--blueprint-gate", action="store_true")
    args = p.parse_args(argv)
    proj = cli.project(args).require()
    if args.blueprint_gate:
        gaps = blueprint_gaps(proj)
        cli.emit(args, {"passes": not gaps, "gaps": gaps},
                 lambda d: "Blueprint Completion Gate: PASS" if d["passes"] else
                 "Blueprint Completion Gate: NOT MET\n" + "\n".join(f"  - {g}" for g in d["gaps"]))
        return 0 if not gaps else 1
    res = validate(proj)

    def text(r):
        lines = []
        for e in r["errors"]:
            lines.append(f"ERROR   {e}")
        for w in r["warnings"]:
            lines.append(f"WARNING {w}")
        lines.append(f"{'VALID' if r['ok'] else 'INVALID'}: {len(r['errors'])} error(s), {len(r['warnings'])} warning(s)")
        return "\n".join(lines)
    cli.emit(args, res, text)
    if not res["ok"]:
        return 1
    if args.strict and res["warnings"]:
        return 1
    return 0


if __name__ == "__main__":
    cli.run(main)
