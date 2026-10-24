# Architecture Document — {Product}

<!-- Owner: Principal Software Architect. Simplest architecture that satisfies actual requirements. Separate CURRENT from PROPOSED when reviewing existing systems. -->

## Context
TBD — actors and external systems.

## System overview
TBD — one paragraph, then a diagram.

```text
TBD diagram
```

## Boundaries
TBD — modules/services, what each owns, allowed dependency directions.

## Stack
| Concern | Choice | ADR | Notes |
|---|---|---|---|
| TBD | | | |

## Data
TBD — stores, ownership, tenancy (or "Not applicable: client-only"). Details in DATA_MODEL.md.

## Security
TBD — authn/authz model, secrets, trust boundaries. Details in SECURITY.md.

## Integrations
TBD — third parties, protocols, failure handling.

## Reliability
TBD — SLOs if a server exists; degradation strategy.

## Environments
TBD — local/preview/staging/production; config and secrets.

## Failure behavior
| Critical path | Failure | User sees | System does | Detected by |
|---|---|---|---|---|
| TBD | | | | |

## Scaling assumptions
TBD — numbers (users, requests, data volume) and the first expected bottleneck.

## Not applicable
TBD — components deliberately absent and why (e.g. "No queue: no async work in V1").
