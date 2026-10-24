---
id: F002
name: Keypad and display
status: PLANNED
priority: MUST
owner_role: design-director
node: N003
requirements:
  - REQ-001
  - REQ-005
  - REQ-009
decisions:
  - ADR-005
  - ADR-006
  - ADR-007
  - ADR-004
depends_on:
  - F001
  - F005
screens:
  - SCR-main
evidence_status: NONE
updated_at: 2026-10-24
---
# F002 — Keypad and display

## Product goal
Fast, error-resistant input where users always see what will be computed (ADR-005).

## User story / jobs
As a user on my phone or the web, I want to tap or type a calculation and see the expression and a live result, so I catch mistakes before pressing equals.

## Actors
End user (touch, mouse, screen reader, switch control).

## Entry conditions
App launched (cold start under 1.5 s on mid-range devices; target to be measured in N003).

## Main flow
1. The user taps keys; the expression line updates (`12 × (3 + 4`).
2. The live preview shows the provisional result in a secondary colour once the expression is evaluable.
3. On `=`, the result becomes primary, the expression moves to the line above, and the entry is added to history (F003).
4. A long-press on the display copies the result (shared with F004's copy action).

## Alternative flows
- `C` clears the current entry; a long-press on `C` (or `AC`) clears everything.
- Backspace deletes the last token.
- Error result: the message replaces the result; the next digit starts a new expression.

## State model
`idle → typing → evaluated → (typing | error)`. The engine state is held in one reducer.

## Data model implications
None beyond the engine state.

## API / contracts
Consumes the F001 API. Emits `onEvaluated(entry)` for F003.

## Permissions
Not applicable.

## UI / screens
SCR-main: two-line display (expression, result) + 4×5 keypad: `C ( ) ÷ / 7 8 9 × / 4 5 6 − / 1 2 3 + / ± 0 . =` and `%` (placement per DESIGN.md), plus a history affordance.

## Edge cases
- Long expressions: the expression line scrolls horizontally, kept at the cursor end; the result font size steps down to fit 16 digits.
- Rotation and resizing keep the state.
- Very fast tapping: no dropped inputs (input queue processed in order).

## Error behavior
Inline message ("Can't divide by zero"), announced politely to screen readers, no modal dialogs.

## Empty / loading states
The empty display shows `0`. No loading state (local compute).

## Analytics / metrics
None (ADR-008).

## Security / privacy requirements
None beyond F001 (no `eval`).

## Accessibility requirements
- Each key has an accessible label ("divide", "plus or minus", "percent") and role button.
- Result changes are announced via a live region (web) or `accessibilityLiveRegion`/announcements (native), debounced while typing.
- Targets ≥ 44pt iOS / 48dp Android; contrast AA in both themes; works at 200% text size (keypad reflows).
- Haptics (REQ-009): a light impact on key press via expo-haptics, disabled when the system setting disables haptics; never the only feedback.

## Observability
Not applicable (ADR-008).

## Dependencies
F001 (engine), F005 (tokens), expo-haptics.

## Out of scope
Scientific keypad; landscape scientific mode.

## Tests
- Component tests: key presses → display state, error display, backspace, clear
- Accessibility tests: labels present; axe on the web build
- Manual: VoiceOver (iOS) and TalkBack (Android) pass; haptics on/off

## Acceptance criteria
- [ ] Every key produces the correct token and the display matches the engine output
- [ ] Live preview appears only for evaluable expressions
- [ ] Screen reader announces keys and results on iOS, Android and web
- [ ] Haptics respect the system setting
- [ ] Layout works from 320 px wide to desktop

## Definition of Done
Mark `[x]` when done with evidence, `[~]` when not applicable (say why).
- [ ] Requirements satisfied
- [ ] UI implemented
- [ ] Logic/persistence implemented
- [~] Authorization enforced server-side: N/A, client-only app (ADR-001)
- [ ] Validation present
- [ ] Loading / empty / error states
- [ ] Accessibility checked
- [ ] Responsive behavior checked
- [ ] Tests written and passing
- [~] Observability (logs/metrics): N/A, no telemetry by decision (ADR-008); errors are shown to the user
- [ ] Security/privacy review
- [ ] Docs updated

## Evidence status
None yet. Evidence lives in `evidence.yaml` (`raftly evidence for F002`).
