# Walkthrough: calculator app + website

Input:

```text
/raftly
I want to build a calculator mobile app and website.
```

The complete result is in [examples/calculator](../examples/calculator) (`.raftly/` plus the rendered `artifacts/`).

## 1. Orient and classify
`raftly context` finds an empty repo, so the mode is GREENFIELD. The **[Head of Product Strategy]** classifies a simple consumer
utility on web, iOS and Android, with no backend, accounts, personal data, payments or AI, and a public website. `raftly init`
records that profile, and the profile alone makes 29 of 45 production checks NOT_APPLICABLE.

## 2. Research (only what matters)
Two material questions: can one codebase serve all three surfaces, and is there a credible decimal library? Both were checked
against primary sources (Expo web docs; decimal.js repo, MIT, no dependencies). Unverifiable items (store-review risk,
user complaints) are labelled **Not verified** in RESEARCH.md and kept as assumptions.

## 3. Product
Requirements REQ-001…011: precedence, exact decimals, predictable edge cases, offline, accessibility, then history,
copy/paste, keyboard, haptics and theme. REQ-011 records explicit exclusions (scientific, conversion, accounts, sync, ads, analytics).
EXP-001 sets kill criteria for the beta.

## 4. Design: three real directions
**[Design Director]** A Native minimal, B Modern utility (live expression line + history drawer), C Workspace/history-first.
They differ in interaction model, not colour. B is recommended (ADR-005) because it makes the product's promise visible.

## 5. Architecture: refuse to overbuild
**[Principal Software Architect]** ADR-001 client-only (no backend, auth, DB, queues or Kubernetes); ADR-002 a pure engine separate
from the UI; ADR-003 decimal.js; ADR-004 Expo + React Native Web (Type-1, revisit trigger tied to assumption A-002);
ADR-006 calculator semantics (precedence, repeated equals, percent, divide by zero, decimal input, display-only rounding);
ADR-007 build the keypad internally (no component library); ADR-008 no analytics.

## 6. Plan
Seven nodes in four dependency phases, a feature spec per significant feature, and a self-contained prompt per node.
The test strategy is weighted toward table-driven and property-based engine tests.

## 7. Blueprint complete
`raftly validate --blueprint-gate` passes, so the stage moves to BLUEPRINT_COMPLETE. The deliverables, `raftly blueprint` and `raftly deck`
follow. Readiness is INSUFFICIENT_EVIDENCE because nothing is built yet, and that is the honest answer.

## 8. Learning
"Rounding must happen only at display time" is recorded as L-001 **PROJECT_ONLY**. It's tied to this engine's display contract.

## Next
`/raftly build next` starts N001 with prompt 001 and records real test evidence before anything is marked VERIFIED.
