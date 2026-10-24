#!/usr/bin/env python3
"""Release-readiness checks for the Raftly repository itself (used in CI).

Checks:
  - plugin.json and marketplace.json are valid and consistent (name, version, ./ source)
  - skills/raftly/SKILL.md frontmatter uses only documented Claude Code fields; size limits
  - every reference/example link in SKILL.md exists, and every reference file is linked
  - JSON schemas parse; core catalogs parse and use known applicability terms
  - scripts have a shebang and are executable
  - no secrets, private keys or local absolute paths in tracked text files
  - shipped examples validate and pass the Blueprint Completion Gate
  - version strings agree (plugin.json, forgelib, SKILL.md metadata, CHANGELOG)
  - brand identifiers agree with skills/<cmd>/core/brand.yaml
  - legal/IP: no accidental license grant before a decision, no "®", no "open source" claims for a non-OSI license,
    and (with --release) every blocker in legal/release-gate.yaml resolved

  check_release.py [--json] [--release]
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_brand_files = sorted((ROOT / "skills").glob("*/core/brand.yaml"))
SKILL = _brand_files[0].parents[1] if _brand_files else ROOT / "skills" / "raftly"
sys.path.insert(0, str(SKILL / "scripts"))

from forgelib import FORGE_VERSION, yamlio  # noqa: E402
from forgelib import gate as gatelib  # noqa: E402
from forgelib.checks import blueprint_gaps, validate  # noqa: E402
from forgelib.brand import brand as load_brand  # noqa: E402
from forgelib.project import Project, parse_frontmatter  # noqa: E402

OSS_LICENSE_MARKERS = ("Permission is hereby granted, free of charge", "Apache License", "GNU GENERAL PUBLIC LICENSE",
                       "GNU AFFERO GENERAL PUBLIC LICENSE", "Mozilla Public License", "Redistribution and use in source and binary forms")
OSI_SPDX = {"Apache-2.0", "MIT", "BSD-2-Clause", "BSD-3-Clause", "MPL-2.0", "GPL-3.0-only", "GPL-3.0-or-later",
            "AGPL-3.0-only", "AGPL-3.0-or-later", "LGPL-3.0-only", "ISC"}
OPEN_SOURCE_CLAIM_RE = re.compile(r"\b(?:is|an?|as)\s+open[- ]source\b", re.I)
PLACEHOLDER_OWNER = "TO BE CONFIRMED"

# Documented SKILL.md frontmatter fields (code.claude.com/docs/en/skills, verified 2026-10-24).
SKILL_FIELDS = {
    "name", "description", "when_to_use", "argument-hint", "arguments", "disable-model-invocation", "user-invocable",
    "allowed-tools", "disallowed-tools", "model", "effort", "context", "agent", "background", "hooks", "paths", "shell",
    "metadata", "license", "compatibility",
}
AGENT_FIELDS = {"name", "description", "tools", "disallowedTools", "model", "permissionMode", "skills", "hooks", "color", "effort", "maxTurns", "memory", "isolation"}
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "results", ".backup"}
TEXT_EXT = {".md", ".py", ".json", ".yaml", ".yml", ".css", ".html", ".txt", ".sh", ".jsx", ".js", ".toml", ".cfg"}
SECRET_RES = [
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"\bsk-(?:ant-)?[A-Za-z0-9_]{20,}"),
    re.compile(r"\bghp_[A-Za-z0-9]{36}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}"),
]
LOCAL_PATH_RE = re.compile(r"/Users/[A-Za-z0-9._-]+/|/home/[A-Za-z0-9._-]+/|[A-Z]:\\Users\\")
# Files that legitimately mention these patterns (the detectors themselves and their tests).
ALLOW_PATTERN_FILES = {"scripts/check_release.py", "skills/raftly/scripts/forgelib/learning.py", "tests/test_gate_learning.py",
                       "tests/test_cli_workflow.py", "tests/test_release.py", "tests/test_legal_brand.py"}


def tracked_files() -> list[Path]:
    out = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            p = Path(dirpath) / f
            if p.suffix in TEXT_EXT or f in ("LICENSE",):
                out.append(p)
    return sorted(out)


def legal_checks(errors: list[str], warnings: list[str], release: bool) -> None:
    """Legal/IP checks (distribution/IP/legal handoff §25–§27, §34)."""
    from forgelib import yamlio as _y

    blockers: list[str] = []
    gate_path = ROOT / "legal" / "release-gate.yaml"
    gate = _y.load_file(gate_path) if gate_path.exists() else None
    if gate is None:
        errors.append("legal/release-gate.yaml missing")
        return
    lic = gate.get("license") or {}
    license_text = (ROOT / "LICENSE").read_text() if (ROOT / "LICENSE").exists() else ""
    looks_oss = any(m in license_text for m in OSS_LICENSE_MARKERS)
    if not lic.get("spdx") and looks_oss:
        errors.append("LICENSE contains an open-source license text but no license decision is recorded in "
                      "legal/release-gate.yaml (risk of granting broader rights than intended)")
    plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
    if plugin.get("license") and plugin.get("license") != lic.get("spdx"):
        errors.append(f"plugin.json license {plugin.get('license')!r} does not match the recorded decision {lic.get('spdx')!r}")
    fm, _ = parse_frontmatter((SKILL / "SKILL.md").read_text())
    if fm.get("license") and fm.get("license") != lic.get("spdx"):
        errors.append(f"SKILL.md license {fm.get('license')!r} does not match the recorded decision {lic.get('spdx')!r}")
    if lic.get("spdx") and lic.get("spdx") not in OSI_SPDX or lic.get("model") in ("source-available", "proprietary"):
        for doc in ("README.md", "CONTRIBUTING.md", ".claude-plugin/plugin.json", ".claude-plugin/marketplace.json"):
            t = (ROOT / doc).read_text()
            m = OPEN_SOURCE_CLAIM_RE.search(t)
            if m:
                errors.append(f"{doc}: claims '{m.group(0)}' but the license is not an OSI open-source license")
    if not gate.get("legal_owner"):
        blockers.append("legal owner (copyright holder) not identified")
    for f in ("LICENSE", "NOTICE"):
        if PLACEHOLDER_OWNER in ((ROOT / f).read_text() if (ROOT / f).exists() else ""):
            blockers.append(f"{f} still has the placeholder copyright holder")
    if not lic.get("spdx") or not lic.get("model"):
        blockers.append("license not chosen (docs/LICENSING_STRATEGY.md)")
    elif lic.get("model") != "open-source" and not lic.get("legal_review"):
        blockers.append("non-open-source/dual license requires legal review before release")
    elif lic.get("spdx") and not looks_oss and lic.get("model") == "open-source" and lic["spdx"] in OSI_SPDX:
        blockers.append(f"LICENSE file does not contain the {lic['spdx']} text")
    bc = (gate.get("brand_clearance") or {}).get("status")
    if bc not in ("CLEARED_BY_COUNSEL", "RENAMED_AND_CLEARED", "RISK_ACCEPTED_BY_OWNER"):
        blockers.append(f"brand clearance is {bc} (docs/BRAND_CLEARANCE.md)")
    if load_brand().get("status") == "PROVISIONAL" and bc in ("CLEARED_BY_COUNSEL", "RENAMED_AND_CLEARED"):
        warnings.append("brand cleared but skills/*/core/brand.yaml status is still PROVISIONAL")
    tp = gate.get("third_party_review") or {}
    if not (tp.get("inventory_compiled") and tp.get("owner_reviewed")):
        blockers.append("third-party license inventory not reviewed by the owner")
    if not (ROOT / "THIRD_PARTY_NOTICES.md").exists():
        errors.append("THIRD_PARTY_NOTICES.md missing")
    if not gate.get("contributor_policy"):
        blockers.append("contributor policy not chosen (NO_EXTERNAL_CODE | DCO | CLA | ASSIGNMENT)")
    if gate.get("contributor_policy") == "CLA" and not (ROOT / "CLA.md").exists():
        blockers.append("contributor policy CLA chosen but CLA.md missing")
    iv = gate.get("install_verified") or {}
    for k in ("plugin_validate", "marketplace_install", "manual_skill_copy"):
        if not iv.get(k):
            blockers.append(f"install method not verified against current Claude Code: {k}")
    for doc in ("NOTICE", "docs/LICENSING_STRATEGY.md", "docs/BRAND_CLEARANCE.md", "docs/IP_REGISTRATION_CHECKLIST.md", "docs/PROVENANCE.md"):
        if not (ROOT / doc).exists():
            errors.append(f"missing {doc}")
    for b in blockers:
        (errors if release else warnings).append(f"RELEASE BLOCKER: {b}")


def run(release: bool = False) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    rel = lambda p: p.relative_to(ROOT).as_posix()  # noqa: E731
    b = load_brand()

    # manifests
    try:
        plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
        if plugin.get("name") != b["plugin_name"]:
            errors.append(f"plugin.json name must be {b['plugin_name']!r} (brand.yaml)")
        if plugin.get("displayName") and plugin.get("displayName") != b["display_name"]:
            errors.append(f"plugin.json displayName must be {b['display_name']!r} (brand.yaml)")
        if plugin.get("version") != FORGE_VERSION:
            errors.append(f"plugin.json version {plugin.get('version')} != forgelib {FORGE_VERSION}")
        for k in ("description", "author"):
            if not plugin.get(k):
                warnings.append(f"plugin.json missing {k}")
    except (OSError, ValueError) as exc:
        errors.append(f"plugin.json: {exc}")
    try:
        mk = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
        for k in ("name", "owner", "plugins"):
            if k not in mk:
                errors.append(f"marketplace.json missing {k}")
        entry = (mk.get("plugins") or [{}])[0]
        if mk.get("name") != b["marketplace_name"]:
            errors.append(f"marketplace.json name must be {b['marketplace_name']!r} (brand.yaml)")
        if entry.get("name") != b["plugin_name"] or not str(entry.get("source", "")).startswith("./"):
            errors.append(f"marketplace.json plugins[0] must be name {b['plugin_name']!r} with a './' relative source")
    except (OSError, ValueError) as exc:
        errors.append(f"marketplace.json: {exc}")

    # skill
    skill_path = SKILL / "SKILL.md"
    text = skill_path.read_text()
    fm, body = parse_frontmatter(text)
    unknown = set(fm) - SKILL_FIELDS
    if unknown:
        errors.append(f"SKILL.md has undocumented frontmatter fields: {sorted(unknown)}")
    if fm.get("name") != b["skill_command"] or SKILL.name != b["skill_command"]:
        errors.append(f"SKILL.md name and skill directory must both be {b['skill_command']!r} (brand.yaml)")
    desc_len = len(str(fm.get("description", ""))) + len(str(fm.get("when_to_use", "")))
    if desc_len > 1536:
        errors.append(f"description + when_to_use is {desc_len} chars (> 1536 listing limit)")
    if (fm.get("metadata") or {}).get("version") != FORGE_VERSION:
        errors.append("SKILL.md metadata.version must match the plugin version")
    lines = text.count("\n")
    words = len(re.findall(r"\w+", body))
    if lines > 500:
        errors.append(f"SKILL.md has {lines} lines (> 500)")
    if not 1200 <= words <= 3000:
        warnings.append(f"SKILL.md body has {words} words (target ~1,500–2,500)")
    links = set(re.findall(r"\]\(((?:references|examples)/[^)#]*)\)", body))
    for link in sorted(links):
        if not (SKILL / link).exists():
            errors.append(f"SKILL.md links missing file: {link}")
    for ref in sorted((SKILL / "references").glob("*.md")):
        if f"references/{ref.name}" not in links:
            errors.append(f"reference not linked from SKILL.md: {ref.name}")
    for script in re.findall(r"scripts/([a-z_]+\.py)", text):
        if not (SKILL / "scripts" / script).exists():
            errors.append(f"SKILL.md mentions missing script {script}")

    # agents
    for agent in sorted((ROOT / "agents").glob("*.md")):
        afm, abody = parse_frontmatter(agent.read_text())
        if not afm.get("name") or not afm.get("description"):
            errors.append(f"agent {agent.name} needs name and description")
        if set(afm) - AGENT_FIELDS:
            warnings.append(f"agent {agent.name} has unrecognised fields {sorted(set(afm) - AGENT_FIELDS)}")

    # schemas and catalogs
    for s in sorted((SKILL / "schemas").glob("*.json")):
        try:
            json.loads(s.read_text())
        except ValueError as exc:
            errors.append(f"{rel(s)}: {exc}")
    for cat in ("production-gate.yaml", "forgotten-20.yaml"):
        ids = set()
        for c in yamlio.load_file(SKILL / "core" / cat)["checks"]:
            if c["id"] in ids:
                errors.append(f"{cat}: duplicate id {c['id']}")
            ids.add(c["id"])
            try:
                gatelib.applies(c["applies_when"], {})
            except gatelib.GateExpressionError as exc:
                errors.append(f"{cat} {c['id']}: {exc}")
    roles = {r["id"] for r in yamlio.load_file(SKILL / "core/roles.yaml")["roles"]}
    for r in yamlio.load_file(SKILL / "core/roles.yaml")["roles"]:
        if not (SKILL / "references" / r["reference"]).exists():
            errors.append(f"roles.yaml {r['id']}: reference {r['reference']} missing")
    if len(roles) < 20:
        errors.append("roles.yaml should define the full senior role set")

    # scripts
    for py in sorted([*(ROOT / "scripts").glob("*.py"), *(SKILL / "scripts").glob("*.py")]):
        head = py.read_text().splitlines()[0] if py.read_text() else ""
        if not head.startswith("#!/usr/bin/env python3"):
            errors.append(f"{rel(py)} lacks a python3 shebang")
        if not os.access(py, os.X_OK):
            errors.append(f"{rel(py)} is not executable")

    # secrets and local paths
    for f in tracked_files():
        r = rel(f)
        if r in ALLOW_PATTERN_FILES:
            continue
        try:
            content = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for pat in SECRET_RES:
            if pat.search(content):
                errors.append(f"{r}: possible secret ({pat.pattern[:30]}…)")
        if LOCAL_PATH_RE.search(content) and not r.startswith("evals/cases/"):
            errors.append(f"{r}: contains a local absolute path")
        if "\u00ae" in content and r not in ALLOW_PATTERN_FILES:
            errors.append(f"{r}: uses the registered-trademark symbol; never use it without a federal registration")

    # examples
    for ex in ("calculator", "b2b-ai-saas"):
        proj = Project(ROOT / "examples" / ex)
        if not proj.exists:
            errors.append(f"examples/{ex} has no .raftly/")
            continue
        res = validate(proj)
        errors += [f"examples/{ex}: {e}" for e in res["errors"]]
        warnings += [f"examples/{ex}: {w}" for w in res["warnings"]]
        errors += [f"examples/{ex}: blueprint gate: {g}" for g in blueprint_gaps(proj)]
        if not (ROOT / "examples" / ex / "artifacts/blueprint.html").exists():
            errors.append(f"examples/{ex}: rendered blueprint missing")

    # version agreement
    changelog = (ROOT / "CHANGELOG.md").read_text() if (ROOT / "CHANGELOG.md").exists() else ""
    if f"[{FORGE_VERSION}]" not in changelog:
        errors.append(f"CHANGELOG.md has no [{FORGE_VERSION}] entry")
    for required in ("README.md", "LICENSE", "CONTRIBUTING.md", "SECURITY.md", "CHANGELOG.md", "NOTICE", "THIRD_PARTY_NOTICES.md"):
        if not (ROOT / required).exists():
            errors.append(f"missing {required}")
    if not (SKILL / "core" / "CONSTITUTION.md").exists():
        errors.append("missing core/CONSTITUTION.md in the skill")
    legal_checks(errors, warnings, release)
    return {"ok": not errors, "errors": errors, "warnings": warnings, "release_mode": release}


def main(argv: list[str]) -> int:
    res = run(release="--release" in argv)
    if "--json" in argv:
        print(json.dumps(res, indent=2))
    else:
        for e in res["errors"]:
            print(f"ERROR   {e}")
        for w in res["warnings"]:
            print(f"WARNING {w}")
        mode = "PUBLIC RELEASE CHECKS" if res["release_mode"] else "RELEASE CHECKS"
        print(f"{mode} {'PASS' if res['ok'] else 'FAIL'}: {len(res['errors'])} error(s), {len(res['warnings'])} warning(s)")
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
