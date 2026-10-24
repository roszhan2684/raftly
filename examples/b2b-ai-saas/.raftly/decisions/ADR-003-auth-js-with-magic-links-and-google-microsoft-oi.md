---
id: ADR-003
title: "Auth.js with magic links and Google/Microsoft OIDC; organizations and roles in our database"
owner_role: security
date: 2026-10-24
status: ACCEPTED
decision_type: RECOMMEND
impact: high
reversibility: medium
type1: true
confidence: 75
affects:
  - REQ-001
  - REQ-002
supersedes: []
superseded_by: null
evidence:
  - "https://authjs.dev"
category: security
revisit_trigger: First customer requiring SAML SSO or SCIM provisioning
---
# ADR-003 — Auth.js with magic links and Google/Microsoft OIDC; organizations and roles in our database

- **Owner role:** security
- **Decision type:** RECOMMEND · **Impact:** high · **Reversibility:** medium · **Confidence:** 75/100

## Context
Users must sign in without passwords and belong to organizations with roles (REQ-001, REQ-002). Bootstrap cost mode applies. SAML SSO is expected only from larger customers later.

## Options considered
| Option | Effort | Security risk owned | Cost | Lock-in | Fit |
|---|---|---|---|---|---|
| A. Auth.js (open source) for sessions/providers + our own org, membership and role tables | medium | moderate (well-trodden library) | none | low | **Good** |
| B. Managed B2B auth service (orgs, SSO, SCIM built in) | low | low | per-MAU/connection pricing (not verified) | medium-high | Strong once SSO is needed |
| C. Build authentication ourselves | high | high | none | none | Rejected (Constitution 7) |

## Decision
Option A now. Orgs, memberships and roles live in Postgres next to the RLS model (ADR-002). Sessions are database-backed, cookies HttpOnly, Secure, SameSite=Lax. Admin accounts are encouraged to use OIDC with MFA at the identity provider.

## Rationale
Keeps identity, tenancy and authorization in one model with no recurring cost while the product is validated. Option B stays the documented path when SAML/SCIM demand appears.

## Supporting evidence
Auth.js documentation (prior knowledge; verify current provider support and the adapter for Drizzle at implementation).

## Rejected alternatives
B deferred (cost and lock-in before need), C rejected (owning security-critical code).

## Consequences
- Invitation, membership and role management are ours to build (F001).
- Email delivery is required for magic links (email provider dependency).
- Adding SAML later: either a library extension or migrating sessions to a managed service. The revisit trigger watches for it.

## Revisit trigger
First customer requiring SAML SSO or SCIM provisioning.

## Affected requirements / features
REQ-001, REQ-002 · F001
