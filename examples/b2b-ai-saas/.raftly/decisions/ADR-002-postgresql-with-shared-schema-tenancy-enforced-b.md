---
id: ADR-002
title: PostgreSQL with shared-schema tenancy enforced by row-level security
owner_role: data
date: 2026-10-24
status: ACCEPTED
decision_type: RECOMMEND
impact: high
reversibility: low
type1: true
confidence: 85
affects:
  - REQ-001
  - REQ-007
  - REQ-011
supersedes: []
superseded_by: null
evidence:
  - "https://www.postgresql.org/docs/current/ddl-rowsecurity.html"
category: data
revisit_trigger: An enterprise customer contractually requires physical isolation or per-tenant data residency
---
# ADR-002 — PostgreSQL with shared-schema tenancy enforced by row-level security

- **Owner role:** data
- **Decision type:** RECOMMEND · **Impact:** high · **Reversibility:** low · **Confidence:** 85/100

## Context
Every customer organization's calls, transcripts and insights must be isolated (REQ-001, REQ-007). Data is relational: orgs → users → calls → transcripts → insights → reviews. Reporting (trends) needs aggregation.

## Options considered
| Option | Isolation | Ops cost | Fit |
|---|---|---|---|
| A. Shared schema + `org_id` on every tenant table + Postgres row-level security (RLS) + a tenant-scoped repository | strong logical, enforced by the database | low | **Best for mid-market SaaS** |
| B. Schema per tenant | stronger logical | migrations multiply | Not needed yet |
| C. Database per tenant | physical | highest | Only for enterprise/residency demands |
| D. Document database | — | low | weaker integrity for relational data and reporting |

## Decision
PostgreSQL, option A. Each request and job sets `app.current_org_id` in a transaction; RLS policies restrict every tenant table to it; the repository layer requires an org context; the migration role is the only role that bypasses RLS.

## Rationale
Defence in depth: application scoping plus database-enforced policies, so one missed `WHERE` clause cannot leak data. Postgres also covers full-text search and, if needed later, vector search via extensions, which defers extra stores.

## Supporting evidence
PostgreSQL documentation on row security policies (prior knowledge; re-verify policy syntax and performance notes at implementation).

## Rejected alternatives
B and C (cost without a current requirement); D (relational integrity and reporting).

## Consequences
- Every new tenant table needs `org_id`, an RLS policy and an isolation test (part of the DoD).
- Background jobs must set the org context explicitly.
- Connection pooling must preserve per-transaction settings (verify pooler mode).
- Moving to per-tenant databases later is a major migration, which makes this Type-1.

## Revisit trigger
An enterprise customer contractually requires physical isolation or per-tenant data residency.

## Affected requirements / features
REQ-001, REQ-007, REQ-011 · F001, F009
