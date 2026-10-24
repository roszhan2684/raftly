# Security — SalesLens

## Summary
SalesLens processes confidential sales conversations containing personal data of customers' employees and prospects.
The security posture focuses on tenant isolation, server-side authorization, protection of recordings and integration
credentials, webhook integrity, and AI-specific risks. This document records readiness, not certification. Evidence is
collected per node and in N014. An independent penetration test is recommended before onboarding enterprise customers.

## Threat model
| Asset | Actor | Entry point | Threat | Control | Status |
|---|---|---|---|---|---|
| Tenant data | authenticated user of org A | any API/job | cross-tenant read/write | RLS + scoped repositories + isolation suite (ADR-002) | planned (N003) |
| Rep privacy | rep | calls/notes APIs | view teammates' calls | visibility in RLS + policy tests | planned (N009) |
| Recordings | internet attacker | storage URLs | enumeration/leak | private bucket, org prefixes, short-lived presigned URLs | planned (N004) |
| Zoom tokens | attacker with DB read | integrations table | token theft | encryption at rest with a key in the secret store, minimal scopes | planned (N004) |
| Billing/state | attacker | webhooks | forged/replayed events | signature verification + event dedupe | planned (N004, N011) |
| Insight integrity | prospect speech / malicious upload | transcript → LLM | prompt injection | no tools, schema-only output, verbatim-quote validation | planned (N007) |
| AI spend | abusive user | uploads | cost exhaustion | allowance + per-org cost limits + rate limits | planned (N011) |
| Accounts | attacker | sign-in | credential stuffing / enumeration | passwordless, rate limits, generic errors | planned (N002) |
| Platform | supply chain | dependencies | malicious package | lockfile, audit in CI, minimal dependencies | planned (N001) |

## Controls
| Control | Applies? | Status | Evidence |
|---|---|---|---|
| Server-side authorization on every operation | yes | UNVERIFIED | N003/N009 test suites |
| Tenant isolation tests | yes | UNVERIFIED | isolation suite |
| Secrets management | yes | UNVERIFIED | N001 |
| Input validation at boundaries | yes | UNVERIFIED | schema validation on every route |
| File-upload restrictions | yes | UNVERIFIED | N004 |
| Webhook verification + idempotency | yes | UNVERIFIED | N004, N011 |
| Rate limiting | yes | UNVERIFIED | N002, N004 |
| Security headers / CSP | yes | UNVERIFIED | N001/N014 |
| AI prompt-injection controls | yes | UNVERIFIED | N007 injection suite |
| Audit log | yes | UNVERIFIED | N012 |

## Data protection
TLS everywhere; encryption at rest for the database and storage (provider-managed keys); application-level encryption
for integration tokens; personal data minimized in logs and telemetry (IDs only).

## Secrets management
Platform secret store per environment; no secrets in the repo or client bundles; rotation runbook for provider keys and
the token-encryption key (G-F20-SECRETS).

## Dependency policy
Lockfile committed; dependency audit in CI; new dependencies require a dependencies.yaml entry with licence and purpose.

## Incident contact and disclosure
security@ address on the website; incident runbook (postmortems via `raftly records new postmortem`); customer
notification obligations per DPA (requires legal review).

## Open risks
R-002 cross-tenant exposure (mitigation planned), R-006 prompt injection, R-001 recording consent (legal).

## Requires professional review
- Penetration test before enterprise onboarding.
- Legal review of DPA, terms, privacy policy and consent language (see COMPLIANCE_READINESS.md).
