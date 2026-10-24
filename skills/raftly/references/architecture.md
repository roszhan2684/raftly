# Architecture

Role: **Principal Software Architect** (`architect`), consulting the frontend, mobile, backend, data, AI,
security and platform roles. Architecture follows the product's constraints, not what is fashionable.

## The simplicity ladder

Start at the lowest rung that satisfies the **actual** requirements, and climb only with a stated reason:

1. Static site / client-only app (local storage, no server).
2. Client app + managed backend-as-a-service for one concern (auth or storage).
3. Single deployable monolith + one relational database.
4. Monolith + background worker/queue (when work is slow, retryable or scheduled).
5. Modular monolith with clear internal boundaries.
6. Separate services, only for independent scaling, isolation or team boundaries you can name today.

Every climb is an ADR with the trigger that justified it.

## What ARCHITECTURE.md defines (when relevant)

frontend · mobile · backend · API style · data model · tenancy · authentication · authorisation ·
background jobs · cache · file/object storage · search · messaging/email · billing · analytics ·
observability · AI · vector search · deployment · CI/CD · environments · backup/restore ·
failure/degradation behaviour · third-party integrations · secret management.
Write "Not applicable: <reason>" for the ones that don't apply. Never invent components to fill the list.

Include: context (system and actors), a system overview diagram (ASCII or Mermaid in a fenced block),
boundaries and dependency directions, the stack table with ADR links, data flows, reliability and failure
behaviour for each critical path (Constitution 26), environments, and scaling assumptions with numbers.

## Type-1 decisions

Data store and tenancy, auth architecture, platform strategy, core framework, primary cloud/vendor
coupling, public API contracts, AI provider coupling. Each gets an ADR with options, evidence,
consequences and a `revisit_trigger` (decision-authority.md).

## Build vs open source vs managed vs paid (spec §10)

For meaningful subsystems (auth, storage, email, analytics, queues, search, billing, AI orchestration,
components, monitoring), when the choice is material, score each option 1–5 on:

| Dimension | Question |
|---|---|
| Engineering effort | build and integrate time |
| Security risk | how much security-critical code do we own? |
| Maintenance burden | upgrades, on-call, patches |
| Initial cost | today, in bootstrap mode |
| Expected scale cost | at the projected volumes |
| Lock-in | proprietary API/data format? |
| Portability | standard protocols, export paths |
| Fit | does it do what we need without contortions? |
| Operational complexity | things to run and monitor |

Put the table in the ADR. Default **BOOTSTRAP COST MODE**: prefer free and open source when they are equally
good, but don't confuse "free today" with lower lifetime complexity (Constitution 7). Rolling your own auth
to save a free-tier fee is usually the wrong trade.

Open-source checks: licence (verify it; MIT/Apache-2.0/BSD preferred; avoid unclear licences and open-core
traps where the critical production feature is paid), release recency, maintainer activity, security history,
TypeScript/language support, bundle or dependency weight, customisability, migration risk.

Record every adopted dependency: `raftly records add dependency --name ... --version ... --purpose ... --license ... --status ADOPTED --chosen-by ADR-00x --lock-in LOW`.

## Cost Architect (spec §22)

For material choices, estimate: current or free-tier cost, the key cost driver (requests, storage, seats,
tokens, minutes of audio), behaviour at 100 / 1k / 10k / 100k users (or the relevant unit), assumptions,
uncertainty, and migration risk. **Never fabricate vendor prices.** If you haven't verified current pricing,
write "exact pricing requires fresh research" and describe the shape of the curve. Use `COST.md` when costs
are material.

## Vendor lock-in (spec §23)

Rate LOW / MEDIUM / HIGH on: standards-based or proprietary API, data portability, migration complexity,
a self-host option, pricing dependency, and whether a fallback or provider abstraction is feasible. Lock-in
is advisory. Managed services are often the right call. Record `lock_in` in dependencies.yaml.

## Failure modes

For each critical path: what fails (dependency down, timeout, bad input, quota exceeded), what the user
sees, what the system does (retry with backoff, queue, degrade, fail closed), and how we find out (metric
or alert). AI paths need a low-confidence path and a provider-outage path.

## Architecture drift detection (spec §18)

In REVIEW and on each build, compare the approved architecture with reality. Typical drift:
- a controller or route touching persistence directly despite a service boundary;
- a planned queue that is missing (work done synchronously in a request);
- UI calling an unapproved third-party API;
- authorisation enforced only in the frontend;
- an undocumented database or store;
- a new dependency that bypasses the chosen abstraction.

Report: planned · actual · drift · risk · recommended fix · **whether the architecture should change
instead of the code**. Record it as debt (`architecture_violation`) or as a superseding ADR.

## Upgrade strategy (spec §34)

Inspect framework and runtime versions, deprecated APIs, major dependencies, security advisories (when
research is available), and EOL dates. Don't upgrade just because a new version exists. Compare benefit,
risk, effort and compatibility, and record the decision.

## Calibration

- Calculator (web + mobile): client-only. One shared TypeScript calculation engine (pure, UI-free, fully
  unit-tested) used by both surfaces. A cross-platform UI is justified *if* current research confirms that
  one toolkit serves web and mobile well (e.g. Expo + React Native Web), otherwise a web app plus a
  wrapped or native shell. No backend, auth, database, queue or Kubernetes. Hosting is static.
- B2B AI SaaS: modular monolith (web app + API) + Postgres with tenant scoping enforced in the data layer
  + object storage for audio + a worker queue for transcription and analysis + a provider abstraction
  around transcription and LLM calls + per-tenant usage metering.
