# Tally

> Raftly project file. Human-readable summary of what this project is and how Raftly is operating on it.
> Canonical machine state lives in `state.yaml`.

- **Mode:** GREENFIELD
- **Stage:** BLUEPRINT_COMPLETE
- **Product type:** consumer-utility
- **Initialised:** 2026-10-24T09:00:00Z

## Idea / goal

"I want to build a calculator mobile app and website."

## Classification
Simple consumer utility on iOS, Android and the web. No backend, no accounts, no personal data, no payments,
no AI. The public website is the product itself (SEO and performance matter).

## Profile

- `surfaces`: [web, ios, android]
- `backend`: false · `accounts`: false · `personal_data`: false · `payments`: false · `multi_tenant`: false · `ai`: false
- `public_site`: true · `analytics`: false · `cost_mode`: BOOTSTRAP

## What Raftly deliberately did not add
A backend, authentication, a database, queues, Kubernetes, microservices, analytics, monitoring backends.
None of them serve a V1 requirement (ADR-001, ADR-008). Their production-gate checks are NOT_APPLICABLE.

## Where things live

| What | File |
|---|---|
| Machine state | `state.yaml` |
| Requirements | `requirements.yaml` |
| Decisions (ADRs) | `decisions/` and `DECISIONS.md` |
| Build graph | `build-graph.yaml` and `BUILD.md` |
| Evidence | `evidence.yaml` |
| Assumptions / risks | `assumptions.yaml`, `risks.yaml` |
