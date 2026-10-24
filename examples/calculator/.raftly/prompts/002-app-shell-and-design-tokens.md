# Prompt 002 — App shell and design tokens

> Build-graph node: **N002** · Features: F005
> Self-contained implementation prompt.

## Role to activate
Staff Mobile Engineer + Staff Design Systems Engineer.

## Files to read first
- `.raftly/state.yaml`
- `.raftly/decisions/ADR-004-*.md` (Expo + React Native Web), `ADR-007-*.md` (internal components)
- `.raftly/DESIGN_SYSTEM.md` (tokens), `.raftly/DESIGN.md` (layout, responsive rules)
- `.raftly/features/F005-theming-and-design-tokens.md`

## Objective
Create the Expo app that runs on iOS, Android and web, with the semantic token system and system-driven light/dark theming.

## Scope
Project scaffold, TypeScript strict mode, lint/format, the tokens module, the theme provider, the base responsive layout container, CI running lint + tests.

## Dependencies
None (foundation).

## Architecture / design constraints
- Use the current stable Expo SDK. Verify the version and web setup in the Expo docs at implementation time (`npx expo install react-dom react-native-web @expo/metro-runtime` per the docs).
- Components use semantic tokens only; add a lint rule against raw hex values outside `tokens.ts`.
- No UI component library (ADR-007).

## Implementation tasks
1. Scaffold the Expo app (TypeScript), enabling web; confirm `npx expo export --platform web` produces a static build.
2. Implement `tokens.ts` from DESIGN_SYSTEM.md (light + dark), plus a contrast-check unit test over all text/background pairs.
3. Theme provider reading the system colour scheme with live updates.
4. Responsive container: phone, tablet and wide-web breakpoints per DESIGN.md.
5. CI workflow: install, lint, type-check, test, web export.

## Explicitly out of scope
Keypad, display, history (later nodes).

## Edge cases
System theme change while the app is open; increased-contrast settings where exposed.

## Security / accessibility requirements
Contrast AA for all token pairs (automated test). No third-party scripts on web.

## Tests required
Token contrast test; theme switching test; a CI run green.

## Verification steps
1. Run on an iOS simulator/device, an Android emulator/device and the web; record what was checked.
2. CI green; record the run.

## After implementation (state and evidence updates)
1. Run the relevant tests/checks and keep the exact commands and outputs.
2. Compare the implementation with every acceptance criterion in the feature spec(s).
3. Record evidence: `raftly evidence record --subject F005 --kind test --result PASS|FAIL --summary "..." --command "..."` (and `--kind manual` for device checks, saying what was checked on which device).
4. Update status: `raftly graph set-status N002 IMPLEMENTED_UNVERIFIED`, then `VERIFIED` only with passing verification evidence; `raftly records feature-status F005 ...` likewise.
5. Record any deviation as an ADR, debt item or risk.
6. Do not mark COMPLETE unless verification passed and the Definition of Done is checked.

## Escalate instead of changing autonomously
- Any change to ADR-001 (client-only) or ADR-004 (Expo + React Native Web): both are Type-1.
- Any new dependency not in `dependencies.yaml`.
- Any change to calculator semantics in ADR-006 (product decision).
- Anything that weakens accessibility (REQ-005).
