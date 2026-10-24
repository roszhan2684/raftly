---
id: ADR-005
title: "Design direction B: Modern utility (live expression line + history drawer)"
owner_role: design-director
date: 2026-10-24
status: ACCEPTED
decision_type: RECOMMEND
impact: medium
reversibility: high
type1: false
confidence: 75
affects:
  - REQ-001
  - REQ-006
supersedes: []
superseded_by: null
evidence: []
category: design
revisit_trigger: Beta users find the expression line distracting (EXP-001 interviews)
---
# ADR-005 — Design direction B: Modern utility (live expression line + history drawer)

- **Owner role:** design-director
- **Decision type:** RECOMMEND · **Impact:** medium · **Reversibility:** high · **Confidence:** 75/100

## Context
Three directions were explored in DESIGN.md: A Native minimal, B Modern utility, C Workspace/history-first.
They differ in interaction model, not just styling.

## Options considered
| Direction | Strength | Weakness |
|---|---|---|
| A. Native minimal | zero learning curve | indistinguishable from built-in calculators (R-003) |
| B. Modern utility | live expression line prevents errors; history one swipe away; still familiar | slightly busier display |
| C. Workspace/history-first | powerful re-running and editing of lines | heavy on phones; more build effort |

## Decision
Direction B on all surfaces. C's editable history is a candidate for a tablet/desktop layout after V1.

## Rationale
B directly expresses the differentiators: you see exactly what will be computed (precedence, percent) and can
reuse results. That reduces the confusion risk R-005 while keeping the familiar keypad.

## Supporting evidence
Product research summary in RESEARCH.md (common user complaints about not seeing the full expression).
Not verified with users yet: EXP-001 interviews validate it.

## Rejected alternatives
A (no differentiation), C (phone ergonomics, scope).

## Consequences
The display needs two lines (expression + result) with careful truncation and screen-reader announcements.

## Revisit trigger
Beta users find the expression line distracting (EXP-001 interviews).

## Affected requirements / features
REQ-001, REQ-006 · F002, F003
