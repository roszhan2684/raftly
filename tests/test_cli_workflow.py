"""Integration tests: the deterministic engine through the forge.py CLI."""

import json
import os
import unittest

from tests.helpers import REPO, SKILL, ProjectCase
from forgelib import yamlio
from forgelib.fsutil import ForgePathError, assert_not_plugin_core


class InitAndState(ProjectCase):
    def test_init_creates_minimal_files_and_is_idempotent(self):
        self.init()
        files = sorted(p.name for p in (self.tmp / ".raftly").iterdir())
        self.assertEqual(files, ["PROJECT.md", "assumptions.yaml", "build-graph.yaml", "dependencies.yaml",
                                 "evidence.yaml", "requirements.yaml", "risks.yaml", "state.yaml"])
        st = (self.tmp / ".raftly/state.yaml").read_text()
        (self.tmp / ".raftly/PROJECT.md").write_text("# edited by human\n")
        res = self.forge("init", "--name", "Other")
        self.assertIn("Nothing was overwritten", res.out)
        self.assertEqual((self.tmp / ".raftly/state.yaml").read_text(), st)
        self.assertEqual((self.tmp / ".raftly/PROJECT.md").read_text(), "# edited by human\n")

    def test_golden_state(self):
        os.environ["FORGE_NOW"] = "2026-01-15T10:00:00Z"
        self.init("Golden", "surfaces=[web,ios]", "backend=false")
        golden = (REPO / "tests/golden/init-state.yaml").read_text()
        self.assertEqual((self.tmp / ".raftly/state.yaml").read_text(), golden)

    def test_existing_repo_starts_in_assessment(self):
        (self.tmp / "package.json").write_text(json.dumps({"dependencies": {"next": "15.0.0"}}))
        (self.tmp / "app.ts").write_text("export {}\n")
        ctx = self.forge("context", "--json").json()
        self.assertEqual(ctx["repo"]["suggested_mode"], "REVIEW")
        self.assertIn("Do NOT rewrite", ctx["recommendation"])
        self.forge("init", "--name", "Existing", "--mode", "RECOVERY")
        self.assertEqual(self.project().state()["project"]["stage"], "ASSESSMENT")
        self.assertEqual(json.loads((self.tmp / "package.json").read_text()), {"dependencies": {"next": "15.0.0"}})

    def test_stage_rules(self):
        self.init()
        res = self.forge("state", "stage", "BUILDING", ok=False)
        self.assertIn("BLUEPRINT_COMPLETE first", res.err)
        res = self.forge("state", "stage", "BLUEPRINT_COMPLETE", ok=False)
        self.assertIn("Blueprint Completion Gate not met", res.err)
        res = self.forge("state", "set", "project.stage", "LAUNCHED", ok=False)
        self.assertIn("managed", res.err)
        self.forge("state", "stage", "PRODUCT")
        self.forge("state", "event", "Researched competitors")
        hist = self.project().state()["history"]
        self.assertEqual(hist[-1]["event"], "Researched competitors")
        self.assertIn("INTAKE -> PRODUCT", hist[-2]["event"])

    def test_profile_and_founder_decisions(self):
        self.init()
        self.forge("state", "profile", "accounts=true")
        self.assertTrue(self.project().state()["project"]["profile"]["accounts"])
        self.forge("state", "founder-decision", "add", "Pricing: per-seat or usage?")
        self.assertIn("Pricing: per-seat or usage?", self.forge("state", "show").out)
        self.forge("state", "founder-decision", "resolve", "Pricing: per-seat or usage?")
        self.assertEqual(self.project().state()["blueprint"]["open_founder_decisions"], [])


