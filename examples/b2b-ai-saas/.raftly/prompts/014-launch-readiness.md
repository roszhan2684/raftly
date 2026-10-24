# Prompt 014 — Launch readiness

> Build-graph node: **N014** · Features: F001, F002, F003, F004, F005, F006, F007, F008, F009, F010
> Self-contained implementation prompt. Paste into Claude Code, or run `/raftly build next`.

## Role to activate
Launch Director (with raftly-launch-reviewer and raftly-security-reviewer agents for independent passes)

## Files to read first
- `.raftly/state.yaml`
- `.raftly/ARCHITECTURE.md` (module boundaries)
- `.raftly/gate.yaml` (all applicable checks)
- `.raftly/LAUNCH.md`, `.raftly/SECURITY.md`, `.raftly/COMPLIANCE_READINESS.md`
- `.raftly/experiments.yaml` (EXP-001)
- Skill reference `production-gate.md`

## Objective
Reach an honest, evidence-backed readiness state for a paid launch.

## Scope
Collect evidence for every applicable production check and Forgotten-20 item, complete the EXP-001 pilot decision, record the professional legal review, the restore drill, the rollback rehearsal, alert ownership and the support path, and produce the launch deck.

## Dependencies
N009–N013 VERIFIED or COMPLETE.

## Architecture / design constraints
- No new features; fixes go back to their owning nodes.
- Never mark PASS without an evidence id; unknowns stay UNVERIFIED.

## Implementation tasks
1. Run the full test, isolation, eval and accessibility suites; record the evidence.
2. Dependency audit and secrets scan; headers/CSP on production.
3. Backup restore drill and rollback rehearsal (record durations).
4. Alerts routed to an owner with runbooks; incident path documented.
5. Legal review of terms, privacy policy, DPA and consent language (G-COMPLIANCE-READINESS, G-LEGAL-DOCS), recorded as evidence by the reviewer's confirmation.
6. EXP-001 decision recorded (experiment status + ADR if pivoting).
7. `raftly gate report --write`, the Forgotten-20 report, `raftly deck --kind launch`.

## Explicitly out of scope
- New functionality

## Edge cases
- Founder wants to launch with UNVERIFIED blockers → FOUNDER ADR accepting specific risks + `--override-reason`

## Security / accessibility requirements
- Independent agent reviews before declaring readiness

## Tests required
- As required per gate check

## Verification steps
- `raftly gate score` shows READY or READY_WITH_WARNINGS; `raftly validate` has zero errors

## After implementation (state and evidence updates)
1. Run relevant tests/checks; keep the exact commands and outputs.
2. Compare the implementation with the feature acceptance criteria.
3. Record evidence: `raftly evidence record --subject F001 --kind test --result PASS|FAIL --summary "..." --command "..."`; register entities (`API-*`, `TBL-*`, `TEST-*`) and link them (`raftly evidence link`).
4. Update status: `raftly graph set-status N014 IMPLEMENTED_UNVERIFIED`, then `VERIFIED` only with passing verification evidence.
5. Record any deviation as an ADR, debt item or risk.
6. Do not mark COMPLETE unless verification passed and the Definition of Done is checked.

## Escalate instead of changing autonomously
- Any change to Type-1 decisions: ADR-001 (modular monolith), ADR-002 (Postgres + RLS tenancy), ADR-003 (auth), ADR-006/ADR-007 (AI providers).
- New third-party services or dependencies not in `dependencies.yaml`.
- Anything that weakens tenant isolation, consent handling or retention.
