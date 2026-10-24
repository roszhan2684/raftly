# Privacy — SalesLens

Engineering readiness, not legal advice.

## Data inventory
| Data class | Purpose | Storage | Access | Processors | Retention | Deletion |
|---|---|---|---|---|---|---|
| Account data | authentication, collaboration | Postgres | self, Admins | email provider, hosting | account life | account/org deletion |
| Call audio | transcription, playback | object storage | per visibility | STT provider, hosting/storage | org setting (default 12 months) | retention job, call/org deletion |
| Transcripts | insights, review | Postgres | per visibility | LLM provider (processing), hosting | until deletion | cascade |
| Insights and coaching notes | coaching | Postgres | rep, managers, Admins | hosting | until deletion | cascade |
| Integration tokens | Zoom import | Postgres (encrypted) | system | — | until disconnect | on disconnect |
| Billing data | subscriptions | Stripe + Postgres ids | Admins | Stripe | accounting period (confirm) | per accounting rules |

## Minimisation decisions
No voiceprints or speaker biometrics; no sentiment profiling of individuals in V1; telemetry uses IDs only; emails
contain short quotes only if the org allows it.

## User rights handling
Org Admins export and delete data (F009); individual users can delete their account (memberships removed; authored notes
retained or deleted per org setting, to be confirmed in legal review); support process for data-subject requests forwarded to the controller (the customer).

## Telemetry and consent
Product analytics on the logged-in app use first-party, aggregated events without call content; the marketing site uses
privacy-preserving analytics or consent where required (decide in N014 with legal review).

## Logging policy
No transcript text, audio URLs, tokens or emails in logs; request bodies scrubbed in error tracking.
