# Data Model — SalesLens

## Stores
PostgreSQL (system of record, queue), S3-compatible object storage (audio, exports).

## Entities
### orgs
| Field | Type | Constraints | Notes |
|---|---|---|---|
| id | uuid | pk | |
| name | text | not null | |
| retention_audio_days | int | 30–1095, default 365 | ADR-012 |
| consent_policy_text | text | | shown at attestation |
| status | enum | active, read_only, pending_deletion | |

### memberships / teams
`memberships(org_id, user_id, role: admin|manager|rep, status)` unique (org_id, user_id);
`teams(org_id, name)`, `team_members(org_id, team_id, user_id, is_manager)`; `orgs.rep_team_visibility boolean`.

### calls
| Field | Type | Constraints | Notes |
|---|---|---|---|
| id | uuid | pk | |
| org_id | uuid | fk, RLS | |
| rep_user_id | uuid | fk | |
| source | enum | upload, zoom | |
| storage_key | text | `org/{org_id}/calls/{id}/audio` | |
| duration_s | int | ≤ 10800 | |
| content_hash | text | unique (org_id, content_hash) | dedupe |
| status | enum | uploading … ready, failed, deleted | |
| consent_attestation_id | uuid | not null before processing | REQ-010 |

### transcripts, transcript_segments
`transcripts(org_id, call_id, provider, model_version, language)`; `transcript_segments(org_id, call_id, speaker_role: rep|prospect|unknown, start_ms, end_ms, text)`.

### insights, insight_reviews, coaching_notes
`insights(org_id, call_id, type, category, quote, start_ms, speaker_role, confidence, prompt_version, model, status)`;
`insight_reviews(org_id, insight_id, reviewer_id, action, reason)`; `coaching_notes(org_id, insight_id, author_id, body, shared_at, read_at)`.

### billing
`subscriptions(org_id, stripe_customer_id, stripe_subscription_id, status, plan)`; `usage_events(org_id, call_id unique, audio_seconds, reported_at)`; `stripe_events(event_id pk)`.

### governance
`consent_attestations(org_id, user_id, scope, policy_version, created_at)`; `exports(org_id, status, storage_key, expires_at)`; `audit_events(org_id, actor_id, action, target, ip_hash, at)` (append-only); `integrations(org_id, provider, encrypted_tokens, scopes, status)`.

## Tenancy
Shared schema; `org_id` on every tenant table; RLS policies `USING (org_id = current_setting('app.current_org_id')::uuid)`
plus role/visibility predicates for reps; app role is subject to RLS; migration role bypasses. Isolation tests cover every repository.

## Indexes
`calls(org_id, rep_user_id, created_at desc)` (lists) · `insights(org_id, status, created_at)` (queue) ·
`insights(org_id, type, category, created_at)` (trends) · `transcript_segments(call_id, start_ms)` · `usage_events(org_id, reported_at)`.

## Data lifecycle
| Data class | Source | Owner | Sensitivity | Storage | Access | Tenant boundary | Retention | Backups | Restore | Export | Deletion | Logs | Analytics use |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Account data (name, email) | users | customer (controller) / us | personal | Postgres | self, Admins | org + global user | life of account | DB backups | PITR | yes | account/org deletion | ids only | aggregated funnel |
| Call audio | upload/Zoom | customer | personal (third parties), confidential | object storage | per visibility | org prefix | org setting (default 12 mo) | storage versioning off; no extra copies | n/a (re-upload) | yes (links) | job + lifecycle | never | never |
| Transcripts | STT | customer | personal, confidential | Postgres | per visibility | RLS | until deletion | DB backups | PITR | yes | cascade | never | never |
| Insights, notes | AI, managers | customer | personal (employee performance) | Postgres | rep/manager/Admin | RLS | until deletion | DB backups | PITR | yes | cascade | never | counts only |
| Integration tokens | Zoom OAuth | us (credentials) | credentials | Postgres (encrypted) | system | RLS | until disconnect | DB backups (encrypted) | PITR | no | on disconnect/org delete | never | never |
| Usage/billing | system/Stripe | us | business | Postgres + Stripe | Admins | RLS | legal/accounting period (confirm with counsel) | DB backups | PITR | invoices | per accounting rules | ids | MRR |
| Audit events | system | customer + us | security | Postgres | Admins | RLS | 2 years | DB backups | PITR | yes | org deletion (after retention) | — | — |
| Eval dataset | synthetic + consented | us | personal (consented) | private bucket | AI team | n/a | until consent withdrawn | storage | — | — | on withdrawal | never | never |

## Migrations
Drizzle migrations, expand/contract policy, reviewed in PRs, applied to staging first, backward compatible for one release.

## Backup and restore
Managed Postgres automated backups with point-in-time recovery (retention per provider settings, ≥ 7 days target); a quarterly
restore drill into staging with timing recorded (G-RESTORE). Audio is not backed up separately (re-uploadable; deletion must be final).
