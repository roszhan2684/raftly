# Decision Book — SalesLens

Major product, design and architecture decisions. Each row links to its ADR. Regenerate the table with `raftly decisions book`.

## Decisions
<!-- generated:decisions:start -->
| ID | Decision | Why (short) | Owner | Type | Confidence | Reversibility | Status |
|---|---|---|---|---|---|---|---|
| [ADR-001](decisions/ADR-001-modular-monolith-in-typescript-next-js-web-api-p.md) | Modular monolith in TypeScript: Next.js web/API plus a background worker | The simplicity ladder, rung 4 (monolith + worker), satisfies every V1 requirement. | architect | RECOMMEND · Type-1 | 82 | medium | ACCEPTED |
| [ADR-002](decisions/ADR-002-postgresql-with-shared-schema-tenancy-enforced-b.md) | PostgreSQL with shared-schema tenancy enforced by row-level security | Defence in depth: application scoping plus database-enforced policies, so one missed `WHERE` clause cannot leak data. | data | RECOMMEND · Type-1 | 85 | low | ACCEPTED |
| [ADR-003](decisions/ADR-003-auth-js-with-magic-links-and-google-microsoft-oi.md) | Auth.js with magic links and Google/Microsoft OIDC; organizations and roles in our database | Keeps identity, tenancy and authorization in one model with no recurring cost while the product is validated. | security | RECOMMEND · Type-1 | 75 | medium | ACCEPTED |
| [ADR-004](decisions/ADR-004-s3-compatible-object-storage-with-per-tenant-pre.md) | S3-compatible object storage with per-tenant prefixes, encryption and lifecycle retention | Standard and portable (low lock-in thanks to the de-facto S3 API). | platform | RECOMMEND | 85 | high | ACCEPTED |
| [ADR-005](decisions/ADR-005-postgres-backed-job-queue-pg-boss-instead-of-red.md) | Postgres-backed job queue (pg-boss) instead of Redis or a cloud queue | One fewer system to run (Constitution 5); enqueueing happens in the same transaction as the call record. | backend | RECOMMEND | 80 | high | ACCEPTED |
| [ADR-006](decisions/ADR-006-speech-to-text-through-a-provider-interface-prov.md) | Speech-to-text through a provider interface; provider selected by a diarization and WER spike | Speed to a reliable pipeline matters more than owning a model in V1. The spike turns an unverified choice into evidence. | ai-ml | RECOMMEND · Type-1 | 65 | medium | ACCEPTED |
| [ADR-007](decisions/ADR-007-llm-extraction-with-structured-outputs-evidence.md) | LLM extraction with structured outputs, evidence quotes and versioned prompts behind a provider abstraction | Best quality-to-effort for V1. Evidence quotes make insights verifiable (R-003). | ai-ml | RECOMMEND · Type-1 | 75 | medium | ACCEPTED |
| [ADR-008](decisions/ADR-008-evaluation-gating-versioned-golden-dataset-and-t.md) | Evaluation gating: versioned golden dataset and thresholds block prompt or model changes | Turns AI quality into an evidence-gated, regression-tested property, like any other test (Constitution 15). | ai-ml | RECOMMEND · Type-1 | 85 | high | ACCEPTED |
| [ADR-009](decisions/ADR-009-design-direction-a-coaching-queue-as-the-landing.md) | Design direction A: coaching queue as the landing view, call detail as drill-in | The primary job is "act on coaching moments without listening to every call". | design-director | RECOMMEND | 70 | high | ACCEPTED |
| [ADR-010](decisions/ADR-010-stripe-for-subscriptions-trials-seats-and-metere.md) | Stripe for subscriptions, trials, seats and metered audio hours | Supports both candidate pricing models without re-architecture; widely documented. | gtm | RECOMMEND | 78 | medium | ACCEPTED |
| [ADR-011](decisions/ADR-011-zoom-is-the-only-v1-integration-crm-linking-defe.md) | Zoom is the only V1 integration; CRM linking deferred | Prove the core job with the smallest integration surface. The pilot tells us which integration comes second. | product-director | RECOMMEND | 72 | high | ACCEPTED |
| [ADR-012](decisions/ADR-012-retention-defaults-and-recording-consent-attesta.md) | Retention defaults and recording-consent attestation | Minimisation and controller support without blocking the core flow. | privacy | RECOMMEND | 70 | medium | ACCEPTED |

Generated from `decisions/` by `decisions.py book`. Edit the ADRs, not this table.
<!-- generated:decisions:end -->

## Open founder decisions
- **Pricing model**: per-seat with an included audio-hour allowance (Raftly recommendation: predictable for buyers,
  allowance protects margin) or usage-based per audio hour. Billing (ADR-010) supports both; the decision affects
  plans, the pricing page, entitlement copy and the unit-economics target in COST.md. Switching later runs the
  Requirement Change Engine on REQ-009.
