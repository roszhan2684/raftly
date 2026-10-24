# Prompt 011 — Billing and usage metering

> Build-graph node: **N011** · Features: F008
> Self-contained implementation prompt. Paste into Claude Code, or run `/raftly build next`.

## Role to activate
Staff Backend Engineer

## Files to read first
- `.raftly/state.yaml`
- `.raftly/ARCHITECTURE.md` (module boundaries)
- `.raftly/features/F008-billing-and-usage-metering.md`
- `.raftly/decisions/ADR-010-*.md`
- `.raftly/state.yaml` → `blueprint.open_founder_decisions` (pricing model)

## Objective
Trials, plans, seats and audio-hour metering with entitlement enforcement, built to support either pricing model.

## Scope
Stripe products/prices in test mode, checkout and the customer portal, a webhook handler (verified, idempotent), seat sync, the `usage_events` ledger and reporting, allowance enforcement for F002, trial expiry and failed-payment flows, and SCR-billing.

## Dependencies
N003 VERIFIED or COMPLETE. **Check whether the founder has resolved the pricing decision**; if not, implement the plan configuration for the recommended per-seat + allowance model behind config.

## Architecture / design constraints
- Our `usage_events` ledger is the source of truth; Stripe receives reports.
- No card data on our servers.
- Entitlement checks are server-side.

## Implementation tasks
1. Stripe objects via configuration (no hard-coded prices).
2. Checkout + portal endpoints; SCR-billing.
3. Webhook handler with signature verification and `stripe_events` dedupe.
4. Seat sync on membership changes.
5. Metering from transcription completions; allowance checks; 80%/100% warnings.
6. Trial expiry → read-only; failed payment → dunning + grace → read-only.

## Explicitly out of scope
- Enterprise invoicing
- Advanced tax automation

## Edge cases
- Out-of-order webhooks
- Duplicate usage reports
- Mid-cycle seat changes

## Security / accessibility requirements
- G-BILLING, G-SEC-WEBHOOKS, G-F20-FAILED-PAYMENTS, G-F20-TRIAL-EXPIRY evidence
- Billing pages accessible

## Tests required
- Webhook replay/order tests
- Metering idempotency
- E2E in Stripe test mode

## Verification steps
- If the pricing model was changed by the founder, ensure the Requirement Change Engine ran first

## After implementation (state and evidence updates)
1. Run relevant tests/checks; keep the exact commands and outputs.
2. Compare the implementation with the feature acceptance criteria.
3. Record evidence: `raftly evidence record --subject F008 --kind test --result PASS|FAIL --summary "..." --command "..."`; register entities (`API-*`, `TBL-*`, `TEST-*`) and link them (`raftly evidence link`).
4. Update status: `raftly graph set-status N011 IMPLEMENTED_UNVERIFIED`, then `VERIFIED` only with passing verification evidence.
5. Record any deviation as an ADR, debt item or risk.
6. Do not mark COMPLETE unless verification passed and the Definition of Done is checked.

## Escalate instead of changing autonomously
- Any change to Type-1 decisions: ADR-001 (modular monolith), ADR-002 (Postgres + RLS tenancy), ADR-003 (auth), ADR-006/ADR-007 (AI providers).
- New third-party services or dependencies not in `dependencies.yaml`.
- Anything that weakens tenant isolation, consent handling or retention.
