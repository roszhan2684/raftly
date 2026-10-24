---
id: ADR-005
title: Postgres-backed job queue (pg-boss) instead of Redis or a cloud queue
owner_role: backend
date: 2026-10-24
status: ACCEPTED
decision_type: RECOMMEND
impact: medium
reversibility: high
type1: false
confidence: 80
affects:
  - REQ-004
  - REQ-005
supersedes: []
superseded_by: null
evidence:
  - "https://github.com/timgit/pg-boss"
category: architecture
revisit_trigger: Sustained job throughput or latency limits measured in production
---
# ADR-005 — Postgres-backed job queue (pg-boss) instead of Redis or a cloud queue

- **Owner role:** backend
- **Decision type:** RECOMMEND · **Impact:** medium · **Reversibility:** high · **Confidence:** 80/100

## Context
Ingestion, transcription and analysis are multi-step, retryable, minutes-long jobs. V1 volume: thousands of jobs per day at most.

## Options considered
| Option | Ops | Durability | Fit |
|---|---|---|---|
| A. Postgres-backed queue (pg-boss) | no new infrastructure | transactional with our data | **Best at V1 volume** |
| B. Redis-based queue (BullMQ) | adds Redis | needs persistence configuration | Viable |
| C. Cloud queue service | managed | strong | lock-in, more moving parts |

## Decision
pg-boss in the worker process. Jobs carry `org_id` and set the RLS context. Retries with exponential backoff, dead-letter queue, and singleton keys for idempotency (`call_id + step`).

## Rationale
One fewer system to run (Constitution 5); enqueueing happens in the same transaction as the call record.

## Supporting evidence
pg-boss repository (MIT; prior knowledge, verify the current version and features at implementation).

## Rejected alternatives
B (extra infrastructure without a demonstrated need), C (lock-in, complexity).

## Consequences
Queue load shares the database; monitor queue depth and job latency (alerts in platform-sre).

## Revisit trigger
Sustained job throughput or latency limits measured in production.

## Affected requirements / features
REQ-004, REQ-005 · F002, F003, F004
