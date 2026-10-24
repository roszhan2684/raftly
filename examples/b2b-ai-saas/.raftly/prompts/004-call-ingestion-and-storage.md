# Prompt 004 — Call ingestion and storage

> Build-graph node: **N004** · Features: F002
> Self-contained implementation prompt. Paste into Claude Code, or run `/raftly build next`.

## Role to activate
Staff Backend Engineer

## Files to read first
- `.raftly/state.yaml`
- `.raftly/ARCHITECTURE.md` (module boundaries)
- `.raftly/features/F002-call-ingestion-and-zoom-import.md`
- `.raftly/decisions/ADR-004-*.md`, `ADR-005-*.md`, `ADR-011-*.md`, `ADR-012-*.md`

## Objective
Get recordings in (upload + Zoom), consent-attested, stored per tenant, and enqueued for transcription.

## Scope
Presigned multipart upload, completion validation, the consent attestation flow, the `calls`/`consent_attestations`/`integrations` tables with RLS, the Zoom OAuth app and webhook, import jobs, and the SCR-upload and SCR-integrations screens.

## Dependencies
N003 VERIFIED or COMPLETE.

## Architecture / design constraints
- Storage keys under `org/{org_id}/` only; presigned URLs ≤ 15 minutes.
- pg-boss jobs with the org context and idempotency keys.
- Allowance check stub calling F008's interface (returns allowed until N011).

## Implementation tasks
1. Upload API + client with resumable multipart and progress.
2. Server-side validation (type sniffing, duration probe, 3-hour cap, content hash dedupe).
3. Consent attestation UI and record (policy version).
4. Zoom OAuth (minimum scopes), encrypted token storage, webhook signature verification, event idempotency, the import job, and "import recent".
5. Enqueue transcription on success; call status transitions.

## Explicitly out of scope
- Transcription itself (N005)
- Other meeting platforms

## Edge cases
- Interrupted uploads
- Duplicate webhooks
- Revoked Zoom tokens
- Single mixed-track audio

## Security / accessibility requirements
- G-SEC-UPLOADS and G-SEC-WEBHOOKS evidence
- Keyboard-accessible file picker; progress announced

## Tests required
- Integration tests (presign/complete/enqueue, dedupe, consent required)
- Webhook signature + replay tests
- E2E upload

## Verification steps
- Every new table added to the isolation suite (extend N003's tests)

## After implementation (state and evidence updates)
1. Run relevant tests/checks; keep the exact commands and outputs.
2. Compare the implementation with the feature acceptance criteria.
3. Record evidence: `raftly evidence record --subject F002 --kind test --result PASS|FAIL --summary "..." --command "..."`; register entities (`API-*`, `TBL-*`, `TEST-*`) and link them (`raftly evidence link`).
4. Update status: `raftly graph set-status N004 IMPLEMENTED_UNVERIFIED`, then `VERIFIED` only with passing verification evidence.
5. Record any deviation as an ADR, debt item or risk.
6. Do not mark COMPLETE unless verification passed and the Definition of Done is checked.

## Escalate instead of changing autonomously
- Any change to Type-1 decisions: ADR-001 (modular monolith), ADR-002 (Postgres + RLS tenancy), ADR-003 (auth), ADR-006/ADR-007 (AI providers).
- New third-party services or dependencies not in `dependencies.yaml`.
- Anything that weakens tenant isolation, consent handling or retention.
