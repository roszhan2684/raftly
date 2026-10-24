---
marp: true
theme: default
paginate: true
header: "Tally"
style: |
  section { font-family: system-ui, sans-serif; }
  h1 { color: #2851D8; }
---

# Tally

Tally is a calculator for iOS, Android and the web that shows exactly what it will compute and gets decimals right, with no backend and no data collection.

<!--
Speaker notes: One-sentence vision. Who it is for and why now.
-->

---

# Problem

People use calculators dozens of times a week for prices, tips, splits and quick sums. Built-in calculators hide the expression (users lose track mid-calculation), disagree on precedence and percent, and on the web often show floating-point artefacts such as `0.30000000000000004`.

<!--
Speaker notes: The pain in the user's words; evidence from RESEARCH.md.
-->

---

# Who it's for

Anyone doing quick everyday arithmetic on a phone or laptop: shoppers, students, freelancers splitting invoices, people at a restaurant. The primary early adopters are detail-minded users annoyed by calculators that hide the expression.

<!--
Speaker notes: Primary user / ICP and the job they hire the product for.
-->

---

# Today's workflow and its pain

**Today:** open the built-in calculator → type → lose track → clear → retype; copy the result by memory. **With Tally:** type with a live expression line and preview → `=` → reuse from history or copy in one tap.

<!--
Speaker notes: What users do today and where it breaks.
-->

---

# Proposed solution

Arithmetic with precedence and parentheses, exact decimals, predictable edge cases, history (100, local), copy/paste, web keyboard input, haptics, light/dark, fully offline, on iOS, Android and the web.

<!--
Speaker notes: Scope of V1 and what is explicitly excluded.
-->

---

# Core experience

- **See before you commit**: the expression and a live preview are always visible.
- **Familiar first**: standard keypad layout; nothing to learn.
- **One-handed and glanceable** on phones; **typeable** on desktops.
- **Quiet**: no ads, prompts or upsells; motion only for feedback.

<!--
Speaker notes: The main flow end to end.
-->

---

# Design direction

**Option B: Modern utility** (ADR-005, RECOMMEND, confidence 75). It makes the product's promise visible without sacrificing familiarity. Validate in EXP-001 interviews.

<!--
Speaker notes: Options considered and why this direction won.
-->

---

# Architecture

A client-only application (ADR-001). One Expo/React Native codebase renders on iOS, Android and the web via react-native-web (ADR-004). All arithmetic happens in a pure TypeScript engine (ADR-002) using decimal.js (ADR-003). History is stored on the device.

<!--
Speaker notes: Simplest architecture that satisfies the requirements; Type-1 decisions.
-->

---

# Build plan

- **Phase 0:** Calculation engine, App shell and design tokens
- **Phase 1:** Keypad and display
- **Phase 2:** History, Web keyboard and clipboard, Offline, PWA and store builds
- **Phase 3:** Launch readiness

<!--
Speaker notes: Dependency-ordered build graph: 7 capabilities, 6 feature specs. No calendar promises.
-->

---

# Security, privacy & compliance

Tally is a client-only app with no backend, no accounts and no data collection (ADR-001, ADR-008). Its attack surface is limited to the input parser, the web delivery chain and dependencies. Server-side controls are not applicable. This document describes readiness, not a certification.

<!--
Speaker notes: Readiness, not certification. Items needing professional review are flagged.
-->

---

# Business & go-to-market

For everyday calculator users who want to trust the answer, Tally is a calculator for mobile and the web that shows exactly what it will compute and gets decimals right. Unlike built-in calculators, it keeps the whole expression visible and never shows floating-point noise.

<!--
Speaker notes: Positioning, channels, pricing inputs.
-->

---

# Launch plan & risks

- **HIGH** Precision or rounding bugs produce wrong results → Decimal arithmetic (ADR-003), display-only rounding, property-based and table-driven engine tests
- **HIGH** Crowded category: hard to stand out against free built-in calculators → Differentiate on correctness, live expression line and history; kill criteria in EXP-001
- **HIGH** App store review may reject a calculator as low-value or duplicative in a saturated category → Ship clear differentiators (live expression, history, accessibility); re-verify current App Store and Google Play guidelines before submission
- **MEDIUM** React Native Web bundle size or input latency degrades the web experience → Performance budget (initial JS ≤ 250 KB gzip target, INP < 200 ms), measure in N003

**Untested assumptions (labelled, not facts):**
- A-001 (confidence 55): Users value exact decimal results and predictable semantics enough to choose Tally over the built-in calculator
- A-002 (confidence 65): One Expo + React Native Web codebase delivers native-feeling UI on iOS/Android and acceptable web performance
- A-003 (confidence 60): A local history of 100 entries covers typical reuse

<!--
Speaker notes: Top risks with mitigations; what would make us stop (kill criteria).
-->
