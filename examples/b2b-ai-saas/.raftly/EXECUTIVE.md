# Executive Summary — SalesLens

## What
An AI coaching assistant that ingests sales calls (upload or Zoom), transcribes them, and surfaces objections, competitor
mentions and coaching moments, each with the exact quote and timestamp, in a manager review queue.

## Who
Sales managers and leaders at B2B teams of 10–100 reps; reps receive shared coaching.

## Why
Managers can't listen to every call; coaching becomes anecdotal and competitive shifts surface late.

## V1
- Orgs, roles and tenant isolation; passwordless sign-in
- Upload + Zoom import with consent attestation
- Diarized transcription; AI insights with evidence, gated by evals (objection precision ≥ 0.85, recall ≥ 0.80)
- Manager queue → coaching notes → rep feed; team trends
- Trials, plans, audio-hour metering; retention/export/deletion; audit log; weekly digest

## Architecture
TypeScript modular monolith (web + worker) on PostgreSQL with row-level-security tenancy (ADR-002, Type-1), a
Postgres-backed job queue, S3-compatible storage, and provider abstractions for speech-to-text and LLM extraction with an
eval harness gating changes. Stripe for billing with an internal usage ledger.

## Plan
14 capabilities in 9 dependency phases. Phase 0 platform; Phase 1 identity + eval harness (in parallel); Phase 2
isolation; Phase 3 ingestion, billing; Phase 4 transcription, governance; Phase 5 extraction; Phase 6 queue, trends; then
rep view, notifications, launch readiness. No calendar commitments; the pilot (EXP-001) gates the paid launch.

## Risks
1. Recording consent and privacy obligations (R-001): attestation, retention, legal review before launch.
2. Cross-tenant exposure (R-002): RLS + isolation suite on every data path.
3. AI insight quality and cost (R-003, R-004): eval gating, evidence quotes, metering and cost limits.

## Launch
Readiness: INSUFFICIENT_EVIDENCE (nothing built). 42 production checks apply (3 are not applicable: mobile platform matrix, app-store listing, client-only error opt-out). Open founder decision: pricing model
(per-seat + allowance recommended vs usage-based).
