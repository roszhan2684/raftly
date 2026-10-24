# Decision Book — Tally

Major product, design and architecture decisions. Each row links to its ADR, which holds the context, options,
evidence, consequences and revisit trigger. Regenerate the table with `raftly decisions book`.

## Decisions
<!-- generated:decisions:start -->
| ID | Decision | Why (short) | Owner | Type | Confidence | Reversibility | Status |
|---|---|---|---|---|---|---|---|
| [ADR-001](decisions/ADR-001-client-only-architecture-no-backend-accounts-or.md) | Client-only architecture: no backend, accounts or database | Constitution 4–5: the simplest architecture that satisfies actual requirements. A backend would add accounts, personal… | architect | RECOMMEND · Type-1 | 92 | medium | ACCEPTED |
| [ADR-002](decisions/ADR-002-one-pure-typescript-calculation-engine-shared-by.md) | One pure TypeScript calculation engine shared by all surfaces | Separating the calculation engine from the UI (spec §55) makes the hardest part exhaustively testable and portable. | architect | AUTO | 95 | high | ACCEPTED |
| [ADR-003](decisions/ADR-003-decimal-arithmetic-with-decimal-js-instead-of-bi.md) | Decimal arithmetic with decimal.js instead of binary floating point | Correctness is the differentiator. A mature, dependency-free MIT library beats owning arbitrary-precision code. | frontend | RECOMMEND | 90 | high | ACCEPTED |
| [ADR-004](decisions/ADR-004-expo-react-native-web-as-the-single-cross-platfo.md) | Expo + React Native Web as the single cross-platform codebase | Expo documents first-class web support from the same codebase via react-native-web, with static rendering and `npx expo… | mobile | RECOMMEND · Type-1 | 72 | low | ACCEPTED |
| [ADR-005](decisions/ADR-005-design-direction-b-modern-utility-live-expressio.md) | Design direction B: Modern utility (live expression line + history drawer) | B directly expresses the differentiators: you see exactly what will be computed (precedence, percent) and can reuse res… | design-director | RECOMMEND | 75 | high | ACCEPTED |
| [ADR-006](decisions/ADR-006-calculator-semantics-expression-entry-with-prece.md) | Calculator semantics: expression entry with precedence, repeated equals, percent rules | Predictability and visibility over cleverness. Each rule is shown by the live expression line (ADR-005). | product-director | RECOMMEND | 80 | medium | ACCEPTED |
| [ADR-007](decisions/ADR-007-build-the-keypad-and-display-internally-no-ui-co.md) | Build the keypad and display internally; no UI component library | Spec §9: "For a trivial component, building internally can be the senior decision." A keypad is a grid of buttons. | design-systems | AUTO | 90 | high | ACCEPTED |
| [ADR-008](decisions/ADR-008-no-analytics-or-telemetry-in-v1.md) | No analytics or telemetry in V1 | Minimisation (privacy-compliance.md). "Collects no data" is a genuine feature for a utility. | privacy | RECOMMEND | 85 | high | ACCEPTED |

Generated from `decisions/` by `decisions.py book`. Edit the ADRs, not this table.
<!-- generated:decisions:end -->

## Open founder decisions
None. Every V1 decision could be resolved by research or engineering judgment. Brand/name ("Tally") is a working name the founder can change without technical impact.
