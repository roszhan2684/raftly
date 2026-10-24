---
id: F001
name: Calculation engine
status: PLANNED
priority: MUST
owner_role: frontend
node: N001
requirements:
  - REQ-001
  - REQ-002
  - REQ-003
decisions:
  - ADR-002
  - ADR-003
  - ADR-006
depends_on: []
screens: []
evidence_status: NONE
updated_at: 2026-10-24
---
# F001 — Calculation engine

## Product goal
Every result Tally shows is correct and predictable. This is the product's core promise (REQ-001–003).

## User story / jobs
As anyone doing everyday maths, I want results that are exactly right and behave the way I expect, so I can trust the answer without double-checking.

## Actors
End user (indirectly through F002/F004); the UI layer as the engine's only client.

## Entry conditions
None. The engine is a pure module.

## Main flow
1. The UI sends the current input sequence (tokens) to `evaluate()`.
2. The tokenizer normalises input (leading `.` → `0.`, operator replacement, `±`).
3. The parser builds an expression tree with standard precedence and parentheses.
4. The evaluator computes with decimal.js (34 significant digits internally).
5. `format()` rounds half-even to ≤ 16 significant digits **for display only**, using scientific notation outside 1e-7…1e16, with locale-aware separators.
6. The result returns `{ value, display, expression, error? }`.

## Alternative flows
- Repeated equals: re-applies the last operator and operand (ADR-006).
- Percent: the contextual rules in ADR-006.
- Unbalanced parentheses: auto-closed on evaluate; the live preview shows the implied `)`.

## State model
`EngineState { tokens, lastOperation?: {op, operand}, lastResult? }`. Pure functions take and return state; nothing is global.

## Data model implications
None (client-only). `lastResult` is exact (a decimal string), never the rounded display string.

## API / contracts
`evaluate(tokens: Token[], state: EngineState): EvalResult` · `preview(tokens, state): string | null` · `format(value: string, opts: {locale, maxSig: 16}): string`. No UI imports (ADR-002).

## Permissions
Not applicable: no users or roles.

## UI / screens
None directly. Consumed by SCR-main (F002).

## Edge cases
- `0.1 + 0.2 = 0.3`; `1 ÷ 3 × 3 = 1` (internal precision, display rounding)
- `2 + 3 × 4 = 14`; `(2 + 3) × 4 = 20`; `−3² ` not supported in V1 (no exponent key)
- `5 ÷ 0` → error "Can't divide by zero"; `0 ÷ 0` → the same message
- `200 + 10%` = 220; `200 × 10%` = 20; `50%` = 0.5
- `5 + 3 = = =` → 8, 11, 14
- very large: `9999999999999999 × 10` → `1e17` (display); very small: `0.00000001` → `1e-8`
- operator after operator replaces it; `.` twice in a number is ignored
- empty input + `=` → no change

## Error behavior
Errors are values (`error: "DIVIDE_BY_ZERO" | "OVERFLOW"`); the engine never throws for user input. The UI maps codes to friendly copy.

## Empty / loading states
Not applicable (synchronous, pure).

## Analytics / metrics
None (ADR-008).

## Security / privacy requirements
Never use `eval`/`Function` on input. The parser accepts only the token grammar. No data leaves the device.

## Accessibility requirements
`format()` also returns a speakable form (e.g. "1.5 times 10 to the 17") for screen-reader announcements (used by F002).

## Observability
Not applicable: no telemetry by decision (ADR-008).

## Dependencies
decimal.js (ADR-003). No feature dependencies.

## Out of scope
- Scientific functions, exponents, memory keys (REQ-011)
- Unit conversion

## Tests
- Table-driven tests for every rule in ADR-006 and each edge case above
- Property-based tests: `a + b − b = a`; display(format(x)) round-trips; no thrown exceptions for random token sequences
- Precision regression suite (repeated operations do not drift)

## Acceptance criteria
- [ ] All ADR-006 semantics pass table-driven tests
- [ ] `0.1 + 0.2` displays `0.3`; repeated `=` does not drift after 1,000 iterations
- [ ] Fuzzing 10,000 random token sequences produces no exceptions
- [ ] Module has zero imports from React/React Native (lint rule)

## Definition of Done
Mark `[x]` when done with evidence, `[~]` when not applicable (say why).
- [ ] Requirements satisfied
- [~] UI implemented: N/A, the engine has no UI (F002)
- [ ] Logic/persistence implemented
- [~] Authorization enforced server-side: N/A, client-only app (ADR-001)
- [ ] Validation present
- [~] Loading / empty states: N/A, synchronous; errors are returned as values
- [ ] Accessibility checked
- [~] Responsive behavior: N/A, no UI
- [ ] Tests written and passing
- [~] Observability (logs/metrics): N/A, no telemetry by decision (ADR-008); errors are shown to the user
- [ ] Security/privacy review
- [ ] Docs updated

## Evidence status
None yet. Evidence lives in `evidence.yaml` (`raftly evidence for F001`).
