# Product Build Document — SalesLens

## How to build
Run `/raftly build next`. Each prompt in `.raftly/prompts/` is self-contained and lists the evidence and status updates required.
N006 (eval harness) only depends on N001 and can run in parallel with identity work.

## Build graph
<!-- generated:graph:start -->
```text
Phase 0
  [ ] N001 Platform foundation
Phase 1
  [ ] N002 Identity and organizations  <- N001
  [ ] N006 AI eval harness and golden dataset  <- N001
Phase 2
  [ ] N003 RBAC and tenant isolation  <- N002
Phase 3
  [ ] N004 Call ingestion and storage  <- N003
  [ ] N011 Billing and usage metering  <- N003
Phase 4
  [ ] N005 Transcription pipeline  <- N004
  [ ] N012 Data governance  <- N004
Phase 5
  [ ] N007 Insight extraction  <- N005, N006
Phase 6
  [ ] N008 Manager review queue  <- N007
  [ ] N010 Team trends  <- N007
Phase 7
  [ ] N009 Rep coaching view  <- N008
  [ ] N013 Notifications  <- N008
Phase 8
  [ ] N014 Launch readiness  <- N009, N010, N011, N012, N013
```

Legend: `[x]` complete · `[v]` verified · `[?]` implemented, unverified · `[>]` in progress · `[~]` partial · `[!]` blocked · `[-]` dropped

| Phase | Node | Name | Type | Depends on | Status | Prompts |
|---|---|---|---|---|---|---|
| 0 | N001 | Platform foundation | ops | — | PLANNED | 001-platform-foundation.md |
| 1 | N002 | Identity and organizations | foundation | N001 | PLANNED | 002-identity-and-organizations.md |
| 1 | N006 | AI eval harness and golden dataset | quality | N001 | PLANNED | 006-ai-eval-harness.md |
| 2 | N003 | RBAC and tenant isolation | security | N002 | PLANNED | 003-rbac-and-tenant-isolation.md |
| 3 | N004 | Call ingestion and storage | feature | N003 | PLANNED | 004-call-ingestion-and-storage.md |
| 3 | N011 | Billing and usage metering | feature | N003 | PLANNED | 011-billing-and-usage-metering.md |
| 4 | N005 | Transcription pipeline | feature | N004 | PLANNED | 005-transcription-pipeline.md |
| 4 | N012 | Data governance | security | N004 | PLANNED | 012-data-governance.md |
| 5 | N007 | Insight extraction | feature | N005, N006 | PLANNED | 007-insight-extraction.md |
| 6 | N008 | Manager review queue | feature | N007 | PLANNED | 008-manager-review-queue.md |
| 6 | N010 | Team trends | feature | N007 | PLANNED | 010-team-trends.md |
| 7 | N009 | Rep coaching view | feature | N008 | PLANNED | 009-rep-coaching-view.md |
| 7 | N013 | Notifications | feature | N008 | PLANNED | 013-notifications.md |
| 8 | N014 | Launch readiness | launch | N009, N010, N011, N012, N013 | PLANNED | 014-launch-readiness.md |

**Progress:** 0.0% complete, 0.0% verified (14 active nodes). Derived from `build-graph.yaml`; do not edit this block by hand.
<!-- generated:graph:end -->

## Phases
- **Phase 0:** N001 platform foundation (CI, environments, telemetry, storage, database).
- **Phase 1:** N002 identity and organizations; N006 AI eval harness (independent, starts early to de-risk A-003).
- **Phase 2:** N003 RBAC and tenant isolation. Every later data path extends its isolation suite.
- **Phase 3:** N004 call ingestion; N011 billing and metering (needs orgs and roles only).
- **Phase 4:** N005 transcription (spike first, validates A-002); N012 data governance.
- **Phase 5:** N007 insight extraction (needs transcripts + harness; validates A-003).
- **Phase 6:** N008 manager queue; N010 trends.
- **Phase 7:** N009 rep view; N013 notifications.
- **Phase 8:** N014 launch readiness (+ EXP-001 pilot decision).

## Feature ordering
Isolation before any customer data (N003 before N004). Eval harness before extraction (N006 before N007). The queue
before rep view and notifications (they consume share events).

## Acceptance gates
- Every node touching tenant data adds isolation tests; failing isolation blocks VERIFIED (G-TENANT-ISOLATION).
- N005 must record the spike evidence and update A-002; N007 must meet ADR-008 thresholds and update A-003.
- If an assumption is INVALIDATED, stop and revisit the dependent ADR before continuing.

## Test strategy
| Layer | Scope | Tooling (confirm at N001) |
|---|---|---|
| Unit | policies, domain rules, validators, metrics | Vitest |
| Integration | repositories with real Postgres (RLS on), jobs, storage emulator, webhooks | Vitest + containers |
| Isolation suite | every endpoint/repository: cross-org access denied, zero rows | custom suite (N003), required in CI |
| Contract | STT/LLM adapters with recorded fixtures; Stripe/Zoom webhook payloads | fixtures |
| AI evals | golden dataset metrics vs thresholds; CI sample + full release run | harness (N006) |
| E2E | sign-up → org → upload → insights → review → share → rep reads | Playwright |
| Accessibility | axe on key screens + manual keyboard/screen reader for the queue | axe + manual |
| Performance | queue/trends p95, job throughput, upload of 3-hour files | k6 or similar (decide at N010) |
| Security | dependency audit, secrets scan, headers check, optional independent review agents | CI + agents |

## Release requirements
All applicable blockers in gate.yaml: product scope/flows, auth, server-side authorization, tenant isolation, backups,
secrets, input validation, uploads, webhooks, sensitive-data controls, compliance readiness (professional review), automated
tests, rollback, billing, AI evals. Plus the Forgotten-20 items (password-less recovery, deletion, export, failed payments,
trial expiry, webhook idempotency, restore drill, audit log, legal pages).
