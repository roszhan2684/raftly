---
id: F004
name: Insight extraction
status: PLANNED
priority: MUST
owner_role: ai-ml
node: N007
requirements:
  - REQ-005
  - REQ-012
decisions:
  - ADR-007
  - ADR-008
depends_on:
  - F003
screens:
  - SCR-call-detail
evidence_status: NONE
updated_at: 2026-10-24
---
# F004 — Insight extraction

## Product goal
Find objections, competitor mentions and coaching opportunities with evidence, at agreed quality (REQ-005, REQ-012).

## User story / jobs
As a manager, I want the moments that matter surfaced with quotes and timestamps, so I can coach without listening to whole calls.

## Actors
Worker, LLM provider, Manager/Rep (consumers).

## Entry conditions
Transcript stored; call status `analyzing`; org within allowance.

## Main flow
1. Chunk the transcript into overlapping windows aligned to speaker turns.
2. Call `ExtractionProvider` with a versioned prompt + JSON schema: `{type: objection|competitor|coaching, category, quote, start_ms, speaker_role, confidence, rationale}`.
3. Validate: schema; the quote exists verbatim in the window; timestamps inside the window; competitor matches the org list or a known-competitor dictionary.
4. Deduplicate across windows; drop items below the confidence threshold.
5. Store insights (status `new`); call status → `ready`; record cost and tokens.

## Alternative flows
Provider error → retry, then a fallback model if configured; persistent failure → call `ready` with "Insights unavailable" and a retry action.

## State model
Insight: `new → accepted | edited | dismissed`; `shared` flag (F005).

## Data model implications
`insights(org_id, call_id, type, category, quote, start_ms, speaker_role, confidence, prompt_version, model)`, `ai_runs(org_id, call_id, tokens_in, tokens_out, cost_estimate, latency_ms)`.

## API / contracts
Internal `ExtractionProvider.extract(window, config) → Insight[]`; `GET /api/calls/{id}/insights`.

## Permissions
Same as call visibility.

## UI / screens
Insight markers on the call timeline and an insights list in SCR-call-detail.

## Edge cases
Prospect quotes the rep; sarcasm; competitor named by the rep, not the prospect; objections spanning windows; transcripts containing instructions (prompt injection R-006).

## Error behavior
Invalid model output is discarded and logged (no partial garbage shown); a cost-limit breach pauses analysis for the org and notifies the Admin.

## Empty / loading states
"No objections detected" is shown as a real result, not an error; analyzing spinner with an estimated time.

## Analytics / metrics
Insights per call by type; dismiss rate (quality signal); cost per call.

## Security / privacy requirements
Transcript treated as data: no tools, no instructions honoured from content, schema-only output, output escaped when rendered; no customer data used for training (REQ-016); provider data-use terms verified.

## Accessibility requirements
Insight markers have text equivalents; confidence conveyed in text, not colour alone.

## Observability
Extraction success rate, schema-failure rate, p95 latency per call, tokens and cost per call and per org (alerts), dismiss rate trend.

## Dependencies
F003 transcripts; N006 eval harness (thresholds must pass before VERIFIED).

## Out of scope
- Sentiment scores
- Talk-ratio analytics (V1.1 candidate)

## Tests
- Eval harness run on the golden dataset: precision/recall per category vs ADR-008 thresholds (evidence)
- Unit: quote verification, dedupe, threshold filter
- Security: injection test transcripts produce no instruction-following behaviour

## Acceptance criteria
- [ ] Objection precision ≥ 0.85 and recall ≥ 0.80 on the eval set (recorded run)
- [ ] Every insight's quote exists verbatim in the transcript
- [ ] Cost per call recorded and within the COST.md budget
- [ ] Injection test suite passes

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
None yet. Evidence lives in `evidence.yaml` (`raftly evidence for F004`).
