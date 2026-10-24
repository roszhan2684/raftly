# Research — Tally

| # | Question | Finding | Source(s) | Checked | Confidence | Informs |
|---|---|---|---|---|---|---|
| 1 | Can one codebase target iOS, Android and the web? | Expo documents first-class web support from the same codebase via react-native-web, static rendering, and production web export with `npx expo export --platform web`. | https://docs.expo.dev/workflow/web/ | 2026-10-24 | High | ADR-004 |
| 2 | Is there a credible decimal library? | decimal.js: "An arbitrary-precision Decimal type for JavaScript", MIT licence, no dependencies. Pin the latest stable version at implementation. | https://github.com/MikeMcl/decimal.js | 2026-10-24 | High | ADR-003 |
| 3 | Do binary floats break decimal arithmetic in JS? | Yes. Numbers are IEEE-754 doubles (`0.1 + 0.2 !== 0.3`). Well-established language behaviour. | ECMAScript Number semantics (prior knowledge; not re-fetched) | 2026-10-24 | High | REQ-002, ADR-003 |
| 4 | What do users complain about in calculators? | Hidden expressions, unclear percent behaviour, precedence differences between apps. | **Not verified**: from prior knowledge of app-store review themes; validate in EXP-001 interviews | — | Medium-low | ADR-005, ADR-006, A-001 |
| 5 | Will stores accept another calculator? | Both stores have quality/duplication guidelines for saturated categories; a differentiated, high-quality app is the mitigation. | **Not verified**: re-read current App Store Review Guidelines and Google Play policy before submission | — | Medium | R-004 |
| 6 | Must an app with no data collection still have a privacy policy? | Generally yes for store listings. Confirm current store requirements at submission. | **Not verified** | — | Medium | G-LEGAL-DOCS |

## Notes
Longer notes: `research/platform-and-precision.md`. Items marked **Not verified** are assumptions until
re-checked. They don't support PASS statuses.
