# Prompt 012 — Data governance

> Build-graph node: **N012** · Features: F009
> Self-contained implementation prompt. Paste into Claude Code, or run `/raftly build next`.

## Role to activate
Privacy Engineering Lead + Staff Backend Engineer

## Files to read first
- `.raftly/state.yaml`
- `.raftly/ARCHITECTURE.md` (module boundaries)
- `.raftly/features/F009-data-governance-and-audit-log.md`
- `.raftly/decisions/ADR-012-*.md`
- `.raftly/PRIVACY.md`, `.raftly/COMPLIANCE_READINESS.md`

## Objective
Retention, export, deletion and audit logging that customers and reviewers can rely on.

## Scope
Retention policies + the nightly retention job (storage + DB), org export job, call and org deletion (cascade incl. storage, integrations, Stripe), the append-only audit log, SCR-audit-log, and settings UI.

## Dependencies
N004 VERIFIED or COMPLETE.

## Architecture / design constraints
- Deletions are reported done only after storage deletion is confirmed.
- The audit table is append-only at the database level (revoke UPDATE/DELETE from the app role).

## Implementation tasks
1. Retention settings API/UI and the nightly job with verification logging.
2. Export job producing JSON/CSV and a signed 24-hour link.
3. Call deletion cascade; org deletion with a 30-day grace and a hard-delete job.
4. Audit events for all listed actions; SCR-audit-log with filters.
5. Document backup roll-off behaviour in PRIVACY.md.

## Explicitly out of scope
- Legal hold
- Customer-managed keys

## Edge cases
- Retention shortened (backlog)
- Deletion during processing
- Export of a very large org

## Security / accessibility requirements
- G-DATA-EXPORT-DELETE, G-PRIV-INVENTORY, G-F20-ACCOUNT-DELETION, G-F20-AUDIT-LOG evidence
- Accessible confirmation dialogs

## Tests required
- Retention job integration test with a storage emulator
- Org deletion E2E
- Audit emission tests

## Verification steps
- Perform and record a deletion drill (`--kind manual`)

## After implementation (state and evidence updates)
1. Run relevant tests/checks; keep the exact commands and outputs.
2. Compare the implementation with the feature acceptance criteria.
3. Record evidence: `raftly evidence record --subject F009 --kind test --result PASS|FAIL --summary "..." --command "..."`; register entities (`API-*`, `TBL-*`, `TEST-*`) and link them (`raftly evidence link`).
4. Update status: `raftly graph set-status N012 IMPLEMENTED_UNVERIFIED`, then `VERIFIED` only with passing verification evidence.
5. Record any deviation as an ADR, debt item or risk.
6. Do not mark COMPLETE unless verification passed and the Definition of Done is checked.

## Escalate instead of changing autonomously
- Any change to Type-1 decisions: ADR-001 (modular monolith), ADR-002 (Postgres + RLS tenancy), ADR-003 (auth), ADR-006/ADR-007 (AI providers).
- New third-party services or dependencies not in `dependencies.yaml`.
- Anything that weakens tenant isolation, consent handling or retention.
