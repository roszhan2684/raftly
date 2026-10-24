# Prompt 006 — AI eval harness

> Build-graph node: **N006** · Features: F004
> Self-contained implementation prompt. Paste into Claude Code, or run `/raftly build next`.

## Role to activate
Principal AI/ML Engineer + Staff QA Engineer

## Files to read first
- `.raftly/state.yaml`
- `.raftly/ARCHITECTURE.md` (module boundaries)
- `.raftly/decisions/ADR-008-*.md` (thresholds)
- `.raftly/features/F004-insight-extraction.md` (output schema)
- Skill reference `ai.md`

## Objective
Create the versioned golden dataset and the evaluation harness that gate every prompt or model change.

## Scope
Labelling guidelines, a dataset of ~150 labelled transcript segments (objection categories, competitor mentions, coaching moments, negatives) from synthetic or consented sources, a metrics runner (precision/recall per category, quote validity, hallucination rate), a CI job on a sample, and a full-run report command.

## Dependencies
N001 VERIFIED or COMPLETE (independent of identity work, so it can run in parallel).

## Architecture / design constraints
- The dataset is versioned (`evals/dataset/v1`), with PII handled under the same rules as production data.
- The harness calls the same `ExtractionProvider` interface the product uses.
- Thresholds from ADR-008 are configuration, not code.

## Implementation tasks
1. Write labelling guidelines with category definitions and examples.
2. Build the dataset (synthetic scripts + consented pilot calls only).
3. Metrics runner + report (markdown/JSON) with per-category confusion.
4. CI job on a 30-case sample; full-run command for releases.
5. Baseline run with a trivial prompt to validate the plumbing.

## Explicitly out of scope
- Production extraction code (N007)

## Edge cases
- Label disagreement (two labellers on 20% of cases; report agreement)
- Class imbalance

## Security / accessibility requirements
- No real customer data without consent
- Reports never contain secrets

## Tests required
- Unit tests for the metrics
- CI sample job green

## Verification steps
- Record the harness and dataset as evidence (`--kind audit`); ready for N007 to use

## After implementation (state and evidence updates)
1. Run relevant tests/checks; keep the exact commands and outputs.
2. Compare the implementation with the feature acceptance criteria.
3. Record evidence: `raftly evidence record --subject F004 --kind test --result PASS|FAIL --summary "..." --command "..."`; register entities (`API-*`, `TBL-*`, `TEST-*`) and link them (`raftly evidence link`).
4. Update status: `raftly graph set-status N006 IMPLEMENTED_UNVERIFIED`, then `VERIFIED` only with passing verification evidence.
5. Record any deviation as an ADR, debt item or risk.
6. Do not mark COMPLETE unless verification passed and the Definition of Done is checked.

## Escalate instead of changing autonomously
- Any change to Type-1 decisions: ADR-001 (modular monolith), ADR-002 (Postgres + RLS tenancy), ADR-003 (auth), ADR-006/ADR-007 (AI providers).
- New third-party services or dependencies not in `dependencies.yaml`.
- Anything that weakens tenant isolation, consent handling or retention.
