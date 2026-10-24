---
id: F003
name: History
status: PLANNED
priority: SHOULD
owner_role: product-director
node: N004
requirements:
  - REQ-006
  - REQ-007
decisions:
  - ADR-001
  - ADR-005
depends_on:
  - F002
screens:
  - SCR-history
evidence_status: NONE
updated_at: 2026-10-24
---
# F003 — History

## Product goal
Reuse past results without re-typing (REQ-006).

## User story / jobs
As a user doing several related calculations, I want to see and reuse earlier results, so I can chain work quickly.

## Actors
End user.

## Entry conditions
At least one evaluated calculation exists (otherwise the empty state shows).

## Main flow
1. The user opens the history drawer (swipe up on mobile, button or `H` on web).
2. Entries are listed newest first: expression, result, relative time.
3. Tapping a result inserts it into the current expression; tapping the expression restores it for editing.
4. "Clear history" asks for inline confirmation, then removes all entries.

## Alternative flows
Long-press on an entry copies the result.

## State model
`entries: HistoryEntry[] (max 100, FIFO)`, persisted after each change.

## Data model implications
`HistoryEntry { id, expression, resultExact, createdAt }` stored in on-device storage (AsyncStorage on native, localStorage on web, behind one adapter). Contains no personal data. Cleared with app data.

## API / contracts
`history.add(entry)`, `history.list()`, `history.clear()`. Storage adapter interface `{ get, set, remove }`.

## Permissions
Not applicable.

## UI / screens
SCR-history: a drawer or bottom sheet on mobile, a side panel on wide web layouts.

## Edge cases
- Storage unavailable (private mode, quota): history works in memory for the session and shows a subtle "History won't be saved" note.
- Corrupted stored data: discard and start empty (logged to the console in dev only).
- The 101st entry evicts the oldest.

## Error behavior
Never blocks calculation. Storage failures degrade to session-only history.

## Empty / loading states
Empty: "Your calculations will appear here. History stays on this device." Loading: none visible (read at startup, < 50 ms).

## Analytics / metrics
None (ADR-008).

## Security / privacy requirements
Local only. Not synced or transmitted. The store privacy label stays "Data Not Collected".

## Accessibility requirements
The drawer is focus-trapped while open on web, has a close button, Escape closes it, and entries are buttons with labels like "12 times 7 equals 84".

## Observability
Not applicable (ADR-008).

## Dependencies
F002.

## Out of scope
Search, export, sync, editing past entries in place (direction C, post-V1).

## Tests
- Unit tests: FIFO cap, persistence round-trip, corrupted data recovery
- Component tests: reuse result, restore expression, clear with confirmation
- Manual: private browsing mode behaviour

## Acceptance criteria
- [ ] The last 100 calculations persist across restarts on all three surfaces
- [ ] Reusing a result inserts the exact value (not the rounded display)
- [ ] Clear history requires confirmation and empties storage
- [ ] Storage failure degrades gracefully with a visible note

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
None yet. Evidence lives in `evidence.yaml` (`raftly evidence for F003`).
