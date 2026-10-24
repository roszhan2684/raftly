---
id: F004
name: Web keyboard and clipboard
status: PLANNED
priority: SHOULD
owner_role: frontend
node: N005
requirements:
  - REQ-008
  - REQ-007
decisions:
  - ADR-004
depends_on:
  - F002
screens:
  - SCR-main
evidence_status: NONE
updated_at: 2026-10-24
---
# F004 — Web keyboard and clipboard

## Product goal
Desktop users calculate at typing speed and move results in and out easily (REQ-007, REQ-008).

## User story / jobs
As a desktop user, I want to type calculations and paste expressions, so I don't have to click a keypad.

## Actors
End user on the web (keyboard, clipboard). Copy also applies on mobile.

## Entry conditions
Web app focused; no text input field elsewhere on the page has focus.

## Main flow
1. Keys map to tokens: `0–9 . + - * / ( ) %`, `Enter`/`=` evaluates, `Backspace` deletes, `Escape` clears, `Delete` clears all.
2. Pressing the matching on-screen key gives visual feedback (pressed state).
3. `Ctrl/Cmd+C` (with no text selected) copies the current result; the copy button and display long-press do the same on mobile.
4. `Ctrl/Cmd+V` pastes: the text is sanitised to the token grammar; invalid characters are rejected with a brief message.

## Alternative flows
`x`/`X` → `×`, `÷` and `:` → `÷`, `,` handled per locale decimal separator.

## State model
Stateless mapping layer feeding F002's reducer.

## Data model implications
None.

## API / contracts
`keyToToken(event, locale) → Token | null`; `sanitizePaste(text, locale) → Token[] | Error`.

## Permissions
The clipboard write uses the async Clipboard API (requires a secure context; falls back gracefully).

## UI / screens
SCR-main (pressed states, a toast "Copied" announced to screen readers).

## Edge cases
- Browser shortcuts (`Ctrl+R`, `Ctrl+L`, tab navigation) are never intercepted.
- Pasting a very long string is capped at 500 characters.
- Number-row vs numpad keys behave the same.

## Error behavior
Rejected paste: "Only numbers and + − × ÷ ( ) % can be pasted". Clipboard permission denied: "Couldn't copy, select the result and copy manually".

## Empty / loading states
Not applicable.

## Analytics / metrics
None (ADR-008).

## Security / privacy requirements
Pasted text is parsed by the tokenizer only, never evaluated as code. Clipboard is read only on an explicit paste event.

## Accessibility requirements
All functions are reachable by keyboard; the keyboard map is documented in a "Keyboard shortcuts" dialog (`?`); focus is always visible.

## Observability
Not applicable (ADR-008).

## Dependencies
F002; expo-clipboard (native copy).

## Out of scope
Custom key remapping.

## Tests
- Unit tests: key map, paste sanitiser (including locale separators)
- E2E (Playwright, web): type `12*(3+4)` Enter → `84`; paste flow; copy flow
- Manual: no conflicts with browser shortcuts in Chrome, Safari, Firefox

## Acceptance criteria
- [ ] All mapped keys work on Chrome, Safari and Firefox
- [ ] Paste accepts valid expressions and rejects others with a message
- [ ] Copy works on web and mobile and is announced
- [ ] No browser shortcut is intercepted

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
None yet. Evidence lives in `evidence.yaml` (`raftly evidence for F004`).