class BuildAndEvidence(ProjectCase):
    def setUp(self):
        super().setUp()
        self.init()
        self.forge("records", "add", "requirement", "--statement", "Evaluate expressions with precedence", "--priority", "MUST")
        self.forge("graph", "add", "--name", "Engine", "--type", "foundation")
        self.forge("graph", "add", "--name", "Keypad UI", "--type", "feature", "--depends", "N001")
        self.forge("records", "new", "feature", "--name", "Engine", "--node", "N001", "--requirements", "REQ-001")
        self.forge("records", "new", "prompt", "--title", "Engine", "--node", "N001")

    def test_links_created(self):
        proj = self.project()
        self.assertEqual(proj.registry("requirements.yaml")[0]["features"], ["F001"])
        node = proj.registry("build-graph.yaml")[0]
        self.assertEqual(node["features"], ["F001"])
        self.assertEqual(node["prompts"], ["001-engine.md"])
        self.assertTrue((self.tmp / ".raftly/prompts/001-engine.md").exists())

    def test_cannot_verify_or_complete_without_evidence(self):
        res = self.forge("graph", "set-status", "N001", "VERIFIED", ok=False)
        self.assertIn("passing verification evidence", res.err)
        res = self.forge("records", "feature-status", "F001", "VERIFIED", ok=False)
        self.assertIn("passing verification evidence", res.err)
        # build/lint evidence is not verification
        self.forge("evidence", "record", "--subject", "F001", "--kind", "build", "--result", "PASS", "--summary", "compiles")
        self.forge("graph", "set-status", "N001", "VERIFIED", ok=False)
        self.forge("evidence", "record", "--subject", "F001", "--kind", "test", "--result", "PASS", "--summary", "unit tests")
        self.forge("graph", "set-status", "N001", "VERIFIED")
        res = self.forge("graph", "set-status", "N001", "COMPLETE", ok=False)
        self.assertIn("features not COMPLETE", res.err)
        self.forge("records", "feature-status", "F001", "VERIFIED")
        res = self.forge("records", "feature-status", "F001", "COMPLETE", ok=False)
        self.assertIn("Definition of Done incomplete", res.err)

    def test_latest_failing_test_revokes_verification(self):
        from forgelib import evidence as ev

        self.forge("evidence", "record", "--subject", "F001", "--kind", "test", "--result", "PASS", "--summary", "ok")
        self.forge("evidence", "record", "--subject", "F001", "--kind", "test", "--result", "FAIL", "--summary", "regression")
        self.assertNotIn("F001", ev.verified_subjects(self.project().evidence()))

    def test_next_and_render(self):
        nxt = self.forge("graph", "next", "--json").json()
        self.assertEqual(nxt["next"][0]["id"], "N001")
        self.assertEqual(nxt["next"][0]["action"], "start")
        self.forge("graph", "render")
        build = (self.tmp / ".raftly/BUILD.md").read_text()
        self.assertIn("<!-- generated:graph:start -->", build)
        self.assertIn("N002 Keypad UI  <- N001", build)
        # rendering twice replaces, not duplicates
        self.forge("graph", "render")
        self.assertEqual((self.tmp / ".raftly/BUILD.md").read_text().count("generated:graph:start"), 1)

    def test_cycle_rejected(self):
        proj = self.project()
        nodes = proj.registry("build-graph.yaml")
        nodes[0]["depends_on"] = ["N002"]
        yamlio.dump_file(self.tmp / ".raftly/build-graph.yaml", {"nodes": nodes})
        res = self.forge("graph", "validate", ok=False)
        self.assertIn("cycle", res.out)
        self.assertNotEqual(self.forge("validate", ok=False).code, 0)

    def test_evidence_queries(self):
        self.forge("evidence", "entity", "--id", "TEST-engine", "--name", "engine.test.ts", "--path", "src/engine.test.ts")
        self.forge("evidence", "link", "TEST-engine", "F001", "--rel", "verifies")
        self.assertIn("REQ-001", self.forge("evidence", "untested").out)
        self.forge("evidence", "record", "--subject", "TEST-engine", "--kind", "test", "--result", "PASS", "--summary", "12 passed")
        self.assertIn("Every active requirement", self.forge("evidence", "untested").out)
        why = self.forge("evidence", "why", "TEST-engine").out
        self.assertIn("F001 (verifies)", why)
        self.assertIn("REQ-001 (justifies)", why)
        impact = self.forge("evidence", "impact", "REQ-001", "--json").json()
        self.assertIn("F001", impact)
        self.assertIn("TEST-engine", impact)
        res = self.forge("evidence", "link", "API-nope", "F001", "--rel", "exposes", ok=False)
        self.assertIn("unknown id", res.err)

    def test_requirement_change_engine(self):
        self.forge("graph", "render")
        rep = self.forge("records", "change-requirement", "REQ-001", "--statement", "Evaluate with precedence and percent",
                         "--reason", "Percent key", "--json").json()
        self.assertEqual(rep["new_requirement"], "REQ-002")
        self.assertEqual(rep["impact"]["product"]["features"], ["F001"])
        self.assertEqual(rep["impact"]["build_graph_nodes"], ["N001"])
        proj = self.project()
        reqs = {r["id"]: r for r in proj.registry("requirements.yaml")}
        self.assertEqual(reqs["REQ-001"]["status"], "SUPERSEDED")
        self.assertEqual(reqs["REQ-001"]["superseded_by"], "REQ-002")
        self.assertEqual(reqs["REQ-002"]["supersedes"], ["REQ-001"])
        _, fm, _ = proj.find_record("feature", "F001")
        self.assertEqual(fm["requirements"], ["REQ-002"])
        self.assertEqual(proj.state()["documents"]["BUILD.md"]["status"], "STALE")
        self.assertEqual(self.forge("validate", "--json", ok=False).json()["errors"], [])


