---
id: F005
name: Theming and design tokens
status: PLANNED
priority: SHOULD
owner_role: design-systems
node: N002
requirements:
  - REQ-010
  - REQ-005
decisions:
  - ADR-007
  - ADR-005
depends_on: []
screens:
  - SCR-main
  - SCR-history
evidence_status: NONE
updated_at: 2026-10-24
---
# F005 — Theming and design tokens

## Product goal
A calm, legible interface in light and dark that follows the system and passes AA contrast (REQ-010, REQ-005).

## User story / jobs
As a user, I want the calculator to match my system theme and stay readable, so it is comfortable day and night.

## Actors
End user.

## Entry conditions
App start; system appearance changes at runtime.

## Main flow
1. Read the system colour scheme; apply the matching token set.
2. Re-theme live when the system appearance changes.

## Alternative flows
None in V1 (no manual theme toggle; revisit with feedback).

## State model
`theme: 'light' | 'dark'` derived from the system.

## Data model implications
None.

## API / contracts
`tokens.ts` exports the semantic tokens from DESIGN_SYSTEM.md; components never use raw colours.

## Permissions
Not applicable.

## UI / screens
All screens.

## Edge cases
High-contrast / increased-contrast settings: use the higher-contrast token variants where the platform exposes them.

## Error behavior
Not applicable.

## Empty / loading states
Not applicable.

## Analytics / metrics
None (ADR-008).

## Security / privacy requirements
None.

## Accessibility requirements
Every text/background token pair meets 4.5:1 (3:1 for large display digits and UI boundaries); focus ring token ≥ 3:1 against adjacent colours; respects reduced motion.

## Observability
Not applicable.

## Dependencies
None (foundation).

## Out of scope
Custom themes and accent pickers.

## Tests
- Unit test: token contrast checker over all pairs (automated)
- Visual check of SCR-main in both themes on each platform

## Acceptance criteria
- [ ] Light and dark follow the system on iOS, Android and web
- [ ] Automated contrast check passes for all token pairs
- [ ] No raw colour values in components (lint rule)

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
None yet. Evidence lives in `evidence.yaml` (`raftly evidence for F005`).
