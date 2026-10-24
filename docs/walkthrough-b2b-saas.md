# Walkthrough: B2B AI sales-coaching platform

Input:

```text
/raftly
Build a B2B AI sales coaching platform that ingests sales calls and identifies objections, competitors, and coaching opportunities.
```

Result: [examples/b2b-ai-saas](../examples/b2b-ai-saas) ("SalesLens").

## What is different from the calculator (by design)
| Concern | Calculator | SalesLens |
|---|---|---|
| Applicable production checks | 16 | 42 |
| Tenancy / RBAC | none | orgs, Admin/Manager/Rep, Postgres RLS (ADR-002, Type-1) |
| Background work | none | Postgres-backed queue (ADR-005) |
| AI | none | STT + LLM behind provider interfaces; eval gating with thresholds (ADR-006–008) |
| Billing | none | Stripe + internal usage ledger (ADR-010); **pricing model left as a founder decision** |
| Compliance | none | GDPR + recording-consent readiness checklist, professional review required |
| Build graph | 7 nodes / 4 phases | 14 nodes / 9 phases |

## Highlights
- **[Principal AI/ML Engineer]** builds the eval harness (N006) in parallel with identity work, so the riskiest
  assumption (A-003, extraction quality) is tested before UI is built on top of it.
- Every insight must carry a verbatim quote validated against the transcript (hallucination guard, R-003), and transcripts are
  treated as untrusted model input (prompt injection, R-006).
- **[Principal Security Engineer]** requires an isolation suite that every later node extends (G-TENANT-ISOLATION).
- Provider choices that couldn't be verified are explicitly **not verified**. The N005/N007 spikes turn them into evidence.
- **Founder decision**: pricing (per-seat + allowance recommended vs usage-based). Billing supports both. Changing it later
  runs `raftly records change-requirement REQ-009 ...` (eval 10).

## Resume (Demo C)
Reopen Claude Code in the repo and run `/raftly`. `raftly context` recognises BLUEPRINT_COMPLETE, the 12 ADRs and the open founder
decision, and recommends `START N001 Platform foundation`, with no re-planning.

## Override (Demo D)
"Use MongoDB instead of PostgreSQL." → `raftly decisions override ADR-002 --chosen MongoDB --reason ... --consequences ...`
preserves the original recommendation, supersedes ADR-002, and records consequences (tenant isolation without RLS, reporting
pipelines, transactions) and new risks.
