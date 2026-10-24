# Prompt 007 — Launch readiness

> Build-graph node: **N007** · Features: F002–F006 (verification pass)

## Role to activate
Launch Director + Staff QA Engineer. Optionally run the `raftly-launch-reviewer` agent for an independent challenge.

## Files to read first
- `.raftly/gate.yaml` (applicable checks: 16 production, plus the Forgotten-20 items)
- `.raftly/LAUNCH.md`, `.raftly/SECURITY.md`, `.raftly/risks.yaml` (R-004 store review)
- `references/production-gate.md` in the Raftly skill

## Objective
Collect real evidence for every applicable production-gate check and reach READY or READY_WITH_WARNINGS honestly.

## Scope
Accessibility audit, platform matrix, dependency audit, secrets check, legal pages review, store listings, regression run, support contact, the gate report.

## Dependencies
N004, N005, N006 VERIFIED or COMPLETE.

## Architecture / design constraints
No new features. Fixes found here go into the owning node (status back to IN_PROGRESS) or become debt.

## Implementation tasks
1. Accessibility: axe on web + manual VoiceOver/TalkBack/keyboard passes on key flows (G-A11Y).
2. Platform matrix: oldest supported + current iOS/Android, small and large screens; Chrome/Safari/Firefox (G-TEST-PLATFORMS).
3. Dependency audit with no unmitigated critical/high advisories (G-SEC-DEPS); secrets scan (G-SEC-SECRETS).
4. Full regression + CI evidence (G-TEST-AUTOMATED, G-TEST-REGRESSION, G-PRODUCT-SCOPE, G-PRODUCT-FLOWS).
5. Performance budget evidence (G-PERF); rollback rehearsal evidence (G-ROLLBACK).
6. Privacy policy reviewed (G-LEGAL-DOCS: needs a human review record); store listing + privacy labels (G-STORE); support contact visible (G-SUPPORT).
7. G-CLIENT-ERRORS: record the ADR-008 opt-out as the evidence-backed decision.
8. `raftly gate report --write` and the Forgotten-20 report; then `raftly deck --kind launch`.

## Explicitly out of scope
New functionality.

## Edge cases
Store rejection (R-004): document the response plan; don't mark G-STORE PASS until approved.

## Security / accessibility requirements
Never mark PASS without an evidence id. Unknowns stay UNVERIFIED.

## Tests required
As listed per gate check.

## Verification steps
`raftly gate score` shows READY or READY_WITH_WARNINGS with coverage ≥ 60%; `raftly validate` has zero errors.

## After implementation (state and evidence updates)
1. Run the relevant tests/checks and keep the exact commands and outputs.
2. Compare the implementation with every acceptance criterion in the feature spec(s).
3. Record evidence: `raftly evidence record --subject F002 --kind test --result PASS|FAIL --summary "..." --command "..."` (and `--kind manual` for device checks, saying what was checked on which device).
4. Update status: `raftly graph set-status N007 IMPLEMENTED_UNVERIFIED`, then `VERIFIED` only with passing verification evidence; `raftly records feature-status F002 ...` likewise.
5. Record any deviation as an ADR, debt item or risk.
6. Do not mark COMPLETE unless verification passed and the Definition of Done is checked.

## Escalate instead of changing autonomously
- Any change to ADR-001 (client-only) or ADR-004 (Expo + React Native Web): both are Type-1.
- Any new dependency not in `dependencies.yaml`.
- Any change to calculator semantics in ADR-006 (product decision).
- Anything that weakens accessibility (REQ-005).
