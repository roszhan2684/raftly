# SalesLens

> Raftly project file. Canonical machine state lives in `state.yaml`.

- **Mode:** GREENFIELD
- **Stage:** BLUEPRINT_COMPLETE
- **Product type:** b2b-ai-saas
- **Initialised:** 2026-10-24T11:00:00Z

## Idea / goal

"Build a B2B AI sales coaching platform that ingests sales calls and identifies objections, competitors, and coaching opportunities."

## Classification
Multi-tenant B2B SaaS with an AI pipeline over sensitive conversational data, billing, one integration (Zoom), email,
file uploads and a public marketing site. Likely regulatory touchpoints: GDPR (EU customers) and call-recording consent laws.

## Profile

- `surfaces`: [web] · `backend`: true · `accounts`: true · `multi_tenant`: true · `ai`: true · `payments`: true
- `personal_data`: true · `sensitive_data`: [credentials] · `file_uploads`: true · `integrations`: true · `email`: true
- `public_site`: true · `analytics`: true · `regulated`: [GDPR, call-recording-consent] · `cost_mode`: BOOTSTRAP

## How this differs from a simple app
Organizations/RBAC/tenancy, an AI evaluation gate, billing and metering, security/observability and GTM are all first-class
here. They were deliberately absent from the calculator example.

## Where things live

| What | File |
|---|---|
| Machine state | `state.yaml` |
| Requirements | `requirements.yaml` |
| Decisions (ADRs) | `decisions/` and `DECISIONS.md` |
| Build graph | `build-graph.yaml` and `BUILD.md` |
| Evidence | `evidence.yaml` |
| Assumptions / risks / experiments | `assumptions.yaml`, `risks.yaml`, `experiments.yaml` |
