---
id: ADR-008
title: No analytics or telemetry in V1
owner_role: privacy
date: 2026-10-24
status: ACCEPTED
decision_type: RECOMMEND
impact: low
reversibility: high
type1: false
confidence: 85
affects:
  - REQ-011
supersedes: []
superseded_by: null
evidence: []
category: privacy
revisit_trigger: A product question that cannot be answered by beta interviews and store reviews
---
# ADR-008 — No analytics or telemetry in V1

- **Owner role:** privacy
- **Decision type:** RECOMMEND · **Impact:** low · **Reversibility:** high · **Confidence:** 85/100

## Context
Tally has no backend and collects no personal data (ADR-001). Product questions for V1 (EXP-001) are
answered through a closed beta and store reviews.

## Options considered
| Option | Pros | Cons |
|---|---|---|
| None | zero data collection, simplest store privacy labels, a trust message | no usage numbers |
| Privacy-preserving aggregate analytics | some usage data | SDK, disclosures, a consent analysis per market |
| Full product analytics | rich data | contradicts the product's positioning |

## Decision
No analytics or crash-reporting SDKs in V1. G-ANALYTICS is N/A (profile). G-CLIENT-ERRORS is resolved as an
explicit privacy-preserving opt-out: errors are surfaced to the user, and beta testers report them.

## Rationale
Minimisation (privacy-compliance.md). "Collects no data" is a genuine feature for a utility.

## Supporting evidence
EXP-001 does not require telemetry.

## Rejected alternatives
Aggregate analytics (deferred), full analytics (rejected).

## Consequences
Store privacy labels: "Data Not Collected". Evidence of crashes relies on beta reports and store vitals provided
by the platforms.

## Revisit trigger
A product question that cannot be answered by beta interviews and store reviews.

## Affected requirements / features
REQ-011 · F006
