# Prompt 001 — Calculation engine

> Build-graph node: **N001** · Features: F001
> Self-contained implementation prompt. Paste into Claude Code, or run `/raftly build next`.

## Role to activate
Staff Frontend Engineer (correctness-focused), with the Staff QA Engineer for test design.

## Files to read first
- `.raftly/state.yaml`
- `.raftly/features/F001-calculation-engine.md` (the full spec and edge cases)
- `.raftly/decisions/ADR-002-*.md` (engine boundary), `ADR-003-*.md` (decimal.js), `ADR-006-*.md` (semantics)
- `.raftly/learnings/L-001-*.md` (display-only rounding)

## Objective
Implement a pure TypeScript calculation engine that encodes every rule in ADR-006 with exact decimal arithmetic.

## Scope
Tokenizer, parser (precedence + parentheses), evaluator (decimal.js), repeated-equals state, percent rules, formatter (display + speakable), error values.

## Dependencies
None. This is a foundation node.

## Architecture / design constraints
- `src/engine/` (or `packages/engine/`), with **no** React/React Native imports (add a lint rule that enforces this).
- Never run input as code, and no regex-based evaluation; a real parser over the token grammar.
- decimal.js configured once in the engine (precision 34, rounding half-even). Rounding happens only in `format()`.
- Pure functions; state passed in and returned.

## Implementation tasks
1. Define `Token`, `EngineState`, `EvalResult` and error codes.
2. Tokenizer: digits, decimal point rules, operators, parentheses, `±`, `%`, operator replacement.
3. Parser: shunting-yard or recursive descent with precedence (× ÷ over + −), auto-closing parentheses on evaluate.
4. Evaluator with decimal.js; percent semantics exactly as in ADR-006; divide-by-zero → error value.
5. Repeated equals via `lastOperation`.
6. `preview()` for the live expression line (null when not evaluable).
7. `format()`: ≤ 16 significant digits, round half-even, scientific notation outside 1e-7…1e16, locale separators; a `speakable` variant.

## Explicitly out of scope
UI, persistence, keyboard mapping, exponent/scientific functions.

## Edge cases
All edge cases listed in F001, including `0.1 + 0.2`, `1 ÷ 3 × 3`, `5 + 3 = = =`, `200 + 10%`, `5 ÷ 0`, and very large/small numbers.

## Security / accessibility requirements
- No dynamic code evaluation (security).
- `format()` returns a speakable string used for screen-reader announcements.

## Tests required
- Table-driven tests: one row per ADR-006 rule and F001 edge case.
- Property-based tests (e.g. fast-check, if adopted, recorded in dependencies.yaml): no exceptions on random token sequences; additive inverse; format/parse round-trip.
- Precision drift test: 1,000 repeated equals.

## Verification steps
1. Run the engine test suite; record the command and the pass count.
2. Run the lint rule proving zero UI imports.
3. Walk F001's acceptance criteria one by one.

## After implementation (state and evidence updates)
1. Run the relevant tests/checks and keep the exact commands and outputs.
2. Compare the implementation with every acceptance criterion in the feature spec(s).
3. Record evidence: `raftly evidence record --subject F001 --kind test --result PASS|FAIL --summary "..." --command "..."` (and `--kind manual` for device checks, saying what was checked on which device).
4. Update status: `raftly graph set-status N001 IMPLEMENTED_UNVERIFIED`, then `VERIFIED` only with passing verification evidence; `raftly records feature-status F001 ...` likewise.
5. Record any deviation as an ADR, debt item or risk.
6. Do not mark COMPLETE unless verification passed and the Definition of Done is checked.

## Escalate instead of changing autonomously
- Any change to ADR-001 (client-only) or ADR-004 (Expo + React Native Web): both are Type-1.
- Any new dependency not in `dependencies.yaml`.
- Any change to calculator semantics in ADR-006 (product decision).
- Anything that weakens accessibility (REQ-005).
