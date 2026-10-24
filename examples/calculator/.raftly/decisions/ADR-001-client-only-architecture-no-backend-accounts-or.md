---
id: ADR-001
title: "Client-only architecture: no backend, accounts or database"
owner_role: architect
date: 2026-10-24
status: ACCEPTED
decision_type: RECOMMEND
impact: high
reversibility: medium
type1: true
confidence: 92
affects:
  - REQ-004
  - REQ-011
supersedes: []
superseded_by: null
evidence:
  - research/platform-and-precision.md
category: architecture
revisit_trigger: A validated need for cross-device sync, accounts or shared data (A-004 invalidated)
---
# ADR-001 — Client-only architecture: no backend, accounts or database

- **Owner role:** architect
- **Decision type:** RECOMMEND · **Impact:** high · **Reversibility:** medium · **Confidence:** 92/100

## Context
Tally evaluates arithmetic locally, keeps history on the device and must work offline (REQ-004). No V1
requirement involves shared data, identity or server-side computation (REQ-011 excludes accounts and sync).

## Options considered
| Option | Pros | Cons | Fit |
|---|---|---|---|
| A. Client-only (static web + app binaries, local storage) | zero server cost, offline by construction, no personal data, smallest attack surface | no sync | **Best fit for V1 requirements** |
| B. Client + BaaS (auth + sync) | cross-device history | accounts, privacy obligations, cost, outage modes; no requirement asks for it | Over-scoped |
| C. Server-side evaluation API | central logic | latency, offline impossible, pointless for arithmetic | Rejected |

## Decision
Client-only. The web build is a static site; mobile apps are self-contained. History lives in on-device storage.

## Rationale
Constitution 4–5: the simplest architecture that satisfies actual requirements. A backend would add accounts,
personal data, uptime and cost with no V1 user outcome.

## Supporting evidence
Requirements REQ-004 and REQ-011; assumption A-004 (sync not needed in V1, confidence 70).

## Rejected alternatives
B (no requirement; creates privacy and operational burden). C (breaks offline and adds latency).

## Consequences
- Production-gate server checks (backups, auth, rate limiting, monitoring, SLOs) are NOT_APPLICABLE.
- History is per device; clearing app data clears history. Stated in the empty state and store listing.
- Adding sync later is a new Type-1 decision (accounts, data model, privacy work).

## Revisit trigger
A validated need for cross-device sync, accounts or shared data (A-004 invalidated).

## Affected requirements / features
REQ-004, REQ-011 · F003, F006
