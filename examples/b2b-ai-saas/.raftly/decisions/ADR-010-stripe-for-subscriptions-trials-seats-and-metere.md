---
id: ADR-010
title: Stripe for subscriptions, trials, seats and metered audio hours
owner_role: gtm
date: 2026-10-24
status: ACCEPTED
decision_type: RECOMMEND
impact: medium
reversibility: medium
type1: false
confidence: 78
affects:
  - REQ-009
supersedes: []
superseded_by: null
evidence:
  - "https://docs.stripe.com/billing"
category: billing
revisit_trigger: Pricing model changes (founder decision) or tax/invoicing needs exceed Stripe Billing
---
# ADR-010 — Stripe for subscriptions, trials, seats and metered audio hours

- **Owner role:** gtm
- **Decision type:** RECOMMEND · **Impact:** medium · **Reversibility:** medium · **Confidence:** 78/100

## Context
REQ-009 needs trials, plans, seats and an audio-hour allowance. **The pricing model itself is an open founder decision** (per-seat with allowance vs usage-based). Billing must support either.

## Options considered
| Option | Effort | Fit for either pricing model | Lock-in |
|---|---|---|---|
| A. Stripe Billing (subscriptions, trials, quantities, usage-based metering) | low | yes | medium |
| B. A merchant-of-record platform | low; handles tax | check usage-metering support (not verified) | medium |
| C. Build billing | very high | — | — |

## Decision
Stripe Billing. Internal `usage_events` table is the source of truth for audio hours (metered from completed transcriptions), reported to Stripe; entitlements are checked server-side before processing; webhooks are verified and idempotent.

## Rationale
Supports both candidate pricing models without re-architecture; widely documented. Keeping our own usage ledger limits lock-in.

## Supporting evidence
Stripe Billing documentation (prior knowledge; verify current usage-based billing APIs and tax options at N011).

## Rejected alternatives
B (re-evaluate if sales tax/VAT handling becomes a burden), C (cost).

## Consequences
- If the founder picks usage-based pricing, the metering already exists; only plan configuration and the pricing page change (that change runs the Requirement Change Engine).
- Failed-payment and trial-expiry flows are Forgotten-20 items (G-F20-FAILED-PAYMENTS, G-F20-TRIAL-EXPIRY).

## Revisit trigger
Pricing model changes (founder decision) or tax/invoicing needs exceed Stripe Billing.

## Affected requirements / features
REQ-009 · F008
