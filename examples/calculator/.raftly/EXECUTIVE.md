# Executive Summary — Tally

## What
Tally is a calculator for iOS, Android and the web that shows exactly what it will compute and gets decimals right,
with no backend and no data collection.

## Who
Everyday calculator users who want to trust the answer: shoppers, students, freelancers, anyone splitting a bill.

## Why
Built-in calculators hide the expression, disagree on percent and precedence, and on the web often show
floating-point noise. Small, frequent friction erodes trust.

## V1
- Correct arithmetic with precedence, exact decimals, predictable edge cases (ADR-006)
- Live expression line + history (direction B, ADR-005)
- Copy/paste, web keyboard, haptics, light/dark
- Fully offline; accessible (WCAG 2.2 AA target)
- Excluded: scientific functions, conversion, accounts, sync, ads, analytics

## Architecture
Client-only (ADR-001). One Expo + React Native Web codebase (ADR-004, Type-1, confidence 72, revisit if web
performance or native feel disappoints). A pure TypeScript engine with decimal.js (ADR-002, ADR-003).

## Plan
Seven dependency-ordered nodes: Phase 0 engine + app shell → Phase 1 keypad/display (validates A-002) →
Phase 2 history, web keyboard, offline and store builds → Phase 3 launch readiness. No calendar commitments.

## Risks
1. Crowded category (R-003): differentiation must be obvious; kill criteria in EXP-001.
2. Store review in a saturated category (R-004): re-verify guidelines before submission.
3. Web performance with React Native Web (R-002): budget measured in N003.

## Launch
Production readiness: INSUFFICIENT_EVIDENCE (nothing is built yet). 16 production checks apply; 29 are not
applicable to a client-only app. The beta (EXP-001) gates the public launch.
