"""Legal/IP release gate and rebranding, exercised on a temporary copy of the repository."""

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.helpers import REPO


def copy_repo() -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="forge-repo-"))
    dst = tmp / "repo"
    shutil.copytree(REPO, dst, ignore=shutil.ignore_patterns(".git", "__pycache__", "results"))
    return dst


def run(cmd, cwd) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *cmd], cwd=cwd, capture_output=True, text=True)


class LegalGate(unittest.TestCase):
    def setUp(self):
        self.repo = copy_repo()

    def tearDown(self):
        shutil.rmtree(self.repo.parent, ignore_errors=True)

    def check(self, *flags):
        res = run(["scripts/check_release.py", "--json", *flags], self.repo)
        return json.loads(res.stdout), res.returncode

    def test_dev_mode_passes_with_blockers_as_warnings(self):
        data, code = self.check()
        self.assertEqual(code, 0, data["errors"])
        self.assertTrue(any(w.startswith("RELEASE BLOCKER: brand clearance") for w in data["warnings"]))

    def test_release_mode_fails_until_decisions_are_made(self):
        data, code = self.check("--release")
        self.assertEqual(code, 1)
        joined = " ".join(data["errors"])
        for frag in ("brand clearance is PENDING", "third-party license inventory", "install method"):
            self.assertIn(frag, joined)

    def set_gate(self, **fields):
        import re as _re
        gate = self.repo / "legal" / "release-gate.yaml"
        g = gate.read_text()
        for key, value in fields.items():
            g, n = _re.subn(rf"(?m)^(\s*{key}:)\s*[^#\n]*", lambda m, v=value: f"{m.group(1)} {v}  ", g, count=1)
            self.assertEqual(n, 1, key)
        gate.write_text(g)

    def test_accidental_open_source_license_is_refused(self):
        self.set_gate(model="null", spdx="null")
        (self.repo / "LICENSE").write_text("MIT License\n\nPermission is hereby granted, free of charge, to any person ...\n")
        data, code = self.check()
        self.assertEqual(code, 1)
        self.assertTrue(any("no license decision is recorded" in e for e in data["errors"]))

    def test_registered_symbol_is_refused(self):
        readme = self.repo / "README.md"
        readme.write_text(readme.read_text() + "\nForgeAI®\n")
        data, code = self.check()
        self.assertEqual(code, 1)
        self.assertTrue(any("registered-trademark symbol" in e for e in data["errors"]))

    def test_open_source_claim_with_source_available_license(self):
        self.set_gate(model="source-available", spdx="PolyForm-Shield-1.0.0")
        readme = self.repo / "README.md"
        readme.write_text(readme.read_text() + "\nForgeAI is an open-source plugin.\n")
        data, code = self.check()
        self.assertTrue(any("claims" in e and "open" in e for e in data["errors"]))

    def test_release_mode_passes_when_everything_is_resolved(self):
        self.set_gate(legal_owner='"Example Owner"', status="RISK_ACCEPTED_BY_OWNER", owner_reviewed="true",
                      plugin_validate="true", marketplace_install="true", manual_skill_copy="true")
        (self.repo / "LICENSE").write_text("Apache License\nVersion 2.0, January 2004\n(full text)\n\nCopyright 2026 Example Owner\n")
        notice = self.repo / "NOTICE"
        notice.write_text(notice.read_text().replace("[COPYRIGHT HOLDER - TO BE CONFIRMED BY THE REPOSITORY OWNER]", "Example Owner"))
        data, code = self.check("--release")
        self.assertEqual(data["errors"], [])
        self.assertEqual(code, 0)


class Rebrand(unittest.TestCase):
    def setUp(self):
        self.repo = copy_repo()

    def tearDown(self):
        shutil.rmtree(self.repo.parent, ignore_errors=True)

    def test_dry_run_changes_nothing(self):
        before = (self.repo / ".claude-plugin/plugin.json").read_text()
        res = run(["scripts/rebrand.py", "--display-name", "Anvil", "--plugin-name", "anvil"], self.repo)
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("Dry run", res.stdout)
        self.assertEqual((self.repo / ".claude-plugin/plugin.json").read_text(), before)

    def test_apply_full_rebrand_keeps_repo_consistent(self):
        state_before = (self.repo / "examples/calculator/.raftly/state.yaml").read_text()
        changelog_before = (self.repo / "CHANGELOG.md").read_text()
        res = run(["scripts/rebrand.py", "--display-name", "Anvil", "--plugin-name", "anvil", "--marketplace-name", "anvil",
                   "--skill-command", "anvil", "--repository-name", "anvil", "--apply", "--replace-text"], self.repo)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        plugin = json.loads((self.repo / ".claude-plugin/plugin.json").read_text())
        self.assertEqual((plugin["name"], plugin["displayName"]), ("anvil", "Anvil"))
        self.assertTrue((self.repo / "skills/anvil/SKILL.md").exists())
        self.assertFalse((self.repo / "skills/raftly").exists())
        self.assertIn("name: anvil", (self.repo / "skills/anvil/SKILL.md").read_text())
        readme = (self.repo / "README.md").read_text()
        self.assertIn("/plugin install anvil@anvil", readme)
        self.assertIn("/anvil:anvil", readme)
        self.assertNotRegex(readme, r"\bRaftly\b")  # old display name fully replaced
        self.assertIn("cp -R anvil/skills/anvil ~/.claude/skills/anvil", readme)
        self.assertIn(".anvil/", readme)  # project folder follows the command
        self.assertFalse((self.repo / "examples/calculator/.raftly").exists())
        self.assertEqual((self.repo / "examples/calculator/.anvil/state.yaml").read_text(), state_before)
        self.assertRegex((self.repo / "skills/anvil/core/brand.yaml").read_text(), r"(?m)^legacy_state_dirs: \[\.forge, \.raftly\]")
        self.assertTrue((self.repo / "agents/anvil-security-reviewer.md").exists())
        self.assertEqual((self.repo / "CHANGELOG.md").read_text(), changelog_before)
        brand = (self.repo / "skills/anvil/core/brand.yaml").read_text()
        self.assertRegex(brand, r"(?m)^status: PROVISIONAL")
        self.assertRegex(brand, r"(?m)^skill_command: anvil")
        check = run(["scripts/check_release.py", "--json"], self.repo)
        self.assertEqual(json.loads(check.stdout)["errors"], [])
        ctx = run(["skills/anvil/scripts/engine.py", "context", "--root", "examples/calculator"], self.repo)
        self.assertEqual(ctx.returncode, 0, ctx.stderr)
        self.assertTrue(re.match(r"Anvil \d+\.\d+\.\d+ context", ctx.stdout))
        ci = (self.repo / ".github/workflows/ci.yml").read_text()
        self.assertNotIn("skills/raftly/", ci)
        self.assertIn("skills/anvil/scripts/engine.py", ci)
        grade = run(["evals/grade.py", "--examples"], self.repo)
        self.assertEqual(grade.returncode, 0, grade.stdout[-500:])

    def test_invalid_names_rejected(self):
        res = run(["scripts/rebrand.py", "--plugin-name", "Bad Name", "--apply"], self.repo)
        self.assertNotEqual(res.returncode, 0)


if __name__ == "__main__":
    unittest.main()
