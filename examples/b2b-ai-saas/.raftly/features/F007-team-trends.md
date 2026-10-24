---
id: F007
name: Team trends
status: PLANNED
priority: MUST
owner_role: product-director
node: N010
requirements:
  - REQ-008
decisions:
  - ADR-009
  - ADR-002
depends_on:
  - F004
screens:
  - SCR-trends
evidence_status: NONE
updated_at: 2026-10-24
---
# F007 — Team trends

## Product goal
Sales leaders see which objections and competitors are rising, by team and rep (REQ-008).

## User story / jobs
As a sales leader, I want trends of objections and competitor mentions, so I can adjust enablement and messaging.

## Actors
Manager, Admin.

## Entry conditions
At least 10 analyzed calls in the selected period (otherwise the empty state explains why).

## Main flow
1. SCR-trends: period selector (4/12 weeks), team filter.
2. Charts: top objection categories over time; competitor mention share; per-rep table.
3. Click a data point → the list of underlying insights (evidence).

## Alternative flows
Export as CSV (Admins).

## State model
Stateless read model.

## Data model implications
Aggregation queries over insights by week; a materialized view refreshed by a job if query p95 exceeds the budget.

## API / contracts
`GET /api/trends?period=&team=` · `GET /api/trends/drilldown?...` · `GET /api/trends/export.csv`.

## Permissions
Managers: their teams; Admins: the org.

## UI / screens
SCR-trends.

## Edge cases
Small samples (show counts, avoid misleading percentages below n = 10); dismissed insights excluded; category renames.

## Error behavior
Chart load failure shows a retry with a table fallback.

## Empty / loading states
"Trends appear after 10 analyzed calls in this period." Skeleton charts.

## Analytics / metrics
Trends page views per manager per week.

## Security / privacy requirements
Aggregates are still tenant-scoped; CSV export audited (F009).

## Accessibility requirements
Every chart has a data table alternative and a text summary; colour-blind-safe palette; no meaning by colour alone.

## Observability
Trends query p95 (budget 500 ms at 50k insights per org).

## Dependencies
F004.

## Out of scope
- Win-rate correlation (needs CRM, REQ-015)

## Tests
- Query correctness against fixtures
- Performance test at 50k insights
- Accessibility: table alternatives present

## Acceptance criteria
- [ ] Trends by team and rep for 4 and 12 weeks
- [ ] Drill-down shows the underlying insights
- [ ] p95 under 500 ms at 50k insights per org
- [ ] Accessible table alternatives

## Definition of Done
Mark `[x]` when done with evidence, `[~]` when not applicable (say why).
- [ ] Requirements satisfied
- [ ] UI implemented
- [ ] API implemented
- [ ] Logic/persistence implemented
- [ ] Authorization enforced server-side (RLS + role policy)
- [ ] Tenant isolation test for every new data path
- [ ] Validation present
- [ ] Loading / empty / error states
- [ ] Retries/idempotency where needed
- [ ] Accessibility checked
- [ ] Responsive behavior checked
- [ ] Tests written and passing
- [ ] Observability (logs/metrics/alerts) in place
- [ ] Security/privacy review
- [ ] Docs updated

## Evidence status
None yet. Evidence lives in `evidence.yaml` (`raftly evidence for F007`).
