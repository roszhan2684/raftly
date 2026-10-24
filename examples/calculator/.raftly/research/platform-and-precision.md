# Research note — platform and precision

## Platform (checked 2026-10-24)
Expo's web guide states first-class support for websites built with React from the same codebase, using
react-native-web for cross-platform components, with static rendering available and production export via
`npx expo export --platform web`. The guide names EAS Hosting as one hosting option; any static host that
serves custom headers works for an exported static site (our requirement: CSP headers, G-SEC-HEADERS).

Open question for N003: web bundle size with react-native-web plus decimal.js against the budget (R-002, A-002).

## Precision (checked 2026-10-24)
decimal.js: arbitrary-precision decimal type, MIT, no dependencies. Plan: precision 34 significant digits
internally, round-half-even, rounding applied only when formatting for display (L-001).

Alternatives considered: an internal implementation (rejected, correctness risk), integer scaling (fails for
division), and floats with rounding tricks (still wrong in edge cases).
