---
id: ADR-008
title: "Evaluation gating: versioned golden dataset and thresholds block prompt or model changes"
owner_role: ai-ml
date: 2026-10-24
status: ACCEPTED
decision_type: RECOMMEND
impact: high
reversibility: high
type1: true
confidence: 85
affects:
  - REQ-012
supersedes: []
superseded_by: null
evidence: []
category: ai
revisit_trigger: Pilot dismiss rate diverges from offline eval results
---
# ADR-008 — Evaluation gating: versioned golden dataset and thresholds block prompt or model changes

- **Owner role:** ai-ml
- **Decision type:** RECOMMEND · **Impact:** high · **Reversibility:** high · **Confidence:** 85/100

## Context
AI quality is the product (REQ-012). Prompt and model changes can silently regress quality.

## Options considered
| Option | Notes |
|---|---|
| A. Versioned golden dataset (start: 150 labelled transcript segments across objection types, competitor mentions, coaching moments, plus negatives), metrics per category, thresholds enforced in CI on a sample and on the full set before release | **Chosen** |
| B. Manual spot checks | not repeatable |
| C. Production feedback only | too late; customers find the regressions |

## Decision
Option A. Launch thresholds (proposed; founder confirms): objection precision ≥ 0.85, recall ≥ 0.80; competitor mention precision ≥ 0.95; evidence quote validity 100%; hallucinated-insight rate ≤ 2%. Every eval run is recorded as evidence.

## Rationale
Turns AI quality into an evidence-gated, regression-tested property, like any other test (Constitution 15).

## Supporting evidence
Engineering practice (ai.md). Dataset built from synthetic and consented design-partner calls only.

## Rejected alternatives
B, C (not repeatable or too late).

## Consequences
- N006 can start in parallel with identity work (it only depends on N001).
- G-AI-EVALS is a launch blocker.
- The dataset contains personal data from consented calls: same retention and access rules as production data.

## Revisit trigger
Pilot dismiss rate diverges from offline eval results.

## Affected requirements / features
REQ-012 · F004
