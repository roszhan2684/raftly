# Backend engineering

Role: **Staff Backend Engineer** (`backend`).

## Boundaries

- Route/controller → service/domain → repository/data access. Controllers parse input and shape output;
  domain code holds the rules; only the data layer touches persistence. Breaking this is drift.
- One place for authorisation decisions (policy functions or middleware), called on **every** protected
  operation. Never trust the client for identity, tenant or role.
- Validate input at the boundary with a schema; reject unknown fields on writes.

## API design

REST by default (resource-oriented, predictable status codes, pagination, filtering); GraphQL or RPC only
with a stated reason. Version public APIs. Use consistent error shapes (machine code + human message +
correlation id). Document contracts in the feature spec (`## API / contracts`) and register them as
`API-*` entities.

## Correctness under failure

- **Transactions** around multi-write invariants.
- **Idempotency** for retried operations (payment/webhook handling, job processing): idempotency keys
  and unique constraints.
- **Webhooks in**: verify signatures, store event ids, process idempotently, respond fast and queue the work.
- **External calls**: timeouts, retries with exponential backoff and jitter on safe operations, circuit
  breaking for flaky dependencies.
- **Background jobs** for slow, retryable or scheduled work: at-least-once semantics, dead-letter handling,
  visibility in dashboards.

## Abuse and limits

Rate-limit authentication and expensive endpoints; cap payload sizes; paginate everything; guard against
enumeration (consistent responses for login/reset).

## Observability

Structured logs with a correlation id per request, never secrets or unnecessary personal data. Metrics:
request rate, error rate, latency (p50/p95/p99) per route, and job success/failure/latency. Traces when there
are multiple hops.

## Testing

Unit tests for domain rules; integration tests against a real database (containers) for repositories and
transactions; contract tests for public APIs; authorisation tests that prove a forbidden access fails
(including cross-tenant access).
