# Data architecture

Role: **Principal Data Engineer / Database Architect** (`data`).

## Store selection

Default to a relational database (PostgreSQL is a strong general default; verify hosting options) when
data has relationships, needs integrity, or will be queried in unanticipated ways. Choose document, key-value,
search or vector stores for a demonstrated access pattern, not by default. Adding a second store is a Type-1
decision with an ADR. (Postgres extensions such as full-text search and pgvector often defer the need.)

## Tenancy models (multi-tenant products, Type-1)

| Model | Isolation | Cost/ops | Use when |
|---|---|---|---|
| Shared schema + `tenant_id` on every row | logical; enforce with row-level security or a mandatory scoped repository | lowest | default for SMB/mid-market SaaS |
| Schema per tenant | stronger logical | migrations multiply | moderate tenant counts, per-tenant customisation |
| Database per tenant | strongest | highest | enterprise/regulatory isolation, data residency per tenant |

Whatever the model: tenant scoping lives in the data layer (not each query author's memory), tests prove
cross-tenant reads and writes fail, and background jobs carry tenant context explicitly.

## Schema design

Name things after the domain; use surrogate keys plus natural unique constraints; timestamps in UTC
(`created_at`, `updated_at`); soft delete only when the product needs undo or audit (it complicates
uniqueness and deletion obligations). Index for the actual query patterns (verify with EXPLAIN), and add
foreign keys and check constraints for integrity.

## Migrations (expand/contract)

1. Expand: add new columns/tables (nullable or with defaults); deploy code that writes both.
2. Backfill in batches, idempotently.
3. Switch reads; verify.
4. Contract: remove old paths in a later release.
Never drop or rewrite data in the same deploy that stops using it. Every migration has a rollback or a
compensating plan, and is tested on production-like data for large tables.

## Data lifecycle (spec §24)

For each material data class, a row in DATA_MODEL.md:

| Data class | Source | Owner | Sensitivity | Storage | Access | Tenant boundary | Retention | Backups | Restore | Export | Deletion | Logs | Analytics use |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

For regulated or sensitive systems this table is a required gate (G-PRIV-INVENTORY, G-PRIV-SENSITIVE).

## Backups and restore

Automated backups with point-in-time recovery where available; retention matched to the product's
promises; **a restore that has actually been performed and timed** (G-RESTORE). Untested backups are
assumptions.

## Analytics data

Keep analytics separate from operational tables (events, warehouse or product-analytics tool); avoid
personal data in events where possible; filter internal traffic; document event names next to features.
