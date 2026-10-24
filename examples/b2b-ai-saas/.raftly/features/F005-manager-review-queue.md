---
id: F005
name: Manager review queue
status: PLANNED
priority: MUST
owner_role: design-director
node: N008
requirements:
  - REQ-006
decisions:
  - ADR-009
depends_on:
  - F004
  - F001
screens:
  - SCR-queue
  - SCR-call-detail
evidence_status: NONE
updated_at: 2026-10-24
---
# F005 — Manager review queue

## Product goal
Managers act on coaching moments weekly: the core workflow (REQ-006, A-001).

## User story / jobs
As a manager, I want a prioritized queue of new insights I can accept, dismiss, edit and share with notes, so coaching takes minutes, not hours.

## Actors
Manager (primary), Admin.

## Entry conditions
Manager of at least one team with analyzed calls.

## Main flow
1. Open SCR-queue (home): new insights grouped by rep, newest first, filter by type and team.
2. Open an item → quote, a 30-second audio snippet around the timestamp, and transcript context.
3. Accept / edit category / dismiss (with an optional reason).
4. Add a coaching note and share with the rep → appears in the rep's feed (F006) and triggers a notification (F010).

## Alternative flows
Bulk dismiss; snooze until next week; jump to the full call (SCR-call-detail).

## State model
Insight review: `new → accepted | dismissed | edited`; `shared_at`; `coaching_notes` thread.

## Data model implications
`insight_reviews(insight_id, reviewer_id, action, reason)`, `coaching_notes(org_id, insight_id, author_id, body, shared_at)`.

## API / contracts
`GET /api/queue?team=&type=` · `POST /api/insights/{id}/review` · `POST /api/insights/{id}/notes` · `POST /api/insights/{id}/share`.

## Permissions
Managers act only on insights from their teams' reps; Admins on all. Enforced server-side + RLS.

## UI / screens
SCR-queue (home for managers), SCR-call-detail (drill-in).

## Edge cases
Rep moved between teams (visibility follows the current team; history retained); insight deleted by retention while open; concurrent review by two managers (last write wins with an audit trail).

## Error behavior
Optimistic updates with rollback and a toast on failure; audio snippet failure → transcript context still shown.

## Empty / loading states
Empty queue: "You're all caught up. New insights appear as calls are analyzed." Skeleton rows while loading.

## Analytics / metrics
Weekly active managers, insights actioned per manager per week (EXP-001 metric), accept/dismiss ratio.

## Security / privacy requirements
Coaching notes are personal data about employees: visible only to the rep, their managers and Admins; audit events for share actions.

## Accessibility requirements
Full keyboard triage (j/k to move, a accept, d dismiss, s share) with visible focus; audio player accessible; screen-reader labels on actions.

## Observability
Queue API p95 latency, review action error rate.

## Dependencies
F004 insights, F001 roles.

## Out of scope
- Scorecards and rubrics
- Coaching assignments with due dates

## Tests
- Component tests for triage actions and states
- Authorization tests: a manager cannot act on another team's insight
- E2E: review → share → appears in the rep feed

## Acceptance criteria
- [ ] Managers can accept, edit, dismiss, note and share from the queue
- [ ] Keyboard triage works end to end
- [ ] Only team insights are visible to each manager
- [ ] Actions are recorded for the EXP-001 metric

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
None yet. Evidence lives in `evidence.yaml` (`raftly evidence for F005`).
