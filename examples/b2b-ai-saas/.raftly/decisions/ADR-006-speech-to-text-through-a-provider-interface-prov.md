---
id: ADR-006
title: "Speech-to-text through a provider interface; provider selected by a diarization and WER spike"
owner_role: ai-ml
date: 2026-10-24
status: ACCEPTED
decision_type: RECOMMEND
impact: high
reversibility: medium
type1: true
confidence: 65
affects:
  - REQ-004
supersedes: []
superseded_by: null
evidence:
  - research/ai-providers.md
category: ai
revisit_trigger: Provider fails eval thresholds, terms change, or cost exceeds COST.md budget
---
# ADR-006 — Speech-to-text through a provider interface; provider selected by a diarization and WER spike

- **Owner role:** ai-ml
- **Decision type:** RECOMMEND · **Impact:** high · **Reversibility:** medium · **Confidence:** 65/100

## Context
Insights depend on accurate transcripts with speaker separation (REQ-004, A-002). Provider quality, diarization, language support, data-use terms and pricing change often and **were not verified for this blueprint**.

## Options considered
| Option | Notes |
|---|---|
| A. Managed STT API behind a `TranscriptionProvider` interface; select by spike | fastest to production; quality varies by provider |
| B. Self-hosted open-source speech model | data stays in our infrastructure; GPU ops and diarization work |
| C. Ask customers for channel-separated recordings only | perfect speaker split; adoption friction |

## Decision
Option A. N005 starts with a spike: 30 consented or synthetic labelled calls through two candidate providers, measuring word error rate, diarization error and cost per audio hour, and checking data retention and no-training terms. Choose the winner. Keep the interface so B remains possible.

## Rationale
Speed to a reliable pipeline matters more than owning a model in V1. The spike turns an unverified choice into evidence.

## Supporting evidence
**Not verified**: provider capabilities and prices must be researched at N005 (research/ai-providers.md lists the questions).

## Rejected alternatives
B deferred (ops cost; revisit if terms or cost fail), C rejected as a requirement (support it opportunistically when Zoom provides separate tracks).

## Consequences
- Dependency status stays PROPOSED until the spike picks a provider.
- Customer DPA and subprocessor list must name the chosen provider (R-008).

## Revisit trigger
Provider fails eval thresholds, terms change, or cost exceeds the COST.md budget.

## Affected requirements / features
REQ-004 · F003
