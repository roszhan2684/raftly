# Definition of Done

A feature is not complete just because UI or code exists (Constitution 13–15).

## Statuses

| Status | Meaning | Rule |
|---|---|---|
| NOT_STARTED | known, not planned | — |
| PLANNED | specified, in graph | — |
| IN_PROGRESS | being implemented | sets `execution.current_node` |
| PARTIAL | some acceptance criteria met | say which in the report |
| BLOCKED | cannot proceed | needs a recorded blocker (`--blocker "..."`) |
| IMPLEMENTED_UNVERIFIED | code exists, not verified | the next action is verification |
| VERIFIED | passing verification evidence exists | test/e2e/manual/review/metric/audit record with PASS, and no newer FAIL |
| COMPLETE | verified **and** every DoD item done or N/A with reason | must pass through VERIFIED; the node needs all its features COMPLETE |
| DROPPED | removed from scope | keep the record; link the superseding requirement |

The scripts enforce these rules. `build`/`lint` evidence alone never verifies a feature.

## DoD checklist (in every feature spec)

Apply the relevant checks; mark `[x]` done (with evidence) or `[~]` not applicable **with a reason**:

- requirements satisfied (every acceptance criterion)
- UI implemented (all states: loading, empty, error, success)
- API implemented · backend/domain logic · persistence
- authorisation enforced **server-side**
- validation present (client for UX, server for truth)
- retries/idempotency where needed
- accessibility checked (automated + manual for key flows)
- responsive behaviour checked
- analytics (only where justified)
- logs and metrics (observability by feature)
- tests written and passing
- docs updated
- security review · privacy considerations
- mobile/platform verification
- migration behaviour (if data changed)
- operational behaviour (alerts, runbook) for critical paths

Example of a correct N/A: `- [~] Authorization enforced server-side: N/A, client-only app with no server (ADR-001)`.
Incorrect: ticking a box because "it probably works".

## Evidence status on the feature

`evidence_status`: NONE → PARTIAL (implementation exists, verification incomplete) → SUFFICIENT
(verification evidence exists). It is updated by `raftly records feature-status`.
