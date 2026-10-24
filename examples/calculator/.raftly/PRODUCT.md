# Product Document — Tally

## Vision
Everyday maths you never have to double-check: a calculator that shows exactly what it will compute and is always right.

## Problem
People use calculators dozens of times a week for prices, tips, splits and quick sums. Built-in calculators
hide the expression (users lose track mid-calculation), disagree on precedence and percent, and on the web
often show floating-point artefacts such as `0.30000000000000004`. The cost is small but frequent: re-typing,
doubt, and occasional wrong answers. See RESEARCH.md #3–#4.

## ICP / users
Anyone doing quick everyday arithmetic on a phone or laptop: shoppers, students, freelancers splitting
invoices, people at a restaurant. The primary early adopters are detail-minded users annoyed by calculators
that hide the expression.

## Jobs
- When I'm adding up several numbers, I want to see the whole expression, so I can spot a typo before I trust the total.
- When I need a percentage (tip, discount, VAT), I want it to behave the way I expect, so I don't have to think about calculator conventions.
- When I'm doing related calculations, I want to reuse earlier results, so I don't re-type them.

## Workflows
**Today:** open the built-in calculator → type → lose track → clear → retype; copy the result by memory.
**With Tally:** type with a live expression line and preview → `=` → reuse from history or copy in one tap.

## Positioning
For everyday calculator users who want to trust the answer, Tally is a calculator for mobile and the web that
shows exactly what it will compute and gets decimals right. Unlike built-in calculators, it keeps the whole
expression visible and never shows floating-point noise.

## Differentiation
Correctness (exact decimals, documented semantics), visibility (live expression line), speed (offline,
instant), reuse (history), accessibility, and no data collection.

## V1 / MVP
Arithmetic with precedence and parentheses, exact decimals, predictable edge cases, history (100, local),
copy/paste, web keyboard input, haptics, light/dark, fully offline, on iOS, Android and the web.

## Exclusions
- Scientific functions, exponents, memory keys: defer until users ask (REQ-011)
- Unit/currency conversion: needs live rates and a server
- Accounts and sync: no V1 requirement (A-004); would add a backend (ADR-001)
- Ads and analytics: contradict the positioning (ADR-008)

## Requirements
| ID | Requirement | Priority | Rationale |
|---|---|---|---|
| REQ-001 | Evaluate + − × ÷ and parentheses with standard precedence | MUST | Core job |
| REQ-002 | Exact decimal results; ≤ 16 significant digits, round-half-even at display only | MUST | Main differentiator |
| REQ-003 | Predictable edge cases (÷0, repeated =, %, decimal point, large/small) | MUST | Trust |
| REQ-004 | Fully offline on web and mobile | MUST | No server; works anywhere |
| REQ-005 | WCAG 2.2 AA, screen readers, keyboard, target sizes | MUST | Constitution 28 |
| REQ-006 | Local history of 100 entries; reuse; clear | SHOULD | Differentiator |
| REQ-007 | One-action copy; paste on web | SHOULD | Results are used elsewhere |
| REQ-008 | Full keyboard input on web | SHOULD | Desktop speed |
| REQ-009 | Haptics on mobile respecting settings | SHOULD | Tactile confirmation |
| REQ-010 | Light/dark following the system | SHOULD | Comfort |
| REQ-011 | Excludes scientific, conversion, accounts, sync, ads, analytics | WONT | Focus |

## Feature map
| Feature | Requirements | Node |
|---|---|---|
| F001 Calculation engine | REQ-001, REQ-002, REQ-003 | N001 |
| F005 Theming and design tokens | REQ-010, REQ-005 | N002 |
| F002 Keypad and display | REQ-001, REQ-005, REQ-009 | N003 |
| F003 History | REQ-006, REQ-007 | N004 |
| F004 Web keyboard and clipboard | REQ-008, REQ-007 | N005 |
| F006 Offline and distribution | REQ-004 | N006 |

## Success metrics
There is no telemetry by decision (ADR-008), so V1 success is measured through the beta (EXP-001) and the stores:
- **North star:** beta users who switch from their built-in calculator (interview), target ≥ 50%.
- **Inputs:** zero reported wrong results; store rating ≥ 4.5 after 50 ratings.
- **Guardrail:** crash rate from store vitals below the platform's "bad behaviour" thresholds.

## Assumptions
| ID | Assumption | Confidence | Validation |
|---|---|---|---|
| A-001 | Users value exact results and visible expressions enough to switch | 55 | EXP-001 beta |
| A-002 | One Expo + RNW codebase feels native and performs on web | 65 | N003 device + Lighthouse check |
| A-003 | 100 history entries is enough | 60 | Beta feedback |
| A-004 | No sync needed in V1 | 70 | Feedback over 60 days |

## Risks
R-001 precision bugs (mitigated by ADR-003 + tests) · R-002 web performance · R-003 crowded category ·
R-004 store review for a saturated category · R-005 semantics confusion. See risks.yaml.

## Kill criteria
EXP-001: if fewer than 25% of 20 beta users would switch, stop investing beyond V1 and keep Tally as a free web tool.
