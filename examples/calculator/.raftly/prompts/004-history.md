# Prompt 004 — History

> Build-graph node: **N004** · Features: F003

## Role to activate
Staff Frontend Engineer.

## Files to read first
- `.raftly/features/F003-history.md`
- `.raftly/DESIGN.md` (SCR-history), `.raftly/decisions/ADR-001-*.md` (local only)

## Objective
A local, capped (100) history with reuse, restore and clear, persisted through a storage adapter.

## Scope
Storage adapter (native and web), the history store, SCR-history UI (drawer/sheet/panel), the empty state, degradation when storage is unavailable.

## Dependencies
N003 VERIFIED or COMPLETE.

## Architecture / design constraints
Storage is behind an adapter interface; entries store the exact result string; no network, no sync.

## Implementation tasks
1. Adapter `{get,set,remove}` with AsyncStorage (native) and localStorage (web) implementations.
2. History store with a FIFO cap of 100; load at startup; persist on change.
3. SCR-history UI per DESIGN.md with entries as accessible buttons.
4. Reuse result / restore expression / clear with inline confirmation.
5. Storage failure → session-only mode with a note.

## Explicitly out of scope
Search, export, sync, editing entries in place.

## Edge cases
Corrupted JSON, quota exceeded, private browsing, the 101st entry.

## Security / accessibility requirements
Local only. Focus trap + Escape on web; labelled entries.

## Tests required
Unit tests (cap, round-trip, corruption); component tests (reuse, restore, clear); manual private-mode test.

## Verification steps
Tests pass; restart persistence verified on iOS, Android and web; record the evidence.

## After implementation (state and evidence updates)
1. Run the relevant tests/checks and keep the exact commands and outputs.
2. Compare the implementation with every acceptance criterion in the feature spec(s).
3. Record evidence: `raftly evidence record --subject F003 --kind test --result PASS|FAIL --summary "..." --command "..."` (and `--kind manual` for device checks, saying what was checked on which device).
4. Update status: `raftly graph set-status N004 IMPLEMENTED_UNVERIFIED`, then `VERIFIED` only with passing verification evidence; `raftly records feature-status F003 ...` likewise.
5. Record any deviation as an ADR, debt item or risk.
6. Do not mark COMPLETE unless verification passed and the Definition of Done is checked.

## Escalate instead of changing autonomously
- Any change to ADR-001 (client-only) or ADR-004 (Expo + React Native Web): both are Type-1.
- Any new dependency not in `dependencies.yaml`.
- Any change to calculator semantics in ADR-006 (product decision).
- Anything that weakens accessibility (REQ-005).
