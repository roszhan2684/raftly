# Prompt 010 — Team trends

> Build-graph node: **N010** · Features: F007
> Self-contained implementation prompt. Paste into Claude Code, or run `/raftly build next`.

## Role to activate
Staff Frontend Engineer + Principal Data Engineer

## Files to read first
- `.raftly/state.yaml`
- `.raftly/ARCHITECTURE.md` (module boundaries)
- `.raftly/features/F007-team-trends.md`
- `.raftly/DATA_MODEL.md` (insights, indexes)

## Objective
Objection and competitor trends by team and rep, accessible and fast.

## Scope
Aggregation queries (with a materialized view if needed), the trends API, drill-down, CSV export (audited), and SCR-trends with chart + table alternatives.

## Dependencies
N007 VERIFIED or COMPLETE.

## Architecture / design constraints
- p95 ≤ 500 ms at 50k insights per org; measure before adding a materialized view.
- Charts library chosen via OSS evaluation (licence, accessibility, bundle); record it in dependencies.yaml, or build a simple SVG chart internally if sufficient.

## Implementation tasks
1. Queries + indexes; performance test with seeded data.
2. API + drill-down + CSV export with an audit event.
3. SCR-trends with accessible table alternatives and text summaries.

## Explicitly out of scope
- Win-rate correlation

## Edge cases
- Small samples (n < 10)
- Dismissed insights excluded

## Security / accessibility requirements
- Tenant-scoped aggregates
- Colour-blind-safe palette; data tables

## Tests required
- Query correctness tests
- Performance test
- Accessibility checks

## Verification steps
- Record performance evidence against the budget

## After implementation (state and evidence updates)
1. Run relevant tests/checks; keep the exact commands and outputs.
2. Compare the implementation with the feature acceptance criteria.
3. Record evidence: `raftly evidence record --subject F007 --kind test --result PASS|FAIL --summary "..." --command "..."`; register entities (`API-*`, `TBL-*`, `TEST-*`) and link them (`raftly evidence link`).
4. Update status: `raftly graph set-status N010 IMPLEMENTED_UNVERIFIED`, then `VERIFIED` only with passing verification evidence.
5. Record any deviation as an ADR, debt item or risk.
6. Do not mark COMPLETE unless verification passed and the Definition of Done is checked.

## Escalate instead of changing autonomously
- Any change to Type-1 decisions: ADR-001 (modular monolith), ADR-002 (Postgres + RLS tenancy), ADR-003 (auth), ADR-006/ADR-007 (AI providers).
- New third-party services or dependencies not in `dependencies.yaml`.
- Anything that weakens tenant isolation, consent handling or retention.
