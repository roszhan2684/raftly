# Prompt 005 — Transcription pipeline

> Build-graph node: **N005** · Features: F003
> Self-contained implementation prompt. Paste into Claude Code, or run `/raftly build next`.

## Role to activate
Principal AI/ML Engineer + Staff Backend Engineer

## Files to read first
- `.raftly/state.yaml`
- `.raftly/ARCHITECTURE.md` (module boundaries)
- `.raftly/features/F003-transcription-pipeline.md`
- `.raftly/decisions/ADR-006-*.md`
- `.raftly/research/ai-providers.md` (questions to answer)
- `.raftly/COST.md`

## Objective
Select the speech-to-text provider with evidence, then build a reliable diarized transcription pipeline.

## Scope
**Spike first:** 30 labelled (synthetic or consented) calls through two candidate providers → WER, diarization error, cost per audio hour, retention and training terms. Then the `TranscriptionProvider` interface, the adapter for the winner, the job, storage of segments, the rep-speaker mapping and failure handling.

## Dependencies
N004 VERIFIED or COMPLETE.

## Architecture / design constraints
- Provider behind an interface (ADR-006); no provider types leak into domain code.
- Use separate audio tracks when available (Zoom).
- Never send audio without a consent attestation.

## Implementation tasks
1. Research current provider docs and pricing (record in RESEARCH.md with dates; never guess).
2. Run the spike; write a spike report as evidence; record a RECOMMEND ADR (or update ADR-006) with the choice; update dependencies.yaml (ADOPTED, licence/terms verified).
3. Implement the adapter, the job with retries/backoff, segment storage, rep mapping + confirmation prompt.
4. Metering hook: emit `usage_events` on success (consumed by N011).
5. Update A-002 with the spike evidence.

## Explicitly out of scope
- Insight extraction (N007)
- Translation

## Edge cases
- Music/silence
- Non-English audio
- Provider timeouts
- Very long files

## Security / accessibility requirements
- Provider terms: no training on customer data (verify)
- Transcript panel accessible

## Tests required
- Adapter contract tests (recorded responses)
- Retry/permanent-failure integration tests
- Spike report

## Verification steps
- `raftly records update A-002 state=SUPPORTED|INVALIDATED`; record cost per audio hour in COST.md

## After implementation (state and evidence updates)
1. Run relevant tests/checks; keep the exact commands and outputs.
2. Compare the implementation with the feature acceptance criteria.
3. Record evidence: `raftly evidence record --subject F003 --kind test --result PASS|FAIL --summary "..." --command "..."`; register entities (`API-*`, `TBL-*`, `TEST-*`) and link them (`raftly evidence link`).
4. Update status: `raftly graph set-status N005 IMPLEMENTED_UNVERIFIED`, then `VERIFIED` only with passing verification evidence.
5. Record any deviation as an ADR, debt item or risk.
6. Do not mark COMPLETE unless verification passed and the Definition of Done is checked.

## Escalate instead of changing autonomously
- Any change to Type-1 decisions: ADR-001 (modular monolith), ADR-002 (Postgres + RLS tenancy), ADR-003 (auth), ADR-006/ADR-007 (AI providers).
- New third-party services or dependencies not in `dependencies.yaml`.
- Anything that weakens tenant isolation, consent handling or retention.
