# Platform, DevOps and SRE

Roles: **Staff Platform / DevOps Engineer** (`platform`), **Principal SRE** (`sre`).

## CI/CD (proportionate)

Every product: CI that runs lint, type-check, tests and build on each push or PR; reproducible builds from
lockfiles; secrets only in the CI secret store. Products with a server add migration checks, a staging
deploy and a smoke test before production. Mobile adds signed builds, store submission automation and
staged rollout.

## Environments

local → (preview per PR, optional) → staging (production-like config, separate data) → production.
Configuration via environment variables; parity between staging and production (G-ENV-PARITY); never copy
production personal data into lower environments without anonymisation.

## Deployment and rollback (spec §33)

For each risky release or migration (MIGRATION.md):
- **Forward migration** steps; **backward compatibility** (expand/contract) so the previous app version still works;
- **data backup** before destructive steps;
- **canary/phased** strategy (percentage, cohort, or feature flag);
- **rollback**: the previous application version (one command or click) and the database rollback or
  compensating strategy;
- **verification**: health checks, key metrics and queries that prove success;
- **failure trigger**: the observable condition that aborts and rolls back.
Client-only apps: rollback means redeploying the previous static build, or a store phased-release halt
plus an expedited fix. Rehearse it once (G-ROLLBACK).

## Reliability (SRE)

- **SLOs** only for products with a server: availability and latency for critical user journeys, with an
  error budget. Don't invent SLOs for an offline app.
- **Monitoring**: error tracking, service metrics (rate, errors, duration), queue depth and job failures,
  dependency health, cost.
- **Alerts** on symptoms (SLO burn, error spikes, failed jobs, cost anomalies), routed to a named owner,
  each with a runbook link. No alert without an action.
- **Capacity**: know the first bottleneck (DB connections, worker throughput, API rate limits) and its trigger.
- **Degradation**: define what the product does when each dependency is down (architecture.md §Failure modes).

## Observability by feature (spec §27)

Each critical feature spec defines: success metric, failure metric, latency, cost (if relevant), logs,
traces (if relevant), alerts, and the business outcome metric.
Example AI feature: completion success, p95 latency, inference cost per job and tenant, retry count, user
rejection rate, hallucination reports.

## Incidents and postmortems (spec §32)

`raftly records new postmortem --title "..." --severity SEV2` creates `.raftly/postmortems/PM-xxx.md`:
summary, timeline (UTC), impact, detection, root cause, contributing factors, resolution, prevention,
**test or guardrail added**, learning candidate. Blameless and specific. Every prevention item becomes a
build-graph node or debt item. Generalizable lessons go through the Learning Firewall.

## Cost

Track the main cost drivers against the estimates in COST.md; alert on anomalies; per-tenant cost visibility
for usage-heavy features (AI, storage, transcription).

## Upgrades (spec §34)

Quarterly (or on advisories): runtime/framework EOL dates, deprecated APIs, major dependency versions,
security advisories. Upgrade when benefit or risk justifies it, not because a version exists. Record the decision.
