#!/usr/bin/env python3
"""Change the public brand (name, plugin id, slash command, project folder) in one step.

Maintainer tool for this repository (not used by the skill at runtime). Dry run by default.

  rebrand.py --display-name "Anvil" --command anvil [--plugin-name anvil] [--marketplace-name anvil]
             [--short-name Anvil] [--repository-name anvil] [--package-name anvil] [--state-dir .anvil]
             [--apply] [--replace-text]

With --apply:
  - updates skills/<cmd>/core/brand.yaml (old state dir is added to legacy_state_dirs so existing projects still load)
  - updates .claude-plugin/plugin.json and marketplace.json
  - renames skills/<old-cmd>/ -> skills/<new-cmd>/, the SKILL.md `name`, and agent files <old-cmd>-*.md -> <new-cmd>-*.md
  - rewrites skill paths (skills/<old-cmd>/) in CI, tests, evals, scripts and docs
  - renames example project folders (examples/*/<old-state-dir>/)
With --replace-text, also rewrites names in human-facing text and code strings:
  display name, short name, "/<plugin>:<cmd>", "<plugin>@<marketplace>", "/<cmd>", the "<cmd> <subcommand>" alias,
  "<cmd>-*-reviewer" agent names, the "<state-dir>/" folder name, and OWNER/<repo>.
  History stays as it is: docs/BRAND_CLEARANCE.md, docs/specs/, legal/release-gate.yaml and CHANGELOG.md.

Brand-neutral internals never change: scripts/engine.py, the "engine" block in state.yaml, the forgelib package, role ids.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_GLOBS = ["README.md", "CONTRIBUTING.md", "SECURITY.md", "NOTICE", "THIRD_PARTY_NOTICES.md", "CODE_OF_CONDUCT.md",
              "docs/*.md", "agents/*.md", "evals/*.md", "evals/*.py", "evals/evals.json", "evals/cases/**/*.md",
              "evals/cases/**/*.yaml", "evals/cases/**/*.sh", "examples/README.md", "examples/*/README.md",
              "examples/*/STATE/**/*.md", "examples/*/STATE/**/*.yaml", "examples/*/STATE/**/*.json",
              "skills/CMD/**/*.md", "skills/CMD/**/*.yaml", "skills/CMD/**/*.py", "skills/CMD/**/*.json", "skills/CMD/**/*.css",
              "scripts/check_release.py", "tests/*.py", "tests/golden/*", ".github/**/*.yml", ".github/**/*.md",
              "legal/README.md", "pyproject.toml", ".claude-plugin/*.json"]
PATH_GLOBS = [".github/workflows/*.yml", "tests/*.py", "evals/*.py", "evals/*.md", "scripts/*.py", "pyproject.toml",
              "README.md", "CONTRIBUTING.md", "SECURITY.md", "NOTICE", "THIRD_PARTY_NOTICES.md", "docs/*.md", "legal/*.md",
              "examples/README.md", "examples/*/README.md"]
SKIP = {"docs/BRAND_CLEARANCE.md", "scripts/rebrand.py", "CHANGELOG.md"}
SKIP_PREFIX = ("docs/specs/", "legal/release-gate.yaml")
SUBCOMMANDS = ("context", "doctor", "init", "state", "records", "decisions", "graph", "evidence", "gate", "learning",
               "blueprint", "deck", "handoff", "validate", "migrate", "inspect", "version")
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def find_skill_dir(root: Path) -> Path:
    dirs = [p.parent.parent for p in (root / "skills").glob("*/core/brand.yaml")]
    if len(dirs) != 1:
        raise SystemExit(f"expected exactly one skills/*/core/brand.yaml, found {len(dirs)}")
    return dirs[0]


def load_brand(skill: Path) -> dict:
    sys.path.insert(0, str(skill / "scripts"))
    from forgelib import yamlio  # noqa: E402

    return yamlio.load_file(skill / "core" / "brand.yaml")


def write_brand(path: Path, brand: dict) -> None:
    text = path.read_text()
    for key, value in brand.items():
        rendered = "[" + ", ".join(value) + "]" if isinstance(value, list) else str(value)
        text, n = re.subn(rf"^({re.escape(key)}:[ \t]*)(\[[^\]]*\]|\S+)", lambda m, v=rendered: f"{m.group(1)}{v}", text,
                          count=1, flags=re.M)
        if not n:
            text += f"{key}: {rendered}\n"
    path.write_text(text)


def expand(root: Path, globs: list[str], cmd: str, state_dir: str) -> list[Path]:
    out = set()
    for g in globs:
        g = g.replace("CMD", cmd).replace("STATE", state_dir)
        for p in root.glob(g):
            rel = p.relative_to(root).as_posix()
            if p.is_file() and rel not in SKIP and not rel.startswith(SKIP_PREFIX) and not rel.endswith("core/brand.yaml"):
                out.add(p)
    return sorted(out)


def text_rules(old: dict, new: dict) -> list[tuple[re.Pattern, str]]:
    oc, nc = old["skill_command"], new["skill_command"]
    rules = [
        (re.compile(rf"/{re.escape(old['plugin_name'])}:{re.escape(oc)}\b"), f"/{new['plugin_name']}:{nc}"),
        (re.compile(rf"\b{re.escape(old['plugin_name'])}@{re.escape(old['marketplace_name'])}\b"),
         f"{new['plugin_name']}@{new['marketplace_name']}"),
        (re.compile(rf"(github\.com/[\w.-]+/|\.github\.io/|marketplace add [\w.-]+/|--marketplace [\w.-]+/|OWNER/){re.escape(old['repository_name'])}\b"),
         rf"\g<1>{new['repository_name']}"),
        (re.compile(rf"\b{re.escape(old['repository_name'])}/skills/"), f"{new['repository_name']}/skills/"),
        (re.compile(rf"--plugin-dir \./{re.escape(old['repository_name'])}\b"), f"--plugin-dir ./{new['repository_name']}"),
        (re.compile(rf"/{re.escape(old['repository_name'])}\.git\b"), f"/{new['repository_name']}.git"),
        (re.compile(rf"\b{re.escape(oc)}-(security|quality|launch)-reviewer\b"), rf"{nc}-\1-reviewer"),
        (re.compile(rf"(?<![\w./:-])/{re.escape(oc)}\b(?![/\w-])"), f"/{nc}"),
        (re.compile(rf"\b{re.escape(oc)} (?=(?:{'|'.join(SUBCOMMANDS)})\b)"), f"{nc} "),
        (re.compile(rf"`{re.escape(oc)}`"), f"`{nc}`"),
        (re.compile(rf"`{re.escape(oc)} "), f"`{nc} "),
        (re.compile(r"(?<![\w)\]])" + re.escape(old["state_dir"]) + r"\b"), new["state_dir"]),
        (re.compile(rf"\b{re.escape(old['display_name'])}\b"), new["display_name"]),
    ]
    if old["artifact_brand"] != old["display_name"]:
        rules.append((re.compile(rf"\b{re.escape(old['artifact_brand'])}\b"), new["artifact_brand"]))
    rules.append((re.compile(rf"\b{re.escape(old['short_name'])}\b"), new["short_name"]))
    rules.append((re.compile(rf"\b{re.escape(old['plugin_name'])}\b(?![./-])"), new["plugin_name"]))
    return rules


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--display-name")
    p.add_argument("--command", "--skill-command", dest="skill_command")
    for key in ("plugin-name", "marketplace-name", "short-name", "artifact-brand", "repository-name", "package-name", "state-dir"):
        p.add_argument(f"--{key}")
    p.add_argument("--root", default=str(ROOT))
    p.add_argument("--apply", action="store_true")
    p.add_argument("--replace-text", action="store_true")
    args = p.parse_args(argv)
    root = Path(args.root).resolve()
    skill = find_skill_dir(root)
    old = load_brand(skill)
    old.setdefault("short_name", old["display_name"])
    old.setdefault("state_dir", f".{old['skill_command']}")
    old["legacy_state_dirs"] = list(old.get("legacy_state_dirs") or [])
    new = dict(old)
    for key in ("display_name", "skill_command", "plugin_name", "marketplace_name", "short_name", "artifact_brand",
                "repository_name", "package_name", "state_dir"):
        val = getattr(args, key, None)
        if val:
            new[key] = val
    if args.display_name:
        new["artifact_brand"] = args.artifact_brand or args.display_name
        new["short_name"] = args.short_name or args.display_name
    if args.skill_command and not args.state_dir:
        new["state_dir"] = f".{args.skill_command}"
    for key in ("plugin_name", "marketplace_name", "skill_command", "repository_name", "package_name"):
        if not NAME_RE.match(str(new[key])):
            raise SystemExit(f"{key} must be lowercase kebab-case: {new[key]!r}")
    if not re.match(r"^\.[a-z0-9][a-z0-9-]*$", new["state_dir"]):
        raise SystemExit(f"state_dir must look like .name: {new['state_dir']!r}")
    if new["state_dir"] != old["state_dir"]:
        new["legacy_state_dirs"] = list(dict.fromkeys([*old["legacy_state_dirs"], old["state_dir"]]))
    changed = {k: (old.get(k), new[k]) for k in new if old.get(k) != new[k]}
    if not changed:
        print("Nothing to change.")
        return 0
    print("Brand changes:")
    for k, (a, b) in changed.items():
        print(f"  {k}: {a} -> {b}")
    rules = text_rules(old, new)
    hits = []
    for f in expand(root, TEXT_GLOBS, old["skill_command"], old["state_dir"]):
        s = f.read_text(errors="ignore")
        n = sum(len(r.findall(s)) for r, _ in rules)
        if n:
            hits.append((f, n))
    print(f"Text occurrences ({'will be replaced' if args.replace_text else 'pass --replace-text to rewrite'}): "
          f"{sum(n for _, n in hits)} in {len(hits)} files")
    for f, n in hits[:60]:
        print(f"  {f.relative_to(root)}: {n}")
    if not args.apply:
        print("Dry run. Re-run with --apply (and usually --replace-text).")
        return 0

    if args.replace_text:
        for f, _ in hits:
            s = f.read_text()
            for r, repl in rules:
                s = r.sub(repl, s)
            f.write_text(s)
    oc, nc = old["skill_command"], new["skill_command"]
    if oc != nc:
        path_re = re.compile(rf'skills(/|" / "){re.escape(oc)}\b')
        for f in expand(root, PATH_GLOBS, oc, old["state_dir"]):
            t = f.read_text()
            t2 = path_re.sub(lambda m: f"skills{m.group(1)}{nc}", t)
            if t2 != t:
                f.write_text(t2)
        for agent in sorted((root / "agents").glob(f"{oc}-*.md")):
            agent.rename(agent.with_name(nc + agent.name[len(oc):]))
    if new["state_dir"] != old["state_dir"]:
        for d in sorted(root.glob(f"examples/*/{old['state_dir']}")):
            target = d.with_name(new["state_dir"])
            if target.exists():
                raise SystemExit(f"{target} already exists")
            d.rename(target)
    write_brand(skill / "core" / "brand.yaml", {k: new[k] for k in new if k != "status"})
    pj = root / ".claude-plugin" / "plugin.json"
    plugin = json.loads(pj.read_text())
    plugin["name"], plugin["displayName"] = new["plugin_name"], new["display_name"]
    pj.write_text(json.dumps(plugin, indent=2, ensure_ascii=False) + "\n")
    mj = root / ".claude-plugin" / "marketplace.json"
    market = json.loads(mj.read_text())
    market["name"] = new["marketplace_name"]
    market["plugins"][0]["name"] = new["plugin_name"]
    mj.write_text(json.dumps(market, indent=2, ensure_ascii=False) + "\n")
    skill_md = skill / "SKILL.md"
    skill_md.write_text(re.sub(r"^name:\s*\S+", f"name: {nc}", skill_md.read_text(), count=1, flags=re.M))
    if oc != nc:
        target = skill.parent / nc
        if target.exists():
            raise SystemExit(f"{target} already exists")
        shutil.move(str(skill), str(target))
        print(f"Renamed {skill.relative_to(root)} -> {target.relative_to(root)}")
    print("Applied. Next: run the tests and scripts/check_release.py, re-render the example artifacts, add a CHANGELOG entry, "
          "update docs/BRAND_CLEARANCE.md, and keep brand status PROVISIONAL until clearance is complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
