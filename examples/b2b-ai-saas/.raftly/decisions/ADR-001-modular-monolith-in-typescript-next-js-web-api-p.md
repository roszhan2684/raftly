---
id: ADR-001
title: "Modular monolith in TypeScript: Next.js web/API plus a background worker"
owner_role: architect
date: 2026-10-24
status: ACCEPTED
decision_type: RECOMMEND
impact: high
reversibility: medium
type1: true
confidence: 82
affects:
  - REQ-003
  - REQ-004
  - REQ-005
supersedes: []
superseded_by: null
evidence:
  - research/architecture-options.md
category: architecture
revisit_trigger: A component needs independent scaling or a separate team owns it
---
# ADR-001 — Modular monolith in TypeScript: Next.js web/API plus a background worker

- **Owner role:** architect
- **Decision type:** RECOMMEND · **Impact:** high · **Reversibility:** medium · **Confidence:** 82/100

## Context
SalesLens needs a web app, an API, and slow, retryable background work (transcription and AI analysis that take minutes per call). The team is small; the expected scale for V1 is tens of organizations and thousands of calls per month.

## Options considered
| Option | Pros | Cons | Fit |
|---|---|---|---|
| A. Modular monolith: Next.js (UI + API routes) + one worker process, shared TypeScript domain modules | one language, one repo, simple deploys, clear module boundaries | needs discipline to keep modules separate | **Best** |
| B. Separate services (ingest, transcription, analysis, web) | independent scaling | distributed failure modes, ops overhead, no team boundary to justify it | Premature |
| C. Serverless functions only | no servers | long jobs fit poorly; harder local dev; per-invocation limits | Poor for multi-minute jobs |

## Decision
One repository and two process types from the same codebase: `web` (Next.js) and `worker` (job consumers). Domain modules (`orgs`, `calls`, `transcripts`, `insights`, `billing`, `governance`) with enforced import boundaries.

## Rationale
The simplicity ladder, rung 4 (monolith + worker), satisfies every V1 requirement. Long jobs live in the worker (ADR-005). Boundaries keep a later extraction possible.

## Supporting evidence
Workload estimate in COST.md and ARCHITECTURE.md scaling assumptions. Framework capabilities to re-verify at implementation (current Next.js major version).

## Rejected alternatives
B (no independent scaling need or team boundary today), C (multi-minute jobs).

## Consequences
- Deploy targets need to run a long-lived worker (not only serverless).
- Module boundaries are enforced with lint rules; violations are architecture drift.
- OpenTelemetry instrumentation spans web and worker.

## Revisit trigger
A component needs independent scaling or a separate team owns it.

## Affected requirements / features
REQ-003, REQ-004, REQ-005 · F002, F003, F004
