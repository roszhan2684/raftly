#!/usr/bin/env python3
"""Initialise a Raftly project (.raftly/) without overwriting existing data.

Creates only what every project needs: state.yaml, the empty registries and a
minimal PROJECT.md. Documents, ADRs, features and prompts are created later,
only when relevant (Constitution: no meaningless empty documents).

Layout (--layout):
  auto     (default) docs layout for a new project (a missing or empty folder, or
           one with no code and no existing docs/ folder); classic layout otherwise
  docs     machine state in .raftly/, every readable document and the build
           outputs in docs/
  classic  everything in .raftly/, build outputs in artifacts/ (existing repositories)

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
from forgelib.project import DEFAULT_DOCS_DIR, STATE_HEADER, new_state, now_iso  # noqa: E402

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

| What | Where |
|---|---|
| Readable documents, decisions, features, prompts | `{docs}` |
| Blueprint and deck | `{out}` |
| Machine state, requirements, build graph, evidence | `{state}` (`state.yaml`, `requirements.yaml`, `build-graph.yaml`, `evidence.yaml`) |
| Assumptions / risks | `{state}` (`assumptions.yaml`, `risks.yaml`) |
"""


def choose_layout(root: Path, requested: str) -> str | None:
    """Return the docs folder name for the docs layout, or None for classic."""
    if requested == "docs":
        return DEFAULT_DOCS_DIR
    if requested == "classic":
        return None
    if not root.exists():
        return DEFAULT_DOCS_DIR
    docs = root / DEFAULT_DOCS_DIR
    if docs.exists() and any(docs.iterdir()):
        return None  # never mix Raftly documents into an existing docs/ folder
    import inspect_repo

    return DEFAULT_DOCS_DIR if inspect_repo.inspect(root, 2000)["code_files"] == 0 else None


def main(argv: list[str]) -> int:
    p = cli.parser("init_project.py", "Initialise .raftly/ for a project")
    p.add_argument("--name", required=True)
    p.add_argument("--mode", default="GREENFIELD", choices=model.MODES)
    p.add_argument("--stage", default=None, choices=model.STAGES)
    p.add_argument("--product-type", default="unclassified")
    p.add_argument("--summary", default="", help="one-paragraph idea or goal in the user's words")
    p.add_argument("--profile", nargs="*", default=[], metavar="KEY=VALUE",
                   help="profile flags, e.g. surfaces=[web,ios] backend=true personal_data=false")
    p.add_argument("--layout", default="auto", choices=["auto", "docs", "classic"],
                   help="where readable documents go (default auto: docs/ for a new project)")
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
    docs_dir = choose_layout(proj.root, args.layout)
    proj.use_docs_dir(docs_dir)
    state = new_state(args.name, args.mode, args.product_type, profile, stage=stage, docs_dir=docs_dir)
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
    if not proj.path("PROJECT.md").exists():
        prof = "\n".join(f"- `{k}`: {v}" for k, v in profile.items()) or "- (not yet classified)"
        state_dir = proj.forge.name + "/"
        proj.write_text("PROJECT.md", PROJECT_MD.format(
            name=args.name, mode=args.mode, stage=stage, product_type=args.product_type,
            created=now_iso(), summary=args.summary or "_Not yet captured._", profile=prof,
            docs=(docs_dir + "/") if docs_dir else state_dir, out=(docs_dir + "/") if docs_dir else "artifacts/",
            state=state_dir))
        created.append("PROJECT.md")
        state["documents"]["PROJECT.md"] = {"status": "CURRENT", "updated_at": now_iso()}
    proj.save_yaml("state.yaml", state, schema="state", header=STATE_HEADER)
    created.append("state.yaml")
    shown = [str(proj.path(f).relative_to(proj.root)) for f in created]
    cli.emit(args, {"created": True, "root": str(proj.root), "files": created, "mode": args.mode, "stage": stage,
                    "layout": "docs" if docs_dir else "classic", "docs_dir": str(proj.docs.relative_to(proj.root))},
             lambda d: f"Initialised Raftly project '{args.name}' ({d['mode']}, stage {d['stage']}, {d['layout']} layout) "
                       f"in {d['root']}.\n" + "\n".join(f"  + {f}" for f in shown))
    return 0


if __name__ == "__main__":
    cli.run(main)