class DecisionsAndOverrides(ProjectCase):
    def setUp(self):
        super().setUp()
        self.init()
        self.forge("decisions", "new", "--title", "Use PostgreSQL", "--owner", "data", "--type", "RECOMMEND", "--impact", "high",
                   "--reversibility", "low", "--confidence", "80", "--revisit", "Document-shaped data dominates")

    def test_unknown_role_rejected(self):
        res = self.forge("decisions", "new", "--title", "X", "--owner", "ninja", "--type", "AUTO", "--impact", "low",
                         "--reversibility", "high", "--confidence", "90", ok=False)
        self.assertIn("unknown owner role", res.err)

    def test_override_records_recommendation_and_choice(self):
        # Demo D: "Use MongoDB instead of PostgreSQL."
        self.forge("decisions", "override", "ADR-001", "--chosen", "MongoDB", "--reason", "Team knows MongoDB",
                   "--consequences", "Lose relational integrity; tenant isolation must be enforced in app code.")
        proj = self.project()
        _, old, _ = proj.find_record("decision", "ADR-001")
        _, new, body = proj.find_record("decision", "ADR-002")
        self.assertEqual(old["status"], "SUPERSEDED")
        self.assertEqual(old["superseded_by"], "ADR-002")
        self.assertEqual(new["decision_type"], "FOUNDER")
        self.assertEqual(new["override"]["chosen"], "MongoDB")
        self.assertEqual(new["override"]["reason"], "Team knows MongoDB")
        self.assertIn("relational integrity", new["override"]["consequences"])
        self.assertIn("will not re-argue", body)
        book = (self.tmp / ".raftly/DECISIONS.md").read_text()
        self.assertIn("founder override", book)
        self.assertIn("SUPERSEDED → ADR-002", book)
        self.assertIn("Founder override", proj.state()["history"][-1]["event"] if "Founder" in proj.state()["history"][-1]["event"]
                      else proj.state()["history"][-2]["event"])
        res = self.forge("decisions", "override", "ADR-001", "--chosen", "DynamoDB", "--reason", "x", ok=False)
        self.assertIn("already superseded", res.err)

    def test_type1_accept_requires_revisit_trigger(self):
        self.forge("decisions", "new", "--title", "Monolith", "--owner", "architect", "--type", "RECOMMEND", "--impact", "high",
                   "--reversibility", "medium", "--confidence", "70", "--status", "PROPOSED")
        res = self.forge("decisions", "status", "ADR-002", "ACCEPTED", ok=False)
        self.assertIn("revisit_trigger", res.err)


