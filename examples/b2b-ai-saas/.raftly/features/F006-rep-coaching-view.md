---
id: F006
name: Rep coaching view
status: PLANNED
priority: MUST
owner_role: frontend
node: N009
requirements:
  - REQ-007
decisions:
  - ADR-009
  - ADR-002
depends_on:
  - F005
screens:
  - SCR-rep-feed
evidence_status: NONE
updated_at: 2026-10-24
---
# F006 — Rep coaching view

## Product goal
Reps receive and learn from coaching on their own calls (REQ-007).

## User story / jobs
As a rep, I want to see the coaching my manager shared and the moments in my calls behind it, so I can improve on the next call.

## Actors
Rep (primary), Manager (author).

## Entry conditions
Rep member with shared coaching or their own analyzed calls.

## Main flow
1. Rep home SCR-rep-feed: shared coaching notes with quote, snippet and link to the call.
2. My calls list with insights (if org setting "reps see AI insights" is on; default on).
3. Mark a coaching note as read or reply.

## Alternative flows
Visibility setting "team visibility" granted by Admin → reps can view teammates' calls (read-only).

## State model
Coaching note: `shared → read`; replies thread.

## Data model implications
`coaching_notes.read_at`, `note_replies`.

## API / contracts
`GET /api/me/coaching` · `GET /api/me/calls` · `POST /api/notes/{id}/read` · `POST /api/notes/{id}/replies`.

## Permissions
Reps see only their own calls and notes unless team visibility is granted (REQ-007). Enforced by RLS policies that include the visibility rule.

## UI / screens
SCR-rep-feed, SCR-call-detail (read-only for reps).

## Edge cases
Rep leaves the org (access removed immediately; notes retained per retention); visibility toggled off while a teammate's call is open (next request denied).

## Error behavior
Standard error states with retry; access denied shows a neutral "not available" page (no data leak).

## Empty / loading states
"No coaching yet. When your manager shares feedback it will appear here."

## Analytics / metrics
Coaching read rate; time to read.

## Security / privacy requirements
Visibility rules tested at the database level; no enumeration of teammates' call ids.

## Accessibility requirements
Feed items are articles with headings; audio accessible; replies form labelled.

## Observability
Feed API latency; authorization denials (alert on spikes, which may indicate a probing attempt or a bug).

## Dependencies
F005, F001.

## Out of scope
- Rep self-review workflows
- Gamification

## Tests
- Authorization matrix tests (rep / teammate / manager / admin × visibility setting)
- E2E: shared note → rep reads → manager sees read status

## Acceptance criteria
- [ ] Reps see shared coaching and their own calls
- [ ] Reps cannot see teammates' calls unless visibility is granted
- [ ] Read status and replies work

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
None yet. Evidence lives in `evidence.yaml` (`raftly evidence for F006`).
