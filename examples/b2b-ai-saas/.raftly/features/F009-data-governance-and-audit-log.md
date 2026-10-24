---
id: F009
name: Data governance and audit log
status: PLANNED
priority: MUST
owner_role: privacy
node: N012
requirements:
  - REQ-011
  - REQ-014
decisions:
  - ADR-012
  - ADR-002
  - ADR-004
depends_on:
  - F002
screens:
  - SCR-org-settings
  - SCR-audit-log
evidence_status: NONE
updated_at: 2026-10-24
---
# F009 — Data governance and audit log

## Product goal
Customers control their data: retention, export, deletion and an audit trail (REQ-011, REQ-014).

## User story / jobs
As an Admin, I want retention rules, exports, deletions and an audit log, so we meet our obligations and can answer security questions.

## Actors
Admin, system (retention job), auditor (reads the log).

## Entry conditions
Admin role.

## Main flow
1. Admin sets retention (audio 30 days – 36 months; transcripts/insights until deletion or a set period).
2. The nightly retention job deletes expired audio from storage and marks calls; deletion is verified and logged.
3. Export: Admin requests an org export (JSON + CSV of calls metadata, transcripts, insights, notes) → background job → expiring download link.
4. Delete a call (cascades) or the organization (30-day grace, then hard delete incl. storage, Stripe customer cancellation, integration revocation).
5. Audit log: role changes, exports, deletions, integration changes, billing changes, sign-ins by Admins.

## Alternative flows
Cancel org deletion during the grace period.

## State model
Org: active → pending_deletion → deleted. Export: requested → ready → expired.

## Data model implications
`retention_policies(org_id, ...)`, `exports`, `audit_events(org_id, actor_id, action, target, ip_hash, at)` (append-only; retained 2 years).

## API / contracts
`PUT /api/org/retention` · `POST /api/org/export` · `DELETE /api/calls/{id}` · `POST /api/org/delete` · `GET /api/audit?...`.

## Permissions
Admins only; audit log read-only, append-only at the database level.

## UI / screens
SCR-org-settings (Data & privacy section), SCR-audit-log.

## Edge cases
Retention shortened → immediate backlog deletion with confirmation; deletion during an active processing job (job cancels); backups roll off per the backup retention (documented).

## Error behavior
Deletion failures retried and alerted; never reported as done until storage deletion is confirmed.

## Empty / loading states
Empty audit log: "Actions by admins will appear here."

## Analytics / metrics
None beyond operational metrics.

## Security / privacy requirements
Export links signed, single-org, expiring in 24 h; audit log tamper-evident (append-only role; optional hash chain V1.1); deletion covers derived data (eval samples, caches).

## Accessibility requirements
Destructive actions require typed confirmation with an accessible dialog.

## Observability
Retention job success, deletion backlog, export failures (alerts).

## Dependencies
F002 storage, F001 roles.

## Out of scope
- Customer-managed encryption keys
- Legal hold

## Tests
- Retention job deletes exactly the expired objects (integration test with storage emulator)
- Org deletion end-to-end including storage and integrations
- Audit events emitted for each listed action

## Acceptance criteria
- [ ] Retention settings enforced by the nightly job, with logged evidence
- [ ] Org export downloadable and complete
- [ ] Call and org deletion remove all derived data
- [ ] The audit log records every listed action

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
None yet. Evidence lives in `evidence.yaml` (`raftly evidence for F009`).
