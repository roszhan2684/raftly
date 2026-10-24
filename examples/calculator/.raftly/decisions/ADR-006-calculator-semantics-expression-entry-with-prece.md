---
id: ADR-006
title: "Calculator semantics: expression entry with precedence, repeated equals, percent rules"
owner_role: product-director
date: 2026-10-24
status: ACCEPTED
decision_type: RECOMMEND
impact: medium
reversibility: medium
type1: false
confidence: 80
affects:
  - REQ-001
  - REQ-003
supersedes: []
superseded_by: null
evidence: []
category: product
revisit_trigger: Consistent beta confusion about percent or repeated equals
---
# ADR-006 — Calculator semantics: expression entry with precedence, repeated equals, percent rules

- **Owner role:** product-director
- **Decision type:** RECOMMEND · **Impact:** medium · **Reversibility:** medium · **Confidence:** 80/100

## Context
Calculators disagree on semantics (immediate execution vs precedence, percent, repeated equals). Users hit
these differences as "wrong answers". REQ-001 and REQ-003 require predictable, documented behaviour.

## Options considered
| Topic | Option chosen | Alternative | Why |
|---|---|---|---|
| Entry model | **Expression entry with standard precedence** (`2 + 3 × 4 = 14`) | immediate execution (`= 20`) | matches maths and phone calculators in expression mode; the live expression line makes it visible |
| Repeated equals | **Repeats the last operator and operand** (`5 + 3 = = → 11`) | no-op | common convention, useful for repeated addition |
| Percent | **`a + b%` → `a + a×b/100`; `a − b%` likewise; `a × b%` → `a×b/100`; lone `b%` → `b/100`** | always `b/100` | matches the expectations behind "add 15% tip" |
| Divide by zero | **Shows "Can't divide by zero"**; the result is not stored in history; the next key starts fresh | Infinity / NaN | clear and recoverable |
| Decimal input | leading `.` → `0.`; a second `.` in a number is ignored; trailing `.` is allowed while typing and dropped on evaluate | errors | forgiving input |
| Precision | exact decimal internally (ADR-003); display ≤ 16 significant digits, round-half-even **at display time only**; scientific notation beyond 1e16 or below 1e-7 | rounding intermediates | prevents drift on repeated operations (L-001) |
| Operator replacement | pressing an operator after an operator replaces it | stacking | prevents typos |
| Negative numbers | `±` toggles the sign of the current number; unary minus after an operator | — | — |

## Decision
Adopt the rules above as the engine specification. F001 encodes each one as table-driven tests.

## Rationale
Predictability and visibility over cleverness. Each rule is shown by the live expression line (ADR-005).

## Supporting evidence
Convention survey summarised in RESEARCH.md (not verified against every platform calculator; the live
expression line mitigates divergence).

## Rejected alternatives
See the table.

## Consequences
The engine needs a small state machine for repeated equals and a parser for precedence and parentheses.

## Revisit trigger
Consistent beta confusion about percent or repeated equals.

## Affected requirements / features
REQ-001, REQ-003 · F001, F002
