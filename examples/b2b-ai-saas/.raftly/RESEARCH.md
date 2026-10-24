# Research — SalesLens

| # | Question | Finding | Source(s) | Checked | Confidence | Informs |
|---|---|---|---|---|---|---|
| 1 | How to enforce tenant isolation in Postgres? | Row security policies restrict rows per role/session setting; combined with app-level scoping for defence in depth. | https://www.postgresql.org/docs/current/ddl-rowsecurity.html (prior knowledge; **re-verify** syntax and pooler interaction at N003) | — | High (concept) | ADR-002 |
| 2 | Postgres-backed job queue viable at V1 volume? | pg-boss provides durable jobs, retries, scheduling on Postgres (MIT). | https://github.com/timgit/pg-boss (prior knowledge; **re-verify** version/features) | — | Medium-high | ADR-005 |
| 3 | Auth library for magic link + OIDC with our own org model? | Auth.js supports email and OAuth/OIDC providers with database adapters. | https://authjs.dev (prior knowledge; **re-verify** Drizzle adapter and provider config) | — | Medium-high | ADR-003 |
| 4 | Billing that supports per-seat and usage-based pricing? | Stripe Billing supports subscriptions, quantities, trials and usage-based billing. | https://docs.stripe.com/billing (prior knowledge; **re-verify** current usage-based APIs) | — | Medium-high | ADR-010 |
| 5 | Which speech-to-text provider? | **Not researched for this blueprint.** Must compare WER, diarization, language support, retention/training terms, and pricing in the N005 spike. | research/ai-providers.md | — | — | ADR-006 |
| 6 | Competitor landscape and price points | **Not verified.** Enterprise conversation-intelligence suites exist; mid-market positioning assumed. Needs dated research before pricing decisions. | — | — | Low | Positioning, pricing founder decision |
| 7 | Recording consent obligations | Consent rules vary by jurisdiction (some require all-party consent). Product must support customers' compliance; **requires legal review**. | Prior knowledge; legal review required | — | Medium | REQ-010, ADR-012, R-001 |
| 8 | LLM provider capabilities, limits, data terms | **Not verified here.** Confirm current model capabilities, context limits, structured outputs, pricing and data-use terms from official docs at N007. | research/ai-providers.md | — | — | ADR-007 |

## Notes
Prior-knowledge items are leads, not evidence. They don't support PASS statuses. Longer notes: `research/`.
