# Cost Model — SalesLens

Prices are **not verified** in this blueprint. Exact pricing requires fresh research (N005/N007 spikes record dated
prices). The table describes cost drivers and shape; amounts are filled in from research, never guessed.

| Component | Free tier / current | Cost driver | 100 users | 1k users | 10k users | 100k users | Assumptions | Uncertainty |
|---|---|---|---|---|---|---|---|---|
| Speech-to-text | provider-dependent | audio hours | ~1k h/mo | ~10k h/mo | ~100k h/mo | ~1M h/mo | 15 calls × 40 min per rep-week | high until spike |
| LLM extraction | provider-dependent | tokens per audio hour | ∝ audio hours | ∝ | ∝ | ∝ | ~2 passes over transcript tokens | high until eval/model choice |
| Postgres | managed tier | storage + compute | small | small-medium | medium (read replicas?) | needs re-architecture review | transcripts ~10 KB/min | medium |
| Object storage | per GB-month + egress | audio GB × retention | low | low-medium | medium | high | ~0.5 GB per 10 h audio (codec-dependent) | medium |
| Web + worker hosting | small instances | concurrency | low | low | medium | high | workers scale with audio hours | medium |
| Stripe | % of revenue (verify) | revenue | — | — | — | — | standard pricing | low |
| Email | free tier likely | emails/month | low | low | low-medium | medium | weekly digests | low |

## Unit economics target
Processing cost (STT + LLM + storage) per seat per month ≤ 15% of the seat price (A-005). Measured with pilot
metering (`ai_runs`, `usage_events`) and compared to the founder's pricing decision.

## Migration risk
STT and LLM providers sit behind interfaces (ADR-006/007), so switching is an eval + config exercise. Storage uses the
S3 API (low lock-in). Stripe lock-in is medium (internal usage ledger mitigates it).
