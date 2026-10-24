# Product Build Document — Tally

## How to build
Run `/raftly build next`, or open the prompt in `.raftly/prompts/` for the next unblocked node. Each prompt is
self-contained and ends with the evidence and status updates Raftly expects.

## Build graph
<!-- generated:graph:start -->
```text
Phase 0
  [ ] N001 Calculation engine
  [ ] N002 App shell and design tokens
Phase 1
  [ ] N003 Keypad and display  <- N001, N002
Phase 2
  [ ] N004 History  <- N003
  [ ] N005 Web keyboard and clipboard  <- N003
  [ ] N006 Offline, PWA and store builds  <- N003
Phase 3
  [ ] N007 Launch readiness  <- N004, N005, N006
```

Legend: `[x]` complete · `[v]` verified · `[?]` implemented, unverified · `[>]` in progress · `[~]` partial · `[!]` blocked · `[-]` dropped

| Phase | Node | Name | Type | Depends on | Status | Prompts |
|---|---|---|---|---|---|---|
| 0 | N001 | Calculation engine | foundation | — | PLANNED | 001-calculation-engine.md |
| 0 | N002 | App shell and design tokens | foundation | — | PLANNED | 002-app-shell-and-design-tokens.md |
| 1 | N003 | Keypad and display | feature | N001, N002 | PLANNED | 003-keypad-and-display.md |
| 2 | N004 | History | feature | N003 | PLANNED | 004-history.md |
| 2 | N005 | Web keyboard and clipboard | feature | N003 | PLANNED | 005-web-keyboard-and-clipboard.md |
| 2 | N006 | Offline, PWA and store builds | ops | N003 | PLANNED | 006-offline-pwa-and-store-builds.md |
| 3 | N007 | Launch readiness | launch | N004, N005, N006 | PLANNED | 007-launch-readiness.md |

**Progress:** 0.0% complete, 0.0% verified (7 active nodes). Derived from `build-graph.yaml`; do not edit this block by hand.
<!-- generated:graph:end -->

## Phases
- **Phase 0, foundations:** N001 Calculation engine (correctness is the product; testable without UI) and N002 App shell + tokens. Independent, so they can be done in either order.
- **Phase 1, core experience:** N003 Keypad and display. Validates A-002 (one codebase, native feel, web performance) before more UI is built on it.
- **Phase 2, completion:** N004 History, N005 Web keyboard/clipboard, N006 Offline + store builds. Independent of each other.
- **Phase 3, launch:** N007 Launch readiness. Evidence for every applicable gate check, then the beta (EXP-001).

## Feature ordering
F001 → F005 → F002 → (F003, F004, F006). MUST features first. SHOULD features follow the core flow they extend.

## Acceptance gates
- A dependant node starts only when its dependencies are VERIFIED or COMPLETE (enforced by `raftly graph next`).
- N003 must record the A-002 validation result. If A-002 is invalidated, stop and revisit ADR-004 before N004–N006.
- DoD per feature spec. Server-side items are N/A with ADR-001 cited.

## Test strategy
| Layer | Scope | Tooling (choose at N001/N002; record in dependencies.yaml) |
|---|---|---|
| Unit (heavy) | engine semantics (table-driven, one row per ADR-006 rule), precision drift, formatter, history store | Jest or Vitest |
| Property-based | random token sequences never throw; arithmetic identities; format round-trip | fast-check (if adopted) |
| Component | keypad/display states, history interactions, accessibility labels | React Native Testing Library |
| E2E (web) | type → evaluate → copy → paste → history | Playwright (Chromium, WebKit, Firefox) |
| Accessibility | axe on web; manual VoiceOver, TalkBack, keyboard passes | axe + manual |
| Performance | web Lighthouse; initial JS vs budget; cold start on devices | Lighthouse |
| Platform matrix | oldest supported + current iOS/Android, small/large screens, three browsers | manual + E2E |

Evidence is recorded with `raftly evidence record`. Build/lint results are supporting evidence, not verification.

## Release requirements
Applicable production-gate blockers: G-PRODUCT-SCOPE, G-PRODUCT-FLOWS, G-SEC-SECRETS, G-TEST-AUTOMATED, G-ROLLBACK.
Plus major/minor checks: G-SEC-DEPS, G-SEC-HEADERS, G-TEST-REGRESSION, G-TEST-PLATFORMS, G-A11Y, G-PERF,
G-CLIENT-ERRORS, G-SUPPORT, G-LEGAL-DOCS, G-SEO, G-STORE. All others are NOT_APPLICABLE by profile (see LAUNCH.md).