class GateCLI(ProjectCase):
    def test_gate_requires_evidence_and_reports(self):
        self.init("Calc", "surfaces=[web,ios,android]", "backend=false")
        self.forge("gate", "init")
        gate = self.project().gate()
        na = {c["id"] for c in gate["checks"] if c["status"] == "NOT_APPLICABLE"}
        self.assertIn("G-BACKUPS", na)
        res = self.forge("gate", "set", "G-TEST-AUTOMATED", "PASS", ok=False)
        self.assertIn("no evidence, no PASS", res.err)
        self.forge("graph", "add", "--name", "Engine", "--type", "foundation")
        self.forge("evidence", "record", "--subject", "G-TEST-AUTOMATED", "--kind", "test", "--result", "FAIL", "--summary", "2 failing")
        res = self.forge("gate", "set", "G-TEST-AUTOMATED", "PASS", "--evidence", "EV-001", ok=False)
        self.assertIn("failing evidence", res.err)
        self.forge("gate", "set", "G-TEST-AUTOMATED", "FAIL", "--evidence", "EV-001")
        rep = self.forge("gate", "report", "--write").out
        self.assertIn("NOT_READY", rep)
        st = self.project().state()
        self.assertEqual(st["production"]["readiness"], "NOT_READY")
        self.assertIn("generated:gate:start", (self.tmp / ".raftly/LAUNCH.md").read_text())
        res = self.forge("gate", "set", "G-ROLLBACK", "NOT_APPLICABLE", "--na-reason", "no server", ok=False)
        self.assertIn("citing a decision", res.err)


class LearningCLI(ProjectCase):
    def test_preference_stays_project_only_and_core_untouched(self):
        self.init()
        before = sorted(p.as_posix() for p in (SKILL / "core").rglob("*"))
        res = self.forge("learning", "record", "--title", "I hate rounded UI buttons", "--kind", "preference",
                         "--quality", "anecdotal", "--authority", "user", "--json").json()
        self.assertEqual(res["outcome"], "PROJECT_ONLY")
        self.assertNotIn("candidate", res)
        self.assertEqual(sorted(p.as_posix() for p in (SKILL / "core").rglob("*")), before)
        self.assertFalse((self.tmp / ".raftly/learning-candidates").exists())

    def test_core_proposal_is_sanitized_and_local(self):
        self.init("Acme Billing")
        res = self.forge("learning", "record", "--title", "Float money rounding", "--kind", "engineering_failure",
                         "--quality", "tested", "--authority", "official_docs", "--repeats", "2", "--cross-project",
                         "--objective", "--json").json()
        self.assertEqual(res["outcome"], "CORE_PROPOSAL")
        bad = self.forge("learning", "propose", "LC-001", "--pattern", "Acme Billing lost cents in /Users/x/acme",
                         "--rule", "Use integers", ok=False)
        self.assertIn("project-private", bad.err)
        ok = self.forge("learning", "propose", "LC-001", "--pattern", "Binary floating point loses cents in money math",
                        "--rule", "Store money as integer minor units or decimal types",
                        "--source", "https://docs.python.org/3/tutorial/floatingpoint.html", "--json").json()
        self.assertTrue(ok["proposal"].startswith(str(self.tmp.resolve())))

    def test_plugin_core_write_guard(self):
        with self.assertRaises(ForgePathError):
            assert_not_plugin_core(SKILL / "core" / "CONSTITUTION.md")
        with self.assertRaises(ForgePathError):
            assert_not_plugin_core(SKILL / "SKILL.md")
        with self.assertRaises(ForgePathError):
            assert_not_plugin_core(REPO / ".claude-plugin" / "plugin.json")
        with self.assertRaises(ForgePathError):
            assert_not_plugin_core(REPO / "agents" / "x.md")
        assert_not_plugin_core(self.tmp / ".raftly" / "x.md")
        assert_not_plugin_core(REPO / "examples" / "calculator" / "artifacts" / "x.html")


