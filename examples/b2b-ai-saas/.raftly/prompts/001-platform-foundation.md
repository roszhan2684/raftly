# Prompt 001 — Platform foundation

> Build-graph node: **N001** · Features: —
> Self-contained implementation prompt. Paste into Claude Code, or run `/raftly build next`.

## Role to activate
Staff Platform Engineer

## Files to read first
- `.raftly/state.yaml`
- `.raftly/ARCHITECTURE.md` (module boundaries)
- `.raftly/decisions/ADR-001-*.md`, `ADR-004-*.md`, `ADR-005-*.md`
- `.raftly/SECURITY.md` (secrets), `.raftly/COST.md`

## Objective
Stand up the repository, CI, environments and observability baseline that every other node builds on.

## Scope
Monorepo layout (web + worker from one codebase), TypeScript strict, lint/format with module-boundary rules, CI (lint, type-check, test, build, migrations check), preview/staging/production environments, secrets per environment, OpenTelemetry + error tracking, Postgres and object storage provisioned per environment.

## Dependencies
None.

## Architecture / design constraints
- Two process types from one codebase: `web` and `worker` (ADR-001).
- Region and providers recorded in a RECOMMEND ADR; the data-residency founder decision is flagged if EU customers are expected.
- No secrets in the repo; `.env.example` only.

## Implementation tasks
1. Scaffold the repo and module folders (`orgs`, `calls`, `transcripts`, `insights`, `billing`, `governance`).
2. Lint rules enforcing module boundaries (no cross-module DB access).
3. CI pipeline with caching; required checks on main.
4. Provision Postgres (with backups and PITR enabled), the storage bucket (private, encrypted, lifecycle placeholder) and the worker runtime for staging and production.
5. OpenTelemetry tracing for web and worker; error tracking with PII scrubbing.
6. Health/readiness endpoints for web and worker.

## Explicitly out of scope
- Feature code

## Edge cases
- Preview environments must not use production data
- Worker deploys must drain jobs gracefully

## Security / accessibility requirements
- Secrets in the platform secret store; least-privilege service credentials
- Error tracking scrubs request bodies and headers

## Tests required
- CI runs green on an empty test suite plus a smoke test
- Health checks return 200 in staging

## Verification steps
- Record CI and staging smoke-test evidence; `raftly gate set G-ENV-PARITY ...` and `G-HEALTH` when evidence exists

## After implementation (state and evidence updates)
1. Run relevant tests/checks; keep the exact commands and outputs.
2. Compare the implementation with the feature acceptance criteria.
3. Record evidence: `raftly evidence record --subject N001 --kind test --result PASS|FAIL --summary "..." --command "..."`; register entities (`API-*`, `TBL-*`, `TEST-*`) and link them (`raftly evidence link`).
4. Update status: `raftly graph set-status N001 IMPLEMENTED_UNVERIFIED`, then `VERIFIED` only with passing verification evidence.
5. Record any deviation as an ADR, debt item or risk.
6. Do not mark COMPLETE unless verification passed and the Definition of Done is checked.

## Escalate instead of changing autonomously
- Any change to Type-1 decisions: ADR-001 (modular monolith), ADR-002 (Postgres + RLS tenancy), ADR-003 (auth), ADR-006/ADR-007 (AI providers).
- New third-party services or dependencies not in `dependencies.yaml`.
- Anything that weakens tenant isolation, consent handling or retention.
