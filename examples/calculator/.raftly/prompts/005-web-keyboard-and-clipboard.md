# Prompt 005 — Web keyboard and clipboard

> Build-graph node: **N005** · Features: F004

## Role to activate
Staff Frontend Engineer.

## Files to read first
- `.raftly/features/F004-web-keyboard-and-clipboard.md`
- `.raftly/DESIGN.md` (keyboard behaviour), the engine tokenizer API

## Objective
Keyboard input, copy and safe paste on the web; copy on mobile.

## Scope
Key-to-token mapping, the shortcuts dialog (`?`), the copy action (button, long-press, Ctrl/Cmd+C), the paste sanitiser.

## Dependencies
N003 VERIFIED or COMPLETE.

## Architecture / design constraints
Mapping is a pure function feeding the existing reducer; never intercept browser shortcuts; pasted text goes through the tokenizer only.

## Implementation tasks
1. `keyToToken(event, locale)` and the global key listener (ignored when a text field has focus).
2. Pressed-state feedback on the matching on-screen key.
3. Copy via the async Clipboard API (web) and expo-clipboard (native), with a "Copied" announcement.
4. `sanitizePaste(text, locale)` with a 500-character cap and friendly rejection messages.
5. The keyboard shortcuts dialog.

## Explicitly out of scope
Custom remapping.

## Edge cases
Numpad vs number row; locale decimal comma; clipboard permission denied; insecure context.

## Security / accessibility requirements
No code evaluation of paste; all features keyboard-reachable; visible focus.

## Tests required
Unit tests (map, sanitiser); Playwright E2E for type/evaluate/copy/paste on Chromium, WebKit and Firefox.

## Verification steps
E2E passes on all three browser engines; manual check that no browser shortcut is intercepted; record the evidence.

## After implementation (state and evidence updates)
1. Run the relevant tests/checks and keep the exact commands and outputs.
2. Compare the implementation with every acceptance criterion in the feature spec(s).
3. Record evidence: `raftly evidence record --subject F004 --kind test --result PASS|FAIL --summary "..." --command "..."` (and `--kind manual` for device checks, saying what was checked on which device).
4. Update status: `raftly graph set-status N005 IMPLEMENTED_UNVERIFIED`, then `VERIFIED` only with passing verification evidence; `raftly records feature-status F004 ...` likewise.
5. Record any deviation as an ADR, debt item or risk.
6. Do not mark COMPLETE unless verification passed and the Definition of Done is checked.

## Escalate instead of changing autonomously
- Any change to ADR-001 (client-only) or ADR-004 (Expo + React Native Web): both are Type-1.
- Any new dependency not in `dependencies.yaml`.
- Any change to calculator semantics in ADR-006 (product decision).
- Anything that weakens accessibility (REQ-005).
