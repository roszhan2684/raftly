---
id: F001
name: Organizations, authentication and roles
status: PLANNED
priority: MUST
owner_role: security
node: N002
requirements:
  - REQ-001
  - REQ-002
  - REQ-007
decisions:
  - ADR-002
  - ADR-003
depends_on: []
screens:
  - SCR-signin
  - SCR-org-settings
evidence_status: NONE
updated_at: 2026-10-24
---
# F001 — Organizations, authentication and roles

## Product goal
Teams can sign up, invite colleagues and work inside an isolated organization with the right permissions (REQ-001, REQ-002, REQ-007).

## User story / jobs
As a sales leader, I want to create my team's workspace and invite managers and reps with the right access, so call data stays inside my company and reps only see what they should.

## Actors
Admin (creates org, manages members and roles), Manager, Rep, invited user.

## Entry conditions
Unauthenticated visitor on the sign-up page, or an invited user with a valid invitation link.

## Main flow
1. Sign up with a magic link or Google/Microsoft OIDC.
2. Create an organization (name, consent policy text default) → creator becomes Admin.
3. Admin invites users by email with a role; the invitee accepts and joins.
4. Admin manages roles, team assignment (manager ↔ reps) and the visibility setting (REQ-007).

## Alternative flows
Existing user invited to a second org → org switcher. Invitation expired (7 days) → request a new one. Last Admin cannot be removed or demoted.

## State model
Invitation: pending → accepted | expired | revoked. Membership: active | suspended.

## Data model implications
`orgs`, `users`, `memberships(org_id, user_id, role)`, `teams`, `team_members`, `invitations`, `sessions`. All tenant tables carry `org_id` with RLS (ADR-002).

## API / contracts
`POST /api/orgs`, `POST /api/orgs/{id}/invitations`, `POST /api/invitations/{token}/accept`, `PATCH /api/memberships/{id}`, `GET /api/me`.

## Permissions
Admin: everything in the org. Manager: read own teams' members. Rep: own profile. Enforced in route policies **and** by RLS.

## UI / screens
SCR-signin, SCR-org-settings (members, roles, teams, visibility, consent policy).

## Edge cases
Email case and plus-addressing; OIDC email not verified → reject; invitation link reused; user removed while sessions are active → sessions revoked.

## Error behavior
Generic sign-in error messages (no account enumeration); clear invitation errors with a recovery action.

## Empty / loading states
New org: an onboarding checklist (invite team → connect Zoom or upload first call). Members list skeletons.

## Analytics / metrics
`org_created`, `invite_sent`, `invite_accepted` (activation funnel; no call content in events).

## Security / privacy requirements
Database sessions, HttpOnly Secure SameSite cookies, CSRF protection on state-changing routes, rate limits on sign-in and invitations, invitation tokens single-use and hashed, audit events for role changes (F009).

## Accessibility requirements
Forms labelled, errors linked to fields, keyboard operable, focus management after sign-in.

## Observability
Sign-in success/failure rate, invitation acceptance latency, auth error logs without tokens or emails in plain text.

## Dependencies
N001 platform foundation; email provider (magic links).

## Out of scope
- SAML SSO and SCIM (ADR-003 revisit trigger)
- Passwords

## Tests
- Unit: role policy matrix
- Integration: invitation lifecycle; last-admin guard
- Security: cross-org access denied for every endpoint (isolation suite)
- E2E: sign up → create org → invite → accept

## Acceptance criteria
- [ ] Users can sign in by magic link and by Google/Microsoft OIDC
- [ ] Admin can invite, change roles and remove members; the last Admin is protected
- [ ] Reps cannot access other reps' data unless visibility is granted
- [ ] No endpoint returns data from another org (isolation suite passes)

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
None yet. Evidence lives in `evidence.yaml` (`raftly evidence for F001`).
