# Mobile engineering

Role: **Staff Mobile Engineer** (`mobile`).

## Platform strategy (usually Type-1)

| Option | Choose when | Watch out for |
|---|---|---|
| Native (Swift / Kotlin) | platform-specific UX, heavy device APIs, top performance | two codebases |
| Cross-platform (React Native/Expo, Flutter) | shared UI and logic across iOS/Android (and possibly web) | native module gaps, upgrade cadence |
| PWA / wrapped web | content- or form-centric, store presence optional | iOS PWA limitations, store review rules for thin wrappers |

Research current capabilities and store policies before deciding. Record an ADR with a revisit trigger
(e.g. "a required native capability is unsupported").

## Platform differences to design for

Navigation conventions (back gesture/button, tab bars), haptics APIs, keyboard behaviour, safe areas and
notches, dynamic type and font scaling, dark mode, permission prompts (ask in context, degrade gracefully
on denial), share sheets, and app lifecycle (background/foreground, state restoration).

## Offline and network

Decide explicitly: fully offline (a calculator), offline-first with sync (notes), or online-only with good
error states. Persist the minimum needed. Handle flaky networks with retries and an honest UI.

## Distribution

App store review guidelines, privacy nutrition labels / data safety forms (they must match actual
behaviour, including SDKs), a privacy policy URL (generally required even when no data is collected),
age rating, signing and certificates, build pipeline (e.g. EAS, Fastlane), staged rollout, and crash
reporting decided (or explicitly declined for privacy reasons). Over-the-air updates are limited by
store rules for native changes.

## Accessibility on mobile

VoiceOver/TalkBack labels and traits, focus order, minimum touch targets (~44 pt iOS / 48 dp Android),
support for larger text without truncation, reduced motion, and haptics never as the only feedback.

## Testing

Unit tests for logic, component tests, and device-matrix smoke tests (oldest supported OS, current OS,
small and large screens, both platforms). Record the matrix and its results as evidence (`G-TEST-PLATFORMS`).
