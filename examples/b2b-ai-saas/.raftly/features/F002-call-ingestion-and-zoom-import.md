---
id: F002
name: Call ingestion and Zoom import
status: PLANNED
priority: MUST
owner_role: backend
node: N004
requirements:
  - REQ-003
  - REQ-010
decisions:
  - ADR-004
  - ADR-011
  - ADR-012
  - ADR-005
depends_on:
  - F001
screens:
  - SCR-upload
  - SCR-integrations
evidence_status: NONE
updated_at: 2026-10-24
---
# F002 — Call ingestion and Zoom import

## Product goal
Calls get into SalesLens with minimal effort and with consent attested (REQ-003, REQ-010).

## User story / jobs
As a rep or manager, I want to upload a recording or have Zoom recordings imported automatically, so coaching starts without manual work.

## Actors
Rep, Manager, Admin (connects Zoom), Zoom (webhook).

## Entry conditions
Authenticated member; the org is within its audio-hour allowance (F008).

## Main flow
1. Upload: choose a file → attest consent (policy text shown) → resumable multipart upload direct to storage → server validates type, duration and size → creates `call` (status `uploaded`) → enqueues transcription.
2. Zoom: Admin connects Zoom (OAuth, minimum scopes) and attests consent for imported meetings → webhook on new cloud recording → import job downloads to storage → same pipeline.
3. The user assigns the rep (defaults to the uploader) and optional call title or account name.

## Alternative flows
Manual "import recent Zoom recordings" (last 30 days) for initial backfill. Allowance exceeded → upload blocked with an upgrade or contact-admin message.

## State model
Call: `uploading → uploaded → transcribing → analyzing → ready | failed(step, reason)`; the `deleted` state is handled by F009.

## Data model implications
`calls(org_id, rep_user_id, source, storage_key, duration_s, status, consent_attestation_id)`, `consent_attestations(org_id, user_id, policy_version, scope, created_at)`, `integrations(org_id, provider, encrypted_tokens, scopes)`.

## API / contracts
`POST /api/calls/uploads` (returns presigned multipart URLs) · `POST /api/calls/{id}/complete` · `POST /api/integrations/zoom/callback` · `POST /api/webhooks/zoom` (signature-verified).

## Permissions
Any member can upload calls for themselves; Managers can upload for their team's reps; Admins connect integrations. Server-side + RLS.

## UI / screens
SCR-upload (drag and drop, progress, attestation), SCR-integrations (Zoom connect/disconnect, status).

## Edge cases
3-hour max (reject longer files with a clear message); unsupported codec; duplicate upload (content hash check); Zoom token revoked; webhook replay; recordings with a single mixed audio track.

## Error behavior
Upload failures resume; validation failures explain the limits; failed imports show on the integrations page with a retry button.

## Empty / loading states
Empty call list: "Upload a call or connect Zoom to get started". Upload progress with remaining time.

## Analytics / metrics
`call_uploaded{source}`, `zoom_connected`, import success rate. No content in events.

## Security / privacy requirements
Presigned URLs short-lived and scoped to the org prefix; file type sniffed server-side; size and duration limits; Zoom tokens encrypted at rest (credentials class); webhook signature verification + idempotency (event id); consent attestation required before processing (REQ-010).

## Accessibility requirements
Drag-and-drop has a keyboard file-picker equivalent; progress announced; attestation checkbox labelled.

## Observability
Upload success/failure rate, import lag (webhook → stored), storage bytes per org, job queue depth.

## Dependencies
F001; object storage (ADR-004); job queue (ADR-005); allowance check (F008).

## Out of scope
- Google Meet / Teams import (ADR-011)
- Live call capture

## Tests
- Integration: presign → complete → job enqueued; duplicate detection; allowance blocking
- Security: webhook signature failure rejected; replayed event ignored; cross-org storage key access denied
- E2E: upload a sample file → status reaches `transcribing`

## Acceptance criteria
- [ ] Upload of supported files up to 3 hours works and resumes after interruption
- [ ] Zoom recordings import automatically after connection
- [ ] No call is processed without a consent attestation
- [ ] Webhooks are verified and idempotent

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
None yet. Evidence lives in `evidence.yaml` (`raftly evidence for F002`).
