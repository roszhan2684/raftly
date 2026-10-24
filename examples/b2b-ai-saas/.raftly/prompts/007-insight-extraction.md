# Prompt 007 — Insight extraction

> Build-graph node: **N007** · Features: F004
> Self-contained implementation prompt. Paste into Claude Code, or run `/raftly build next`.

## Role to activate
Principal AI/ML Engineer

## Files to read first
- `.raftly/state.yaml`
- `.raftly/ARCHITECTURE.md` (module boundaries)
- `.raftly/features/F004-insight-extraction.md`
- `.raftly/decisions/ADR-007-*.md`, `ADR-008-*.md`
- `.raftly/research/ai-providers.md`
- N006 harness docs

## Objective
Detect objections, competitor mentions and coaching moments with verifiable evidence, meeting the ADR-008 thresholds at budgeted cost.

## Scope
The `ExtractionProvider` interface + Anthropic adapter, versioned prompts with a JSON schema, chunking, validation (schema, verbatim quote, timestamps, competitor list), dedupe, confidence threshold, storage, cost/tokens metering, failure handling and the prompt-injection test suite.

## Dependencies
N005 and N006 VERIFIED or COMPLETE.

## Architecture / design constraints
- Confirm the current model capabilities, limits, pricing and data-use terms from official docs before choosing a model (record in RESEARCH.md).
- Transcript content is untrusted data: no tools, no instruction following, schema-only output.
- Model choice by eval quality and cost, recorded in ADR-007 (update) or a new ADR.

## Implementation tasks
1. Implement the interface and adapter; configure per-environment models.
2. Prompt v1 with a schema; chunking aligned to speaker turns.
3. Validation pipeline and dedupe; drop below-threshold items.
4. Persist insights + `ai_runs` (tokens, cost estimate, latency).
5. Iterate prompts against the N006 harness until thresholds pass; record each full run as evidence.
6. Injection test transcripts (e.g. a prospect saying "ignore previous instructions").

## Explicitly out of scope
- Review UI (N008)
- Training on customer data (REQ-016)

## Edge cases
- Competitor named by the rep
- Objection spanning windows
- Empty results (valid)

## Security / accessibility requirements
- G-SEC-AI, G-AI-EVALS, G-AI-FALLBACK, G-AI-COST evidence
- Confidence shown in text

## Tests required
- Harness full run meeting thresholds
- Unit tests for validation/dedupe
- Injection suite

## Verification steps
- `raftly records update A-003 state=...` with the eval evidence id

## After implementation (state and evidence updates)
1. Run relevant tests/checks; keep the exact commands and outputs.
2. Compare the implementation with the feature acceptance criteria.
3. Record evidence: `raftly evidence record --subject F004 --kind test --result PASS|FAIL --summary "..." --command "..."`; register entities (`API-*`, `TBL-*`, `TEST-*`) and link them (`raftly evidence link`).
4. Update status: `raftly graph set-status N007 IMPLEMENTED_UNVERIFIED`, then `VERIFIED` only with passing verification evidence.
5. Record any deviation as an ADR, debt item or risk.
6. Do not mark COMPLETE unless verification passed and the Definition of Done is checked.

## Escalate instead of changing autonomously
- Any change to Type-1 decisions: ADR-001 (modular monolith), ADR-002 (Postgres + RLS tenancy), ADR-003 (auth), ADR-006/ADR-007 (AI providers).
- New third-party services or dependencies not in `dependencies.yaml`.
- Anything that weakens tenant isolation, consent handling or retention.
- Lowering ADR-008 thresholds (founder/product decision).
