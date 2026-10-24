import unittest

from tests.helpers import REPO  # noqa: F401
from forgelib import gate as g
from forgelib import learning as lf

CALCULATOR = {"surfaces": ["web", "ios", "android"], "backend": False}
B2B = {"surfaces": ["web"], "backend": True, "accounts": True, "personal_data": True, "multi_tenant": True, "ai": True,
       "payments": True, "email": True, "integrations": True, "file_uploads": True, "public_site": True, "analytics": True,
       "sensitive_data": ["credentials"]}
HEALTH = {"surfaces": ["web"], "backend": True, "accounts": True, "personal_data": True, "sensitive_data": ["phi"], "regulated": ["HIPAA"]}


class Applicability(unittest.TestCase):
    def test_expressions(self):
        self.assertTrue(g.applies("always", {}))
        self.assertTrue(g.applies("backend and accounts", {"backend": True, "accounts": True}))
        self.assertFalse(g.applies("backend and accounts", {"backend": True}))
        self.assertTrue(g.applies("payments or integrations", {"integrations": True}))
        self.assertTrue(g.applies("ui and not backend", CALCULATOR))
        self.assertTrue(g.applies("surface:ios", CALCULATOR))
        self.assertTrue(g.applies("sensitive:phi", HEALTH))
        self.assertTrue(g.applies("regulated:hipaa", HEALTH))
        self.assertTrue(g.applies("sensitive:any", HEALTH))
        with self.assertRaises(g.GateExpressionError):
            g.applies("kubernetes", {})

    def test_calculator_is_not_penalised_for_missing_server(self):
        checks = g.instantiate(CALCULATOR)
        status = {c["id"]: c["status"] for c in checks}
        for server_check in ("G-BACKUPS", "G-AUTH", "G-AUTHZ-SERVER", "G-TENANT-ISOLATION", "G-SEC-RATE",
                             "G-MONITORING", "G-BILLING", "G-DATA-MIGRATIONS", "G-COMPLIANCE-READINESS"):
            self.assertEqual(status[server_check], "NOT_APPLICABLE", server_check)
        for applies in ("G-TEST-AUTOMATED", "G-ROLLBACK", "G-A11Y", "G-STORE", "G-LEGAL-DOCS", "G-SEC-HEADERS"):
            self.assertEqual(status[applies], "UNVERIFIED", applies)

    def test_sensitive_products_elevate_checks(self):
        health = {c["id"]: c["status"] for c in g.instantiate(HEALTH)}
        self.assertEqual(health["G-COMPLIANCE-READINESS"], "UNVERIFIED")
        self.assertEqual(health["G-PRIV-SENSITIVE"], "UNVERIFIED")
        b2b = {c["id"]: c["status"] for c in g.instantiate(B2B)}
        for cid in ("G-TENANT-ISOLATION", "G-AI-EVALS", "G-BILLING", "G-SEC-WEBHOOKS", "G-SEC-UPLOADS"):
            self.assertEqual(b2b[cid], "UNVERIFIED")

    def test_instantiate_preserves_evidence(self):
        checks = g.instantiate(CALCULATOR)
        for c in checks:
            if c["id"] == "G-TEST-AUTOMATED":
                c.update(status="PASS", evidence=["EV-001"])
        again = g.instantiate(CALCULATOR, checks)
        c = next(c for c in again if c["id"] == "G-TEST-AUTOMATED")
        self.assertEqual((c["status"], c["evidence"]), ("PASS", ["EV-001"]))


