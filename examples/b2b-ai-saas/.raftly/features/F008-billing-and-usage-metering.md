---
id: F008
name: Billing and usage metering
status: PLANNED
priority: MUST
owner_role: backend
node: N011
requirements:
  - REQ-009
decisions:
  - ADR-010
depends_on:
  - F001
  - F003
screens:
  - SCR-billing
evidence_status: NONE
updated_at: 2026-10-24
---
# F008 — Billing and usage metering

## Product goal
Monetize with trials and plans while protecting margin on audio processing (REQ-009, A-005).

## User story / jobs
As an Admin, I want to start a trial, choose a plan, manage seats and see audio usage, so we pay for what we use without surprises.

## Actors
Admin, Stripe (webhooks), system (metering).

## Entry conditions
Org created (trial starts automatically, 14 days).

## Main flow
1. Trial starts at org creation with a trial allowance of audio hours.
2. Admin chooses a plan (pricing model pending the founder decision; billing supports per-seat + allowance or usage-based) via Stripe Checkout.
3. Seats sync with active memberships; audio hours are metered from completed transcriptions into `usage_events` and reported to Stripe.
4. The allowance is checked before processing new calls (F002); warnings at 80% and 100%.

## Alternative flows
Trial expiry → read-only mode (data visible, no new processing) until a plan is chosen. Failed payment → dunning emails, 7-day grace, then read-only.

## State model
Subscription: trialing → active → past_due → canceled; org access: full | read_only.

## Data model implications
`subscriptions(org_id, stripe_ids, status, plan)`, `usage_events(org_id, call_id, audio_seconds, reported_at)`, `stripe_events(event_id unique)`.

## API / contracts
`POST /api/billing/checkout` · `POST /api/billing/portal` · `POST /api/webhooks/stripe` (signature-verified, idempotent) · `GET /api/billing/usage`.

## Permissions
Admins only.

## UI / screens
SCR-billing (plan, seats, usage meter, invoices via the Stripe portal).

## Edge cases
Webhook arrives before checkout completes; duplicate events; seat count changes mid-cycle; usage reported twice (idempotent by `call_id`); the founder switches the pricing model (Requirement Change Engine).

## Error behavior
Billing outages never block reading data; processing pauses only when the allowance is exhausted or access is read-only, with clear messages.

## Empty / loading states
Usage meter starts at 0 with an explanation of what counts as audio hours.

## Analytics / metrics
Trial → paid conversion, MRR (from Stripe), audio hours per seat.

## Security / privacy requirements
No card data touches our servers (Stripe-hosted pages); webhook signature verification; idempotent processing; billing changes audited.

## Accessibility requirements
Usage meter has a text equivalent; billing forms come from the Stripe-hosted, accessible pages.

## Observability
Webhook failure rate, metering lag, cost-to-revenue ratio per org (alert when above the COST.md threshold).

## Dependencies
F001 orgs/memberships, F003 completed transcriptions (metering source), Stripe.

## Out of scope
- Invoicing for enterprise contracts
- Sales tax automation beyond Stripe settings (revisit trigger in ADR-010)

## Tests
- Webhook replay and ordering tests
- Metering idempotency
- Trial expiry and failed-payment flows (Forgotten 20%)
- E2E in Stripe test mode

## Acceptance criteria
- [ ] Trial, checkout, seat sync and the customer portal work in test mode
- [ ] Audio hours metered once per call and enforced
- [ ] Failed payment and trial expiry flows behave as specified
- [ ] Webhooks verified and idempotent

## Definition of Done
Mark `[x]` when done with evidence, `[~]` when not applicable (say why).
- [ ] Requirements satisfied
- [ ] UI implemented
- [ ] API implemented
- [ ] Logic/persistence implemented
- [ ] Authorization enforced server-side (RLS + role policy)
- [ ] Tenant isolation test for every new data path
- [ ] Validation present
- [ ] Loading / empty / error states
- [ ] Retries/idempotency where needed
- [ ] Accessibility checked
- [ ] Responsive behavior checked
- [ ] Tests written and passing
- [ ] Observability (logs/metrics/alerts) in place
- [ ] Security/privacy review
- [ ] Docs updated

## Evidence status
None yet. Evidence lives in `evidence.yaml` (`raftly evidence for F008`).
