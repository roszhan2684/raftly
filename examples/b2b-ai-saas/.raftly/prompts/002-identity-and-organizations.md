# Prompt 002 — Identity and organizations

> Build-graph node: **N002** · Features: F001
> Self-contained implementation prompt. Paste into Claude Code, or run `/raftly build next`.

## Role to activate
Staff Backend Engineer + Principal Security Engineer

## Files to read first
- `.raftly/state.yaml`
- `.raftly/ARCHITECTURE.md` (module boundaries)
- `.raftly/features/F001-organizations-authentication-and-roles.md`
- `.raftly/decisions/ADR-003-*.md`, `ADR-002-*.md`
- `.raftly/DATA_MODEL.md` (orgs, users, memberships)

## Objective
Passwordless sign-in, organizations, invitations and memberships.

## Scope
Auth.js setup (magic link, Google, Microsoft OIDC), database sessions, `orgs`/`users`/`memberships`/`invitations`/`teams` tables with migrations, org creation, invitation flow, org switcher, sign-in and org settings screens.

## Dependencies
N001 VERIFIED or COMPLETE.

## Architecture / design constraints
- Org and role data in our Postgres (ADR-003).
- Every tenant table has `org_id` (RLS policies arrive in N003, but design for them now).
- Cookies HttpOnly, Secure, SameSite=Lax; CSRF protection on mutations.

## Implementation tasks
1. Auth.js with the Drizzle adapter; magic link via the transactional email provider (choose and record the dependency).
2. Migrations for identity tables.
3. Org creation → creator is Admin.
4. Invitations: hashed single-use tokens, 7-day expiry, role assignment, acceptance flow.
5. Membership management API + SCR-org-settings members tab; last-admin guard.
6. Rate limits on sign-in and invitation endpoints.

## Explicitly out of scope
- RLS policies (N003)
- SAML/SCIM

## Edge cases
- Unverified OIDC emails rejected
- Invitation reuse
- User in multiple orgs

## Security / accessibility requirements
- No account enumeration in auth responses
- Accessible forms with labelled errors

## Tests required
- Integration tests for the invitation lifecycle and last-admin guard
- E2E: sign up → create org → invite → accept

## Verification steps
- Walk F001's acceptance criteria that don't depend on RLS; RLS-dependent criteria verify in N003

## After implementation (state and evidence updates)
1. Run relevant tests/checks; keep the exact commands and outputs.
2. Compare the implementation with the feature acceptance criteria.
3. Record evidence: `raftly evidence record --subject F001 --kind test --result PASS|FAIL --summary "..." --command "..."`; register entities (`API-*`, `TBL-*`, `TEST-*`) and link them (`raftly evidence link`).
4. Update status: `raftly graph set-status N002 IMPLEMENTED_UNVERIFIED`, then `VERIFIED` only with passing verification evidence.
5. Record any deviation as an ADR, debt item or risk.
6. Do not mark COMPLETE unless verification passed and the Definition of Done is checked.

## Escalate instead of changing autonomously
- Any change to Type-1 decisions: ADR-001 (modular monolith), ADR-002 (Postgres + RLS tenancy), ADR-003 (auth), ADR-006/ADR-007 (AI providers).
- New third-party services or dependencies not in `dependencies.yaml`.
- Anything that weakens tenant isolation, consent handling or retention.
