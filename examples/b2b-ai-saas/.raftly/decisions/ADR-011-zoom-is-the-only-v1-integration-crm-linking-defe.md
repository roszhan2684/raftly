---
id: ADR-011
title: "Zoom is the only V1 integration; CRM linking deferred"
owner_role: product-director
date: 2026-10-24
status: ACCEPTED
decision_type: RECOMMEND
impact: medium
reversibility: high
type1: false
confidence: 72
affects:
  - REQ-003
  - REQ-015
supersedes: []
superseded_by: null
evidence: []
category: product
revisit_trigger: More than 30% of pilot calls come from another platform, or deals context is the top pilot request
---
# ADR-011 — Zoom is the only V1 integration; CRM linking deferred

- **Owner role:** product-director
- **Decision type:** RECOMMEND · **Impact:** medium · **Reversibility:** high · **Confidence:** 72/100

## Context
Ingestion friction threatens activation (A-004). Integrations are expensive to build and maintain (OAuth, webhooks, rate limits, app review).

## Options considered
| Option | Value | Cost |
|---|---|---|
| A. Upload + Zoom cloud-recording import | covers the most common recorded-meeting source in the target segment (assumption, validate in pilot) | one OAuth app + webhook |
| B. Upload + Zoom + Google Meet + Teams | broader | 3× integration and review work |
| C. CRM linking in V1 | deal context | not needed to prove the core job |

## Decision
Option A. Zoom import via OAuth (minimum scopes for recordings), webhook for new recordings plus a manual "import recent" action. CRM linking is REQ-015 (COULD), deferred.

## Rationale
Prove the core job with the smallest integration surface. The pilot tells us which integration comes second.

## Supporting evidence
Assumption (not verified): Zoom is the dominant recorder for the ICP. Validate in EXP-001 recruitment.

## Rejected alternatives
B (scope), C (not needed for the core job).

## Consequences
- Zoom OAuth tokens are credentials (sensitive_data: credentials): encrypted at rest, scoped, revocable.
- Webhook verification and idempotency (G-SEC-WEBHOOKS).

## Revisit trigger
More than 30% of pilot calls come from another platform, or deal context is the top pilot request.

## Affected requirements / features
REQ-003, REQ-015 · F002
