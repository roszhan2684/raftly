---
id: ADR-003
title: Decimal arithmetic with decimal.js instead of binary floating point
owner_role: frontend
date: 2026-10-24
status: ACCEPTED
decision_type: RECOMMEND
impact: medium
reversibility: high
type1: false
confidence: 90
affects:
  - REQ-002
supersedes: []
superseded_by: null
evidence:
  - "https://github.com/MikeMcl/decimal.js"
  - RESEARCH.md
category: engineering
revisit_trigger: Bundle-size budget exceeded or a lighter audited decimal library appears
---
# ADR-003 — Decimal arithmetic with decimal.js instead of binary floating point

- **Owner role:** frontend
- **Decision type:** RECOMMEND · **Impact:** medium · **Reversibility:** high · **Confidence:** 90/100

## Context
JavaScript numbers are IEEE-754 binary doubles: `0.1 + 0.2` yields `0.30000000000000004`. REQ-002 requires
exact results for decimal input.

## Options considered
| Option | Effort | Correctness | Weight | Licence | Fit |
|---|---|---|---|---|---|
| Build an internal decimal type | high | risky (security-critical-like correctness code we would own) | small | — | Poor |
| decimal.js | low | arbitrary-precision decimal | moderate, no dependencies | MIT | **Good** |
| Integer scaling (fixed decimals) | medium | breaks on division and large ranges | tiny | — | Poor |
| Native float + rounding tricks | low | still wrong in edge cases | none | — | Rejected |

## Decision
Use decimal.js inside the engine only (configured precision 34 significant digits internally; display at 16).

## Rationale
Correctness is the differentiator. A mature, dependency-free MIT library beats owning arbitrary-precision code.

## Supporting evidence
decimal.js repository: "An arbitrary-precision Decimal type for JavaScript", MIT licence, "No dependencies"
(checked 2026-10-24). Version to pin at implementation time (latest stable from npm).

## Rejected alternatives
Internal implementation (cost and risk), integer scaling (division), floats (wrong).

## Consequences
Adds a dependency to the engine bundle. Measured against the web performance budget in N003 (R-002).

## Revisit trigger
Bundle-size budget exceeded, or a lighter audited decimal library appears.

## Affected requirements / features
REQ-002 · F001
