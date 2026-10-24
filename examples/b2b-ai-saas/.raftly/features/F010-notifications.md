---
id: F010
name: Notifications
status: PLANNED
priority: SHOULD
owner_role: backend
node: N013
requirements:
  - REQ-013
decisions:
  - ADR-003
depends_on:
  - F005
screens:
  - SCR-notification-settings
evidence_status: NONE
updated_at: 2026-10-24
---
# F010 — Notifications

## Product goal
Build the weekly coaching habit (REQ-013, A-001).

## User story / jobs
As a manager, I want a weekly digest of new coaching moments; as a rep, I want to know when coaching is shared with me.

## Actors
Manager, Rep, email provider.

## Entry conditions
Member with email notifications enabled (default on, with one-click unsubscribe).

## Main flow
1. A weekly job builds a per-manager digest: counts by rep and top three items with links (no transcript text in email beyond short quotes, an org setting).
2. A share event sends a rep notification.
3. Preferences page to opt out per type.

## Alternative flows
No new insights → no digest sent.

## State model
Notification: queued → sent | bounced | suppressed.

## Data model implications
`notification_prefs(user_id, type, enabled)`, `notifications_log`.

## API / contracts
`PUT /api/me/notifications` · provider webhook for bounces.

## Permissions
Users manage their own preferences.

## UI / screens
SCR-notification-settings.

## Edge cases
Bounced emails suppress future sends; timezones (digest Monday 08:00 local); users in multiple orgs.

## Error behavior
Provider failures retried; persistent failures logged; never block core flows.

## Empty / loading states
Not applicable (email).

## Analytics / metrics
Digest open → queue visit rate (privacy-respecting, aggregated).

## Security / privacy requirements
Authenticated sending domain (SPF, DKIM, DMARC); minimal personal data in emails; unsubscribe link.

## Accessibility requirements
Plain-text alternative; semantic HTML email; sufficient contrast.

## Observability
Send success, bounce rate, digest job duration.

## Dependencies
F005; email provider (chosen in N013).

## Out of scope
- Slack notifications (V1.1 candidate)

## Tests
- Digest content builder unit tests
- Preference enforcement
- Bounce handling

## Acceptance criteria
- [ ] Weekly digest sent to managers with new insights only
- [ ] Rep notification on share
- [ ] One-click unsubscribe and preferences work
- [ ] Sending domain authenticated

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
None yet. Evidence lives in `evidence.yaml` (`raftly evidence for F010`).
