---
id: L-001
title: Rounding must happen only at display time
outcome: PROJECT_ONLY
kind: implementation_finding
evidence_quality: reproduced
source_authority: official_docs
repeat_count: 0
cross_project: false
objective: true
contradicted: false
contains_private: false
related:
  - REQ-002
  - F001
candidate: null
created_at: 2026-10-24
---
# L-001 — Rounding must happen only at display time

- **Firewall outcome:** PROJECT_ONLY (credibility 64/100)
- **Kind:** implementation_finding

## Observation
While specifying the engine, rounding intermediate results to the 16 displayed digits made repeated operations
drift (for example `1 ÷ 3 × 3` and repeated `=`). Keeping exact decimal values internally and rounding only in
`format()` removes the drift.

## Evidence
Reproduced in a research spike against decimal.js behaviour (RESEARCH.md #2–#3). It becomes test evidence
when F001's precision-drift test runs.

## Firewall reasoning
- not cross-project as stated: the rule is tied to this engine's display contract (16 significant digits, round-half-even)
- the general principle (avoid binary floats for decimal maths) is already part of Raftly's references, so no proposal is needed

## How this project applies it
ADR-006 precision rule; F001 API (`lastResult` stores the exact value); prompt 001 constraint "Rounding happens only in `format()`".
