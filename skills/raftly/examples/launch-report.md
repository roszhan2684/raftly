**LAUNCH · LAUNCH_READINESS · Not ready: insufficient evidence on 3 blockers**

Production gate: **INSUFFICIENT_EVIDENCE**. Evidence covers 58% of applicable weight, so there is no score yet.
- PASS: automated tests in CI (EV-031), secrets scan (EV-032), tenant isolation tests (EV-029), headers/CSP (EV-035)
- **FAIL**: none
- **UNVERIFIED blockers**: G-BACKUPS (no backup configuration found), G-AI-EVALS (eval-v2 has 40 cases, threshold not yet agreed),
  G-ROLLBACK (no rehearsal recorded)
- WARNING: G-SEC-DEPS: 2 moderate advisories, mitigated (EV-036)
- Forgotten 20%: account deletion and failed-payment emails not implemented (added as N017, N018)

I did not mark anything PASS without a recorded result.

**Next action**: enable managed backups and run a restore drill (closes G-BACKUPS and G-RESTORE), agree the eval threshold
(founder input: recall ≥ 0.80?), then rehearse the rollback. Estimated three short sessions.
