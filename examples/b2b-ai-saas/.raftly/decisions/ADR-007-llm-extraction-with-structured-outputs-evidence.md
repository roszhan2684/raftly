---
id: ADR-007
title: LLM extraction with structured outputs, evidence quotes and versioned prompts behind a provider abstraction
owner_role: ai-ml
date: 2026-10-24
status: ACCEPTED
decision_type: RECOMMEND
impact: high
reversibility: medium
type1: true
confidence: 75
affects:
  - REQ-005
  - REQ-012
supersedes: []
superseded_by: null
evidence:
  - research/ai-providers.md
category: ai
revisit_trigger: Eval thresholds missed, provider terms change, or cost per audio hour exceeds budget
---
# ADR-007 — LLM extraction with structured outputs, evidence quotes and versioned prompts behind a provider abstraction

- **Owner role:** ai-ml
- **Decision type:** RECOMMEND · **Impact:** high · **Reversibility:** medium · **Confidence:** 75/100

## Context
Detect objections, competitor mentions and coaching opportunities in long transcripts with trustworthy evidence (REQ-005), meeting quality thresholds (REQ-012) at an acceptable cost (A-005).

## Options considered
| Option | Pros | Cons |
|---|---|---|
| A. General LLM with JSON-schema outputs, evidence quotes + timestamps, chunked over transcript windows, versioned prompts | fast to iterate; strong language understanding | cost per call; provider dependency |
| B. Fine-tuned smaller classifier | cheap at scale | needs labelled data we don't have; training on customer data is excluded (REQ-016) |
| C. Keyword/rule-based detection | cheap, transparent | misses paraphrased objections; brittle |

## Decision
Option A, using Anthropic's API as the initial provider behind an `ExtractionProvider` interface. The model is chosen by the N006 eval harness on quality and cost. Outputs are validated against a schema; every insight must cite a quote that exists verbatim in the transcript (rejected otherwise); prompts are versioned in code; competitor names are matched against an org-configurable competitor list to reduce false positives.

## Rationale
Best quality-to-effort for V1. Evidence quotes make insights verifiable (R-003). Abstraction plus eval gating (ADR-008) make the provider replaceable.

## Supporting evidence
Provider capabilities, context limits, pricing and data-use terms must be confirmed from current documentation at N007 (**not verified** here). See research/ai-providers.md.

## Rejected alternatives
B (no training data; REQ-016), C (quality).

## Consequences
- Per-call cost is metered and budgeted (F008, G-AI-COST).
- Transcript text is untrusted input (prompt-injection risk R-006): no tools, schema-only outputs.
- Data-use terms must exclude training on customer data; confirm zero-retention options if required by customers.

## Revisit trigger
Eval thresholds missed, provider terms change, or cost per audio hour exceeds budget.

## Affected requirements / features
REQ-005, REQ-012 · F004
