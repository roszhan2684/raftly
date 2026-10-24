---
id: ADR-004
title: S3-compatible object storage with per-tenant prefixes, encryption and lifecycle retention
owner_role: platform
date: 2026-10-24
status: ACCEPTED
decision_type: RECOMMEND
impact: medium
reversibility: high
type1: false
confidence: 85
affects:
  - REQ-003
  - REQ-011
supersedes: []
superseded_by: null
evidence: []
category: infrastructure
---
# ADR-004 — S3-compatible object storage with per-tenant prefixes, encryption and lifecycle retention

- **Owner role:** platform
- **Decision type:** RECOMMEND · **Impact:** medium · **Reversibility:** high · **Confidence:** 85/100

## Context
Recordings are large (up to 3 h) and contain personal data. They must be stored durably, isolated per tenant, deleted on schedule (REQ-011), and never served publicly.

## Options considered
| Option | Pros | Cons |
|---|---|---|
| S3-compatible object storage (any major provider) | durable, cheap per GB, lifecycle rules, presigned URLs, portable API | another service |
| Database blobs | one store | bloats Postgres, backups and costs |
| Local disk on servers | none | not durable, not scalable |

## Decision
An S3-compatible bucket per environment, keys `org/{org_id}/calls/{call_id}/...`, server-side encryption, private ACLs, short-lived presigned URLs for direct upload and playback, lifecycle rules plus an application retention job (ADR-012).

## Rationale
Standard and portable (low lock-in thanks to the de-facto S3 API). Presigned direct uploads keep large files off the web server.

## Supporting evidence
Engineering judgment; provider and region chosen in N001 (record the region with the data-residency founder decision when it arises).

## Rejected alternatives
DB blobs and local disk (durability, cost).

## Consequences
- Upload is client → storage via presigned multipart URLs; the server validates on completion.
- Retention is enforced both by lifecycle rules and by the governance job, so deletions are provable (F009).

## Revisit trigger
Not applicable beyond the provider/region choice (highly reversible).

## Affected requirements / features
REQ-003, REQ-011 · F002, F009
