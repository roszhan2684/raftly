---
id: ADR-009
title: "Design direction A: coaching queue as the landing view, call detail as drill-in"
owner_role: design-director
date: 2026-10-24
status: ACCEPTED
decision_type: RECOMMEND
impact: medium
reversibility: high
type1: false
confidence: 70
affects:
  - REQ-006
  - REQ-008
supersedes: []
superseded_by: null
evidence: []
category: design
revisit_trigger: EXP-001 shows managers start from trends rather than the queue
---
# ADR-009 — Design direction A: coaching queue as the landing view, call detail as drill-in

- **Owner role:** design-director
- **Decision type:** RECOMMEND · **Impact:** medium · **Reversibility:** high · **Confidence:** 70/100

## Context
Three directions in DESIGN.md: A Coaching queue (inbox), B Call-centric library, C Team dashboard first. They differ in information architecture and the primary workflow.

## Options considered
| Direction | Best for | Weakness |
|---|---|---|
| A. Coaching queue | managers acting weekly on specific moments (the core job) | less "big picture" on landing |
| B. Call library | browsing calls | makes managers do the listening the product should save |
| C. Dashboard first | leaders reporting upward | insight → action loop is indirect |

## Decision
Direction A as the manager home; B as the call detail view (transcript + timeline + insights); C as the Trends tab. Reps land on their own coaching feed.

## Rationale
The primary job is "act on coaching moments without listening to every call". A puts that action first, which also generates the accept/dismiss signal for quality monitoring.

## Supporting evidence
Assumption A-001 (confidence 60); validated by EXP-001.

## Rejected alternatives
B and C as landing views (kept as secondary views).

## Consequences
Queue states (new, accepted, shared, dismissed) drive both UX and data. Dismiss reasons feed the eval dataset (with consent).

## Revisit trigger
EXP-001 shows managers start from trends rather than the queue.

## Affected requirements / features
REQ-006, REQ-008 · F005, F006, F007
