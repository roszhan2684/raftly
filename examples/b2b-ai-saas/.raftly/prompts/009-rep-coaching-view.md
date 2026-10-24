# Prompt 009 — Rep coaching view

> Build-graph node: **N009** · Features: F006
> Self-contained implementation prompt. Paste into Claude Code, or run `/raftly build next`.

## Role to activate
Staff Frontend Engineer

## Files to read first
- `.raftly/state.yaml`
- `.raftly/ARCHITECTURE.md` (module boundaries)
- `.raftly/features/F006-rep-coaching-view.md`
- `.raftly/DESIGN.md` (SCR-rep-feed)

## Objective
Reps see shared coaching and their own calls; visibility rules are enforced in the database.

## Scope
Rep feed API and UI, my-calls list, read status and replies, RLS policy updates for the team-visibility setting, and authorization matrix tests.

## Dependencies
N008 VERIFIED or COMPLETE.

## Architecture / design constraints
- The visibility setting is evaluated in RLS policies, not only in the UI.

## Implementation tasks
1. Feed and my-calls endpoints.
2. SCR-rep-feed UI with read status and replies.
3. RLS policy extension for team visibility; add to the isolation suite.
4. Neutral "not available" page for denied access.

## Explicitly out of scope
- Self-review workflows

## Edge cases
- Rep leaves the org mid-session
- Visibility toggled off

## Security / accessibility requirements
- Authorization matrix (rep/teammate/manager/admin × visibility)
- Accessible feed (articles, headings)

## Tests required
- Matrix tests
- E2E share → read

## Verification steps
- Isolation suite still green

## After implementation (state and evidence updates)
1. Run relevant tests/checks; keep the exact commands and outputs.
2. Compare the implementation with the feature acceptance criteria.
3. Record evidence: `raftly evidence record --subject F006 --kind test --result PASS|FAIL --summary "..." --command "..."`; register entities (`API-*`, `TBL-*`, `TEST-*`) and link them (`raftly evidence link`).
4. Update status: `raftly graph set-status N009 IMPLEMENTED_UNVERIFIED`, then `VERIFIED` only with passing verification evidence.
5. Record any deviation as an ADR, debt item or risk.
6. Do not mark COMPLETE unless verification passed and the Definition of Done is checked.

## Escalate instead of changing autonomously
- Any change to Type-1 decisions: ADR-001 (modular monolith), ADR-002 (Postgres + RLS tenancy), ADR-003 (auth), ADR-006/ADR-007 (AI providers).
- New third-party services or dependencies not in `dependencies.yaml`.
- Anything that weakens tenant isolation, consent handling or retention.
