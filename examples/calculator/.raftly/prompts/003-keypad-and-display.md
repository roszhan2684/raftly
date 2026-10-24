# Prompt 003 — Keypad and display

> Build-graph node: **N003** · Features: F002
> Self-contained implementation prompt. **This node validates assumption A-002**: report the results.

## Role to activate
Staff Frontend Engineer + Design Director (interaction details), with the Staff Mobile Engineer for haptics.

## Files to read first
- `.raftly/features/F002-keypad-and-display.md`
- `.raftly/DESIGN.md` (SCR-main spec, direction B), `.raftly/DESIGN_SYSTEM.md`
- `.raftly/decisions/ADR-005-*.md`, `ADR-006-*.md`, `ADR-007-*.md`
- The engine API from N001 (`src/engine/`)

## Objective
Build SCR-main: a two-line display (expression + live result) and the keypad, wired to the engine, accessible on all three platforms.

## Scope
Keypad component, display component, reducer integrating engine state, haptics, screen-reader announcements, responsive layout.

## Dependencies
N001 (engine) and N002 (shell/tokens) must be VERIFIED or COMPLETE.

## Architecture / design constraints
- UI only calls the engine API; no arithmetic in components.
- Internal components on React Native primitives (ADR-007).
- Haptics via expo-haptics, light impact, gated on the system setting.

## Implementation tasks
1. Keypad grid per DESIGN.md with pressed states and accessible labels.
2. Display: the expression line (horizontal scroll pinned to the end) and the result line (auto-shrink to fit 16 digits).
3. Reducer: typing / evaluated / error states; `onEvaluated` event for history.
4. Announcements: debounced live region (web) and accessibility announcements (native).
5. Haptics respecting settings.
6. Measure: web Lighthouse (performance, accessibility) and cold start on two physical devices.

## Explicitly out of scope
History UI (N004), keyboard/paste (N005).

## Edge cases
Long expressions; rapid taps; rotation/resizing; 200% text size; error display then the next digit.

## Security / accessibility requirements
WCAG 2.2 AA: labels, roles, target sizes, contrast, announcements; haptics never the only feedback.

## Tests required
Component tests for state transitions; axe on the web build; manual VoiceOver and TalkBack passes.

## Verification steps
1. Component tests pass; axe shows no violations on SCR-main.
2. Manual screen-reader pass on iOS and Android (record device and OS).
3. Lighthouse on the web export: record performance and the initial JS size against the budget (R-002).
4. **Update A-002**: `raftly records update A-002 state=SUPPORTED` (or `INVALIDATED`) with the evidence id.

## After implementation (state and evidence updates)
1. Run the relevant tests/checks and keep the exact commands and outputs.
2. Compare the implementation with every acceptance criterion in the feature spec(s).
3. Record evidence: `raftly evidence record --subject F002 --kind test --result PASS|FAIL --summary "..." --command "..."` (and `--kind manual` for device checks, saying what was checked on which device).
4. Update status: `raftly graph set-status N003 IMPLEMENTED_UNVERIFIED`, then `VERIFIED` only with passing verification evidence; `raftly records feature-status F002 ...` likewise.
5. Record any deviation as an ADR, debt item or risk.
6. Do not mark COMPLETE unless verification passed and the Definition of Done is checked.

## Escalate instead of changing autonomously
- Any change to ADR-001 (client-only) or ADR-004 (Expo + React Native Web): both are Type-1.
- Any new dependency not in `dependencies.yaml`.
- Any change to calculator semantics in ADR-006 (product decision).
- Anything that weakens accessibility (REQ-005).
