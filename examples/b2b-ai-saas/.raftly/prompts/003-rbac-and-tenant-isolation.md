# Prompt 003 — RBAC and tenant isolation

> Build-graph node: **N003** · Features: F001
> Self-contained implementation prompt. Paste into Claude Code, or run `/raftly build next`.

## Role to activate
Principal Security Engineer + Principal Data Engineer

## Files to read first
- `.raftly/state.yaml`
- `.raftly/ARCHITECTURE.md` (module boundaries)
- `.raftly/decisions/ADR-002-*.md` (RLS model)
- `.raftly/features/F001-*.md` (permissions)
- `.raftly/SECURITY.md` (threat model)

## Objective
Database-enforced tenant isolation and server-side role policies, proven by tests.

## Scope
RLS policies on every tenant table, a per-transaction org context for web requests and jobs, a tenant-scoped repository, role policy functions (Admin/Manager/Rep + visibility setting), and an isolation test suite that future nodes extend.

## Dependencies
N002 VERIFIED or COMPLETE.

## Architecture / design constraints
- The app connects as a non-owner role subject to RLS; migrations use a separate role.
- The org context is set with `SET LOCAL` inside each transaction; verify pooler compatibility.
- Policy functions are the only place role decisions are made.

## Implementation tasks
1. Enable RLS and write policies for all identity/team tables.
2. Middleware: resolve session → membership → set the org context; deny when absent.
3. Job helper: `withOrgContext(orgId, fn)` for the worker.
4. Role policy module with a unit-tested matrix.
5. Isolation suite: for every endpoint and repository method, a second org's user gets 404/403 and zero rows.
6. Document the "new tenant table checklist" in ARCHITECTURE.md.

## Explicitly out of scope
- Feature endpoints beyond identity (they adopt the pattern later)

## Edge cases
- Connection reuse leaking context between requests (test with concurrent requests)
- Admin of org A who is a member of org B

## Security / accessibility requirements
- Isolation tests are required evidence for G-TENANT-ISOLATION and G-AUTHZ-SERVER
- Consider the raftly-security-reviewer agent before VERIFIED

## Tests required
- Isolation suite
- Policy matrix unit tests
- Concurrency test for context leakage

## Verification steps
- Record isolation evidence; `raftly gate set G-TENANT-ISOLATION PASS --evidence EV-...` only when the suite passes

## After implementation (state and evidence updates)
1. Run relevant tests/checks; keep the exact commands and outputs.
2. Compare the implementation with the feature acceptance criteria.
3. Record evidence: `raftly evidence record --subject F001 --kind test --result PASS|FAIL --summary "..." --command "..."`; register entities (`API-*`, `TBL-*`, `TEST-*`) and link them (`raftly evidence link`).
4. Update status: `raftly graph set-status N003 IMPLEMENTED_UNVERIFIED`, then `VERIFIED` only with passing verification evidence.
5. Record any deviation as an ADR, debt item or risk.
6. Do not mark COMPLETE unless verification passed and the Definition of Done is checked.

## Escalate instead of changing autonomously
- Any change to Type-1 decisions: ADR-001 (modular monolith), ADR-002 (Postgres + RLS tenancy), ADR-003 (auth), ADR-006/ADR-007 (AI providers).
- New third-party services or dependencies not in `dependencies.yaml`.
- Anything that weakens tenant isolation, consent handling or retention.
