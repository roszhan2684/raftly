# Prompt 008 — Manager review queue

> Build-graph node: **N008** · Features: F005
> Self-contained implementation prompt. Paste into Claude Code, or run `/raftly build next`.

## Role to activate
Staff Frontend Engineer + Design Director

## Files to read first
- `.raftly/state.yaml`
- `.raftly/ARCHITECTURE.md` (module boundaries)
- `.raftly/features/F005-manager-review-queue.md`
- `.raftly/DESIGN.md` (SCR-queue, direction A)
- `.raftly/DESIGN_SYSTEM.md`
- `.raftly/decisions/ADR-009-*.md`

## Objective
The manager home: triage insights with keyboard speed, add notes and share with reps.

## Scope
Queue API with filters, review/notes/share endpoints with policies, SCR-queue, the drill-in to SCR-call-detail (transcript + timeline + audio snippet), keyboard triage, empty/loading/error states and audit events.

## Dependencies
N007 VERIFIED or COMPLETE.

## Architecture / design constraints
- Managers act only on their teams' insights (policy module + RLS).
- Audio snippets via short-lived presigned URLs.
- Optimistic UI with rollback.

## Implementation tasks
1. Queue API (pagination, filters) and review endpoints.
2. SCR-queue grouped by rep with filters; item detail with quote, snippet and context.
3. Keyboard shortcuts (j/k/a/d/s) with a help overlay.
4. Notes and share; emit share events for N013.
5. Audit events for share actions.

## Explicitly out of scope
- Scorecards
- Assignments

## Edge cases
- Concurrent reviews
- Rep changed teams
- Insight deleted by retention

## Security / accessibility requirements
- Authorization tests for every endpoint
- WCAG 2.2 AA: keyboard triage, focus, labels, audio controls

## Tests required
- Component tests (states, actions)
- Authorization tests
- E2E review → share

## Verification steps
- Record the EXP-001 metric instrumentation (actions per manager per week) as working

## After implementation (state and evidence updates)
1. Run relevant tests/checks; keep the exact commands and outputs.
2. Compare the implementation with the feature acceptance criteria.
3. Record evidence: `raftly evidence record --subject F005 --kind test --result PASS|FAIL --summary "..." --command "..."`; register entities (`API-*`, `TBL-*`, `TEST-*`) and link them (`raftly evidence link`).
4. Update status: `raftly graph set-status N008 IMPLEMENTED_UNVERIFIED`, then `VERIFIED` only with passing verification evidence.
5. Record any deviation as an ADR, debt item or risk.
6. Do not mark COMPLETE unless verification passed and the Definition of Done is checked.

## Escalate instead of changing autonomously
- Any change to Type-1 decisions: ADR-001 (modular monolith), ADR-002 (Postgres + RLS tenancy), ADR-003 (auth), ADR-006/ADR-007 (AI providers).
- New third-party services or dependencies not in `dependencies.yaml`.
- Anything that weakens tenant isolation, consent handling or retention.
