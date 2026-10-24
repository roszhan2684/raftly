# Architecture Document — Tally

## Context
Actors: the end user on iOS, Android or a web browser. External systems: the app stores (distribution),
a static web host (distribution). **No runtime services.**

## System overview
A client-only application (ADR-001). One Expo/React Native codebase renders on iOS, Android and the web
via react-native-web (ADR-004). All arithmetic happens in a pure TypeScript engine (ADR-002) using decimal.js
(ADR-003). History is stored on the device.

```text
            ┌──────────────────────── Tally app (one codebase) ─────────────────────────┐
 user ──►   │  UI layer (React Native components, tokens, a11y, haptics)                 │
            │      │ tokens / events                     ▲ EvalResult                      │
            │      ▼                                     │                                 │
            │  Engine (pure TS): tokenizer → parser → evaluator(decimal.js) → formatter   │
            │      │ onEvaluated                                                          │
            │      ▼                                                                      │
            │  History store ──► storage adapter ──► AsyncStorage (native) / localStorage │
            └─────────────────────────────────────────────────────────────────────────────┘
 distribution:  iOS/Android signed builds → stores      web static export → static host (+ service worker)
```

## Boundaries
- `engine/` depends on nothing but decimal.js. UI → engine is the only direction (lint-enforced).
- `history/` depends on the storage adapter interface only.
- `ui/` depends on engine, history and tokens. No business logic in components.

## Stack
| Concern | Choice | ADR | Notes |
|---|---|---|---|
| App runtime (iOS/Android/web) | Expo + React Native + React Native Web | ADR-004 | Type-1; revisit if A-002 is invalidated |
| Calculation | Pure TypeScript engine | ADR-002 | no UI imports |
| Decimal maths | decimal.js | ADR-003 | MIT, no dependencies |
| UI components | Internal | ADR-007 | no component library |
| Persistence | On-device key-value storage | ADR-001 | history only |
| Analytics / telemetry | None | ADR-008 | privacy by design |
| Web hosting | Static host with custom headers | to be decided in N006 (RECOMMEND) | any host that supports CSP headers |

## Data
Not applicable beyond on-device history (no server, no personal data). `HistoryEntry { id, expression,
resultExact, createdAt }`. Blueprint data section: NOT_APPLICABLE.

## Security
No server attack surface. Relevant controls: no dynamic code evaluation in the parser, no secrets in the bundle,
CSP and security headers on the web host, dependency hygiene, accurate store privacy labels. See SECURITY.md.

## Integrations
None at runtime. Build-time: Expo build tooling, app store submission.

## Reliability
No SLOs (no service). Reliability = correctness (engine tests) + crash-free operation (store vitals, beta reports).

## Environments
Local development (Expo dev server, simulators) · CI (lint, type-check, tests, web export) · production (store
releases; static web deploy). A preview web deploy per PR is optional.

## Failure behavior
| Critical path | Failure | User sees | System does | Detected by |
|---|---|---|---|---|
| Evaluate | divide by zero / overflow | inline message | returns an error value; next key starts fresh | engine tests |
| Evaluate | parser bug | wrong or blocked result | n/a | table + property tests; beta reports |
| History | storage unavailable/corrupt | "History won't be saved" note | session-only history | unit tests |
| Web load | offline first visit | browser offline page | service worker serves later visits | manual test |
| Release | bad build shipped | defect | web: redeploy the previous build; stores: halt the phased release, ship a fix | rollback rehearsal (G-ROLLBACK) |

## Scaling assumptions
Scale is irrelevant to runtime cost (no servers). Static hosting cost grows only with bandwidth. The bundle is cached.

## Not applicable
Backend, database, authentication, authorisation, queues, caches, search, email, billing, observability
backend, Kubernetes, microservices: none of the V1 requirements need them (ADR-001).
