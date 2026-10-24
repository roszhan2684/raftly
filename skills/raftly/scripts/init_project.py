#!/usr/bin/env python3
"""Initialise a Raftly project (.raftly/) without overwriting existing data.

Creates only what every project needs: state.yaml, the empty registries and a
minimal PROJECT.md. Documents, ADRs, features and prompts are created later,
only when relevant (Constitution: no meaningless empty documents).

Examples:
  init_project.py --name "Calculator" --mode GREENFIELD --product-type consumer-utility \
      --profile surfaces=[web,ios,android] backend=false
  init_project.py --name "Acme" --mode RECOVERY --stage ASSESSMENT
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from forgelib import cli, model  # noqa: E402
from forgelib.project import STATE_HEADER, new_state, now_iso  # noqa: E402

PROJECT_MD = """# {name}

> Raftly project file. Human-readable summary of what this project is and how
> Raftly is operating on it. Canonical machine state lives in `state.yaml`.

- **Mode:** {mode}
- **Stage:** {stage}
- **Product type:** {product_type}
- **Initialised:** {created}

## Idea / goal

{summary}

## Profile

{profile}

## Where things live

| What | File |
|---|---|
| Machine state | `state.yaml` |
| Requirements | `requirements.yaml` |
| Decisions (ADRs) | `decisions/` and `DECISIONS.md` |
| Build graph | `build-graph.yaml` and `BUILD.md` |
| Evidence | `evidence.yaml` |
| Assumptions / risks | `assumptions.yaml`, `risks.yaml` |
"""


def main(argv: list[str]) -> int:
    p = cli.parser("init_project.py", "Initialise .raftly/ for a project")
    p.add_argument("--name", required=True)
    p.add_argument("--mode", default="GREENFIELD", choices=model.MODES)
    p.add_argument("--stage", default=None, choices=model.STAGES)
    p.add_argument("--product-type", default="unclassified")
    p.add_argument("--summary", default="", help="one-paragraph idea or goal in the user's words")
    p.add_argument("--profile", nargs="*", default=[], metavar="KEY=VALUE",
                   help="profile flags, e.g. surfaces=[web,ios] backend=true personal_data=false")
    args = p.parse_args(argv)
    proj = cli.project(args)

    if proj.exists:
        state = proj.state()
        cli.emit(args, {"created": False, "reason": "already initialised", "state": state["project"]},
                 lambda d: f"Raftly project already exists at {proj.forge} (mode {d['state']['mode']}, "
                           f"stage {d['state']['stage']}). Nothing was overwritten.")
        return 0

    profile = cli.parse_kv(args.profile)
    stage = args.stage or ("INTAKE" if args.mode == "GREENFIELD" else "ASSESSMENT")
    state = new_state(args.name, args.mode, args.product_type, profile, stage=stage)
    if args.summary:
        state["project"]["summary"] = args.summary

    proj.forge.mkdir(parents=True, exist_ok=True)
    created = []
    # registries first; state last so a crash never leaves state pointing at nothing
    for filename, key, schema, extra in (
        ("requirements.yaml", "requirements", "requirements", {}),
        ("assumptions.yaml", "assumptions", "assumptions", {}),
        ("risks.yaml", "risks", "risks", {}),
        ("dependencies.yaml", "dependencies", "dependencies", {"cost_mode": profile.get("cost_mode", "BOOTSTRAP")}),
        ("build-graph.yaml", "nodes", "build-graph", {}),
    ):
        if not (proj.forge / filename).exists():
            proj.save_yaml(filename, {**extra, key: []}, schema=schema)
            created.append(filename)
    if not (proj.forge / "evidence.yaml").exists():
        proj.save_evidence({"entities": [], "links": [], "records": []})
        created.append("evidence.yaml")
    if not (proj.forge / "PROJECT.md").exists():
        prof = "\n".join(f"- `{k}`: {v}" for k, v in profile.items()) or "- (not yet classified)"
        proj.write_text("PROJECT.md", PROJECT_MD.format(
            name=args.name, mode=args.mode, stage=stage, product_type=args.product_type,
            created=now_iso(), summary=args.summary or "_Not yet captured._", profile=prof))
        created.append("PROJECT.md")
        state["documents"]["PROJECT.md"] = {"status": "CURRENT", "updated_at": now_iso()}
    proj.save_yaml("state.yaml", state, schema="state", header=STATE_HEADER)
    created.append("state.yaml")
    cli.emit(args, {"created": True, "root": str(proj.root), "files": created, "mode": args.mode, "stage": stage},
             lambda d: f"Initialised Raftly project '{args.name}' ({d['mode']}, stage {d['stage']}).\n"
                       + "\n".join(f"  + .raftly/{f}" for f in d["files"]))
    return 0


if __name__ == "__main__":
    cli.run(main)
