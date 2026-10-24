#!/usr/bin/env python3
"""Migrate a project's .raftly/ schema to the current version.

Rules (spec section 37): never silently reinterpret prior decisions; preserve history;
back up before writing. Each migration is a pure function state -> state plus an
optional file-level step, registered in MIGRATIONS.

  migrate_schema.py --check          report current vs target version (exit 1 if migration needed)
  migrate_schema.py                  migrate in place (backup in .raftly/.backup/<timestamp>/)
  migrate_schema.py --dry-run        show what would change

Migration 0 -> 1 handles pre-release / hand-written state files that lack the
`raftly` block or use legacy field names.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from forgelib import FORGE_VERSION, SCHEMA_VERSION, cli, model  # noqa: E402
from forgelib.project import FORGE_DIR, ForgeError, now_iso  # noqa: E402
from forgelib.schema import validate_named  # noqa: E402

LEGACY_STATUS = {"DONE": "COMPLETE", "TODO": "PLANNED", "WIP": "IN_PROGRESS", "VERIFY": "IMPLEMENTED_UNVERIFIED"}


def m0_to_1(state: dict, proj) -> tuple[dict, list[str]]:
    notes = []
    if "engine" not in state:
        state = {"engine": {"version": FORGE_VERSION, "schema_version": 1}, **{k: v for k, v in state.items() if k != "forge"}}
        notes.append("added engine.version / engine.schema_version")
    proj_block = state.setdefault("project", {})
    if "phase" in proj_block and "stage" not in proj_block:
        proj_block["stage"] = str(proj_block.pop("phase")).upper()
        notes.append("renamed project.phase -> project.stage")
    if proj_block.get("stage") not in model.STAGES:
        notes.append(f"unknown stage {proj_block.get('stage')!r} -> ASSESSMENT (re-assess; nothing reinterpreted)")
        proj_block["stage"] = "ASSESSMENT"
    if proj_block.get("mode") not in model.MODES:
        notes.append(f"unknown mode {proj_block.get('mode')!r} -> DOCTOR")
        proj_block["mode"] = "DOCTOR"
    proj_block.setdefault("name", proj.root.name)
    proj_block.setdefault("product_type", "unclassified")
    ts = now_iso()
    proj_block.setdefault("created_at", ts)
    proj_block.setdefault("updated_at", ts)
    bp = state.setdefault("blueprint", {})
    bp.setdefault("status", "IN_PROGRESS")
    for s in model.BLUEPRINT_SECTIONS:
        bp.setdefault(s, "NOT_STARTED")
    bp.setdefault("open_founder_decisions", [])
    state.setdefault("execution", {"current_node": None, "next_nodes": []})
    state.setdefault("production", {"readiness": "UNVERIFIED", "last_gate_at": None})
    state.setdefault("documents", {})
    state.setdefault("counts", {})
    state.setdefault("learning", {"project_learnings": 0, "candidates": 0})
    state.setdefault("history", [])
    # file-level: legacy statuses in build graph (mapped explicitly, recorded)
    graph = proj.load_yaml("build-graph.yaml", default=None)
    if graph and graph.get("nodes"):
        changed = 0
        for n in graph["nodes"]:
            if n.get("status") in LEGACY_STATUS:
                n["status"] = LEGACY_STATUS[n["status"]]
                changed += 1
            n.setdefault("depends_on", [])
        if changed:
            notes.append(f"mapped {changed} legacy build-graph status value(s)")
            state.setdefault("_pending_files", {})["build-graph.yaml"] = graph
    return state, notes


MIGRATIONS = {0: m0_to_1}


def main(argv: list[str]) -> int:
    p = cli.parser("migrate_schema.py", "Migrate .raftly/ schema")
    p.add_argument("--check", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)
    proj = cli.project(args)
    if not (proj.forge / "state.yaml").exists():
        raise ForgeError("no .raftly/state.yaml to migrate")
    state = proj.load_yaml("state.yaml") or {}
    legacy_key = "forge" in state and "engine" not in state
    if legacy_key:  # pre-release projects stored version info under "forge"
        state = {"engine": state["forge"], **{k: v for k, v in state.items() if k != "forge"}}
    current = (state.get("engine") or {}).get("schema_version", 0)
    if not isinstance(current, int):
        raise ForgeError(f"schema_version must be an integer, got {current!r}")
    if current > SCHEMA_VERSION:
        raise ForgeError(f"project schema v{current} is newer than this Raftly (v{SCHEMA_VERSION}); upgrade Raftly")
    legacy_dir = proj.legacy_dir
    if args.check:
        need = current < SCHEMA_VERSION or legacy_key or legacy_dir is not None
        cli.emit(args, {"current": current, "target": SCHEMA_VERSION, "migration_needed": need},
                 lambda d: f"schema v{d['current']} -> v{d['target']}: " + ("migration needed" if need else "up to date"))
        return 1 if need else 0
    if current == SCHEMA_VERSION and not legacy_key and legacy_dir is None:
        cli.emit(args, {"current": current, "migrated": False}, lambda d: f"Already at schema v{current}.")
        return 0

    notes_all = []
    version = current
    while version < SCHEMA_VERSION:
        fn = MIGRATIONS.get(version)
        if fn is None:
            raise ForgeError(f"no migration registered from v{version}")
        state, notes = fn(state, proj)
        version += 1
        state["engine"]["schema_version"] = version
        notes_all += [f"v{version - 1}->v{version}: {n}" for n in notes]
    pending = state.pop("_pending_files", {})
    state["engine"]["version"] = FORGE_VERSION
    if legacy_key:
        notes_all.append('renamed the legacy "forge" block to "engine"')
    errors = validate_named(state, "state")
    if errors:
        raise ForgeError("migrated state would be invalid (nothing written):\n  " + "\n  ".join(errors))
    if legacy_dir is not None:
        notes_all.append(f"moved {legacy_dir.name}/ to {FORGE_DIR}/")
    if args.dry_run:
        cli.emit(args, {"from": current, "to": version, "changes": notes_all, "dry_run": True},
                 lambda d: "Would migrate:\n" + "\n".join(f"  - {c}" for c in d["changes"]))
        return 0
    backup = proj.forge / ".backup" / now_iso().replace(":", "")
    backup.mkdir(parents=True, exist_ok=True)
    for f in ["state.yaml", *pending.keys()]:
        if (proj.forge / f).exists():
            shutil.copy2(proj.forge / f, backup / f)
    for fname, data in pending.items():
        proj.save_yaml(fname, data)
    state.setdefault("history", []).append({"at": now_iso(), "event": f"Schema migrated v{current} -> v{version}: "
                                            + "; ".join(notes_all or ["no data changes"])})
    proj.save_yaml("state.yaml", state, schema="state")
    if legacy_dir is not None:
        target = proj.root / FORGE_DIR
        if target.exists():
            raise ForgeError(f"cannot move {legacy_dir.name}/: {FORGE_DIR}/ already exists")
        os.rename(legacy_dir, target)
    cli.emit(args, {"from": current, "to": version, "changes": notes_all, "backup": str(backup)},
             lambda d: f"Migrated v{d['from']} -> v{d['to']} (backup: {d['backup']})\n" + "\n".join(f"  - {c}" for c in d["changes"]))
    return 0


if __name__ == "__main__":
    cli.run(main)
