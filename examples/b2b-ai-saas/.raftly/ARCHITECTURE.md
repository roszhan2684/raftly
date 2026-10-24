# Architecture Document — SalesLens

## Context
Actors: Admins, Managers, Reps (browser). External systems: Zoom (OAuth + webhooks), speech-to-text provider,
LLM provider (Anthropic API), Stripe, transactional email provider, object storage, error tracking/telemetry backend.

## System overview
A TypeScript modular monolith (ADR-001): the `web` process (Next.js UI + API routes) and the `worker` process
(pg-boss consumers) share domain modules. PostgreSQL holds all relational data with row-level-security tenancy
(ADR-002) and the job queue (ADR-005). Audio lives in S3-compatible storage under per-tenant prefixes (ADR-004).
AI calls go through provider interfaces (ADR-006, ADR-007) gated by an eval harness (ADR-008).

```text
 Browser ──HTTPS──► web (Next.js UI + API) ──► domain modules ──► PostgreSQL (RLS, pg-boss queue)
    │                      │   ▲                                      ▲
    │ presigned upload     │   └── Stripe/Zoom webhooks (verified, idempotent)
    ▼                      │ enqueue
 Object storage ◄──────────┼──────────── worker (pg-boss consumers)
 (org/{id}/...)            │               ├─ ingest/import (Zoom API)
                           │               ├─ transcribe ─► TranscriptionProvider ─► STT API
                           │               ├─ extract ────► ExtractionProvider ─► LLM API
                           │               ├─ meter usage ─► Stripe
                           │               └─ retention / export / digests
                           └─ OpenTelemetry traces + metrics, error tracking (PII-scrubbed)
```

## Boundaries
Modules: `orgs` (identity, memberships, roles), `calls` (ingestion, storage, consent), `transcripts`, `insights`
(extraction, reviews, notes), `trends` (read models), `billing`, `governance` (retention, export, deletion, audit),
`notifications`. Rules: modules call each other through exported service functions only; only repositories touch
the database; every repository requires an org context; provider SDKs live only in `adapters/`.

## Stack
| Concern | Choice | ADR | Notes |
|---|---|---|---|
| Web + API | Next.js (TypeScript) | ADR-001 | one deployable + worker |
| Background jobs | pg-boss on Postgres | ADR-005 | retries, DLQ, idempotency keys |
| Database | PostgreSQL + RLS, Drizzle ORM | ADR-002 | Type-1 |
| Auth | Auth.js (magic link, Google/Microsoft OIDC) | ADR-003 | SAML on revisit trigger |
| Object storage | S3-compatible, per-tenant prefixes | ADR-004 | lifecycle + retention job |
| Transcription | Provider interface; provider via spike | ADR-006 | PROPOSED dependency |
| AI extraction | Anthropic API behind `ExtractionProvider` | ADR-007 | model chosen by eval |
| AI quality | Eval harness + golden dataset | ADR-008 | launch blocker |
| Billing | Stripe Billing + internal usage ledger | ADR-010 | pricing model: founder decision open |
| Integrations | Zoom only | ADR-011 | CRM deferred |
| Observability | OpenTelemetry + error tracking | ADR-001 | PII scrubbing |
| Email | Transactional provider (chosen in N013) | — | SPF/DKIM/DMARC |

## Data
PostgreSQL is the system of record; audio in object storage; transcripts and insights in Postgres. Tenancy:
shared schema + `org_id` + RLS. Details in DATA_MODEL.md.

## Security
Server-side authorization through policy functions + RLS; database sessions; secrets in the platform secret store;
encrypted integration tokens; verified webhooks; transcript content treated as untrusted model input. Details in SECURITY.md.

## Integrations
| Integration | Direction | Auth | Failure handling |
|---|---|---|---|
| Zoom | inbound webhooks + API pulls | OAuth (min scopes), encrypted tokens | retries; token revocation → integration status "reconnect" |
| STT provider | outbound | API key (secret store) | retries/backoff; permanent failure surfaced on the call |
| LLM provider | outbound | API key | retries; fallback model optional; "insights unavailable" |
| Stripe | both | API key + webhook signature | idempotent events; billing outage never blocks reads |
| Email | outbound + bounce webhooks | API key | retries; suppression list |

## Reliability
Initial SLOs (staging-measured before launch): web availability 99.5% monthly; p95 API < 500 ms for queue and trends;
call ready (upload → insights) p95 < 60 minutes for calls ≤ 1 hour. Error budget policy: freeze features when breached.

## Environments
local (docker compose: Postgres, storage emulator) · preview per PR (no production data) · staging (production-like,
synthetic data) · production. Migrations run in CI against staging first.

## Failure behavior
| Critical path | Failure | User sees | System does | Detected by |
|---|---|---|---|---|
| Upload | interrupted | resume prompt | multipart resume | upload failure metric |
| Zoom import | token revoked | integration needs reconnect | stop polling; notify Admin | import error alert |
| Transcription | provider down/timeout | "Transcribing… delayed" | retry w/ backoff, DLQ after 3 | queue age alert |
| Extraction | invalid output | items omitted, "insights unavailable" if none | discard + retry; fallback model | schema-failure rate alert |
| Extraction | cost limit hit | "Analysis paused, contact admin" | pause org processing | cost alert |
| Billing webhook | duplicate/out of order | nothing | idempotent processing | webhook failure alert |
| Tenancy | missing org context | 403 | deny by default (RLS) | authz denial spike alert |

## Scaling assumptions
V1 upper range: ~30 orgs, ~600 reps, ~6,000 audio hours/month (research/architecture-options.md). First expected
bottlenecks: provider rate limits and cost, then Postgres connection count from worker concurrency. Triggers in ADR-001/ADR-005.

## Not applicable
Microservices, Kubernetes, Redis, a separate search engine, a vector database. None has a demonstrated V1 need.
