# Prompt {number} — {title}

> Build-graph node: **{node}** · Features: {features}
> Self-contained implementation prompt. Paste into Claude Code, or run `/raftly build next`.

## Role to activate
{role}

## Files to read first
- `.raftly/state.yaml` (current stage and node statuses)
- `.raftly/ARCHITECTURE.md` (boundaries you must respect)
- TBD — feature specs, ADRs, design docs this node depends on

## Objective
TBD

## Scope
TBD

## Dependencies
TBD — nodes that must already be VERIFIED/COMPLETE.

## Architecture / design constraints
- TBD

## Implementation tasks
1. TBD

## Explicitly out of scope
- TBD

## Edge cases
- TBD

## Security / accessibility requirements
- TBD

## Tests required
- TBD

## Verification steps
1. Run the relevant tests/checks and capture the command and result.
2. Compare the implementation with every acceptance criterion in the feature spec.

## After implementation (state and evidence updates)
1. Run relevant tests/checks.
2. Compare implementation with feature acceptance criteria.
3. Record evidence: `evidence.py record --subject <F/N id> --kind test --result PASS|FAIL --summary "..." --command "..."`.
4. Update status: `build_graph.py set-status {node} IMPLEMENTED_UNVERIFIED`, then `VERIFIED` only with passing evidence.
5. Record any deviation as an ADR, debt item or risk (`decisions.py` / `records.py`).
6. Do not mark COMPLETE unless verification passed and the Definition of Done is checked.

## Escalate instead of changing autonomously
- Any change to an accepted Type-1 decision (see DECISIONS.md).
- New third-party dependency or paid service not in `dependencies.yaml`.
- Anything that weakens security, privacy or accessibility requirements.
