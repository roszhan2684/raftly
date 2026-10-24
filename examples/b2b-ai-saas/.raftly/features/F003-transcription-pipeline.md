---
id: F003
name: Transcription pipeline
status: PLANNED
priority: MUST
owner_role: ai-ml
node: N005
requirements:
  - REQ-004
decisions:
  - ADR-006
  - ADR-005
depends_on:
  - F002
screens:
  - SCR-call-detail
evidence_status: NONE
updated_at: 2026-10-24
---
# F003 — Transcription pipeline

## Product goal
Accurate, diarized transcripts that attribute speech to the rep or the prospect (REQ-004).

## User story / jobs
As a manager, I want an accurate transcript with speakers identified, so insights point at what the prospect actually said.

## Actors
Worker (system), speech-to-text provider, Manager/Rep (read transcript).

## Entry conditions
Call in status `uploaded` with a consent attestation.

## Main flow
1. The transcription job sends audio to the provider (via `TranscriptionProvider`).
2. Receive words with timestamps and speaker labels.
3. Map the rep speaker (match with the rep's Zoom participant or a voice heuristic: the speaker with the most talk time on outbound calls, confirmed by the user on first view if confidence is low).
4. Store the transcript segments; status → `analyzing`; enqueue extraction.

## Alternative flows
Separate audio tracks available (Zoom) → per-track transcription, no diarization needed. Low diarization confidence → "Confirm who the rep is" prompt on the call page.

## State model
Transcription job: queued → running → succeeded | failed (retryable) | failed_permanent.

## Data model implications
`transcripts(call_id, provider, model_version, language)`, `transcript_segments(call_id, speaker_role, start_ms, end_ms, text)` with `org_id` + RLS. Full-text index for search (V1.1).

## API / contracts
Internal `TranscriptionProvider.transcribe(audioUrl, options) → Transcript`; `GET /api/calls/{id}/transcript`.

## Permissions
Read per call visibility rules (F001/F006).

## UI / screens
Transcript panel in SCR-call-detail (with speaker labels and click-to-seek).

## Edge cases
Silence or music-only files; non-English calls (detect and mark unsupported in V1 if the provider can't handle them); provider timeouts; very long calls split into chunks.

## Error behavior
Retries with backoff (3 attempts); permanent failure shows "We couldn't transcribe this call" with a retry action and the reason category.

## Empty / loading states
"Transcribing… usually under 10 minutes for a 1-hour call" (verify against the chosen provider in the spike).

## Analytics / metrics
Transcription success rate, duration vs processing time, cost per audio hour.

## Security / privacy requirements
Provider must contractually not train on our data and should support short retention (verify in the spike); audio URLs presigned and short-lived; transcripts inherit call retention.

## Accessibility requirements
The transcript is readable by screen readers with speaker labels; seek controls keyboard-operable.

## Observability
p95 transcription latency, failure rate by reason, provider error codes, cost per audio hour (alert above budget).

## Dependencies
F002; provider chosen by the N005 spike (ADR-006).

## Out of scope
- Translation
- Real-time transcription

## Tests
- Contract tests for the provider adapter with recorded responses
- Spike report: WER and diarization error on 30 labelled calls (evidence)
- Integration: retry and permanent-failure paths

## Acceptance criteria
- [ ] The spike selects a provider with recorded WER/diarization/cost evidence
- [ ] Transcripts store speaker roles and timestamps
- [ ] Failures are retried and surfaced honestly
- [ ] A-002 updated (SUPPORTED/INVALIDATED) with evidence

## Definition of Done
Mark `[x]` when done with evidence, `[~]` when not applicable (say why).
- [ ] Requirements satisfied
- [ ] UI implemented
- [ ] API implemented
- [ ] Logic/persistence implemented
- [ ] Authorization enforced server-side (RLS + role policy)
- [ ] Tenant isolation test for every new data path
- [ ] Validation present
- [ ] Loading / empty / error states
- [ ] Retries/idempotency where needed
- [ ] Accessibility checked
- [ ] Responsive behavior checked
- [ ] Tests written and passing
- [ ] Observability (logs/metrics/alerts) in place
- [ ] Security/privacy review
- [ ] Docs updated

## Evidence status
None yet. Evidence lives in `evidence.yaml` (`raftly evidence for F003`).