class Scoring(unittest.TestCase):
    def mk(self, *specs):
        return [{"id": f"G-X{i}", "group": "production", "category": "x", "title": "x", "severity": sev, "status": st, "evidence": []}
                for i, (sev, st) in enumerate(specs)]

    def test_no_evidence_no_score(self):
        sc = g.score(self.mk(("blocker", "UNVERIFIED"), ("major", "UNVERIFIED")))
        self.assertEqual(sc["readiness"], "INSUFFICIENT_EVIDENCE")
        self.assertIsNone(sc["score"])

    def test_blocker_fail_is_not_ready(self):
        sc = g.score(self.mk(("blocker", "FAIL"), ("major", "PASS"), ("minor", "PASS")))
        self.assertEqual(sc["readiness"], "NOT_READY")

    def test_ready_and_warnings(self):
        self.assertEqual(g.score(self.mk(("blocker", "PASS"), ("major", "PASS")))["readiness"], "READY")
        sc = g.score(self.mk(("blocker", "PASS"), ("major", "WARNING"), ("minor", "UNVERIFIED")))
        self.assertEqual(sc["readiness"], "READY_WITH_WARNINGS")
        self.assertAlmostEqual(sc["score"], (3 + 1) / 5, places=3)
        self.assertEqual(g.score(self.mk(("blocker", "NOT_APPLICABLE")))["readiness"], "UNVERIFIED")

    def test_set_rules(self):
        check = {"severity": "blocker"}
        self.assertIn("evidence", g.set_status_problem(check, "PASS", [], None, set()))
        self.assertIn("unknown evidence", g.set_status_problem(check, "PASS", ["EV-9"], None, {"EV-1"}))
        self.assertIsNone(g.set_status_problem(check, "PASS", ["EV-1"], None, {"EV-1"}))
        self.assertIn("decision", g.set_status_problem(check, "NOT_APPLICABLE", [], "not needed", set()))
        self.assertIsNone(g.set_status_problem(check, "NOT_APPLICABLE", [], "decision: ADR-001 client-only", set()))
        self.assertIsNone(g.set_status_problem({"severity": "minor"}, "NOT_APPLICABLE", [], "no analytics", set()))


class LearningFirewall(unittest.TestCase):
    def test_user_preference_is_project_only(self):
        # Eval 6 / Demo E: "I hate rounded buttons"
        res = lf.classify({"kind": "preference", "evidence_quality": "anecdotal", "source_authority": "user",
                           "repeat_count": 10, "cross_project": True, "objective": False})
        self.assertEqual(res["outcome"], "PROJECT_ONLY")

    def test_outcomes(self):
        cases = [
            ({"kind": "implementation_finding"}, "REJECT"),
            ({"kind": "local_fact", "evidence_quality": "observed"}, "PROJECT_ONLY"),
            ({"kind": "engineering_failure", "evidence_quality": "observed", "source_authority": "project", "objective": True}, "PROJECT_ONLY"),
            ({"kind": "engineering_failure", "evidence_quality": "reproduced", "objective": True, "cross_project": True}, "CANDIDATE"),
            ({"kind": "engineering_failure", "evidence_quality": "tested", "source_authority": "official_docs", "objective": True,
              "cross_project": True}, "CORE_PROPOSAL"),
            ({"kind": "engineering_failure", "evidence_quality": "tested", "source_authority": "official_docs", "objective": True,
              "cross_project": True, "contains_private": True}, "CANDIDATE"),
            ({"kind": "pattern", "evidence_quality": "anecdotal", "objective": True, "cross_project": True, "contradicted": True}, "REJECT"),
        ]
        for obs, expected in cases:
            with self.subTest(obs=obs):
                self.assertEqual(lf.classify(obs)["outcome"], expected)

    def test_leak_scan(self):
        hits = lf.leak_scan("See /Users/alice/acme/app.ts, mail bob@acme.io, api_key=sk-abcdefghijklmnopqrstu, Acme Corp", ["Acme Corp"])
        joined = " ".join(hits)
        for frag in ("absolute user path", "email", "secret", "project identifier"):
            self.assertIn(frag, joined)
        self.assertEqual(lf.leak_scan("Store money as integer minor units, not binary floats.", ["Acme"]), [])


if __name__ == "__main__":
    unittest.main()
