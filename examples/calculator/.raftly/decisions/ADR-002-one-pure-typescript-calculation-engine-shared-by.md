---
id: ADR-002
title: One pure TypeScript calculation engine shared by all surfaces
owner_role: architect
date: 2026-10-24
status: ACCEPTED
decision_type: AUTO
impact: medium
reversibility: high
type1: false
confidence: 95
affects:
  - REQ-001
  - REQ-002
  - REQ-003
supersedes: []
superseded_by: null
evidence: []
category: architecture
---
# ADR-002 — One pure TypeScript calculation engine shared by all surfaces

- **Owner role:** architect
- **Decision type:** AUTO · **Impact:** medium · **Reversibility:** high · **Confidence:** 95/100

## Context
Calculator correctness (REQ-001–003) is the product. The same semantics must hold on iOS, Android and web.

## Options considered
| Option | Pros | Cons |
|---|---|---|
| Engine module with no UI imports (tokenizer → parser → evaluator → formatter) | testable in isolation, one source of truth | needs a clear API |
| Logic inside keypad components | quick to start | untestable, diverges per surface |

## Decision
`packages/engine` (or `src/engine`): pure TypeScript, no React/React Native imports, deterministic.
API: `evaluate(expression: string, state?: EngineState) → Result` and `format(value, locale) → string`.

## Rationale
Separating the calculation engine from the UI (spec §55) makes the hardest part exhaustively testable and portable.

## Supporting evidence
Standard practice; no research needed (AUTO).

## Rejected alternatives
Logic in components (untestable, duplicated).

## Consequences
The UI is a thin client of the engine. Engine tests are the main correctness evidence for F001.

## Revisit trigger
Not applicable (AUTO, highly reversible).

## Affected requirements / features
REQ-001, REQ-002, REQ-003 · F001, F002