class Migration(ProjectCase):
    def test_v0_to_v1(self):
        (self.tmp / ".raftly").mkdir()
        (self.tmp / ".raftly/state.yaml").write_text("project:\n  name: Legacy\n  phase: building\n  mode: BUILD\nhistory:\n  - at: '2025-01-01T00:00:00Z'\n    event: old event\n")
        (self.tmp / ".raftly/build-graph.yaml").write_text("nodes:\n  - id: N001\n    name: A\n    type: feature\n    status: DONE\n")
        self.assertEqual(self.forge("migrate", "--check", ok=False).code, 1)
        dry = self.forge("migrate", "--dry-run").out
        self.assertIn("phase -> project.stage", dry)
        self.assertFalse((self.tmp / ".raftly/.backup").exists())
        self.forge("migrate")
        st = self.project().state()
        self.assertEqual(st["engine"]["schema_version"], 1)
        self.assertEqual(st["project"]["stage"], "BUILDING")
        self.assertEqual(st["history"][0]["event"], "old event")  # history preserved
        self.assertIn("Schema migrated", st["history"][-1]["event"])
        self.assertEqual(self.project().registry("build-graph.yaml")[0]["status"], "COMPLETE")
        self.assertTrue(any((self.tmp / ".raftly/.backup").rglob("state.yaml")))
        self.assertEqual(self.forge("migrate", "--check").code, 0)


class LegacyStateDir(ProjectCase):
    def test_legacy_forge_folder_is_read_and_migrated(self):
        # a project created before the rename: .forge/ folder and a "forge:" version block
        self.init()
        from forgelib.project import FORGE_DIR

        current = self.tmp / FORGE_DIR
        legacy = self.tmp / ".forge"
        current.rename(legacy)
        state = (legacy / "state.yaml").read_text().replace("engine:\n", "forge:\n")
        (legacy / "state.yaml").write_text(state)
        ctx = self.forge("context", "--json").json()
        self.assertTrue(ctx["state"]["needs_migration"])
        self.assertEqual(ctx["state"]["legacy_dir"], ".forge")
        self.assertIn("migrat", ctx["recommendation"])
        self.assertEqual(self.forge("migrate", "--check", ok=False).code, 1)
        dry = self.forge("migrate", "--dry-run").out
        self.assertIn(f"moved .forge/ to {FORGE_DIR}/", dry)
        self.assertTrue(legacy.exists())
        self.forge("migrate")
        self.assertFalse(legacy.exists())
        st = self.project().state()
        self.assertIn("engine", st)
        self.assertNotIn("forge", st)
        self.assertEqual(self.forge("validate", "--json").json()["errors"], [])


class Validation(ProjectCase):
    def test_detects_integrity_problems(self):
        self.init()
        self.forge("graph", "add", "--name", "Engine", "--type", "foundation")
        proj = self.project()
        nodes = proj.registry("build-graph.yaml")
        nodes[0]["status"] = "COMPLETE"
        nodes[0]["features"] = ["F009"]
        yamlio.dump_file(self.tmp / ".raftly/build-graph.yaml", {"nodes": nodes})
        (self.tmp / ".raftly/SECURITY.md").write_text("# Security\n\nThe app is HIPAA compliant and 100% secure.\nIt is not HIPAA compliant yet.\n")
        res = self.forge("validate", "--json", ok=False).json()
        errs = " ".join(res["errors"])
        self.assertIn("unknown feature F009", errs)
        self.assertIn("without passing verification evidence", errs)
        warns = " ".join(res["warnings"])
        self.assertIn("HIPAA compliant", warns)
        self.assertIn("100% secure", warns)
        self.assertEqual(sum("HIPAA compliant" in w for w in res["warnings"]), 1)  # negated claim not flagged


class DoctorAndRender(ProjectCase):
    def test_doctor_no_change(self):
        self.init()
        d = self.forge("doctor", "--json").json()
        self.assertIn(d["verdict"], ("No change recommended.", "Address the issues in severity order; do not create work beyond them."))

    def test_renderers(self):
        self.init()
        self.forge("graph", "add", "--name", "Engine", "--type", "foundation")
        self.forge("blueprint")
        page = (self.tmp / "artifacts/blueprint.html").read_text()
        self.assertIn("<svg", page)
        self.forge("deck", "--kind", "launch")
        self.assertTrue((self.tmp / "artifacts/launch-deck.md").exists())
        self.forge("handoff")
        self.assertIn("## Dangerous areas", (self.tmp / ".raftly/HANDOFF.md").read_text())


if __name__ == "__main__":
    unittest.main()
