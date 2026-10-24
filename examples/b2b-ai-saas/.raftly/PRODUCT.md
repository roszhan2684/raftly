# Product Document — SalesLens

## Vision
Every sales manager coaches from real moments in real calls, without listening to every call.

## Problem
Sales managers are expected to coach, but reviewing calls is slow: a manager with eight reps doing 15 calls a
week cannot listen to 120 hours of audio. Coaching becomes anecdotal, objections go unnoticed until deals are
lost, and competitive shifts surface late. Enterprise conversation-intelligence tools exist but are heavy and
priced for large organizations (**not verified**: competitor positioning and pricing need dated research; see RESEARCH.md #6).

## ICP / users
- **ICP (A-006):** B2B sales teams of 10–100 reps without an enterprise conversation-intelligence tool, recording calls on Zoom.
- **Buyer:** VP or Head of Sales. **Admin:** RevOps or a sales manager. **Primary user:** frontline sales managers. **Secondary user:** reps.

## Jobs
- When I prepare my weekly 1:1s, I want the coaching moments from my reps' calls, so I can coach on specifics in minutes.
- When a competitor shows up more often, I want to see it early, so I can arm the team.
- When I'm a rep, I want to see the moments my manager flagged, so I can handle the objection better next time.

## Workflows
**Today:** a manager listens to a few random calls at double speed, takes notes, and coaches from memory; reps rarely
revisit their own calls. **With SalesLens:** calls flow in (upload or Zoom) → transcripts and insights within the
hour → the manager triages a queue on Monday morning → shares 3–5 coaching notes → reps read them with quotes and audio.

## Positioning
For sales managers at growing B2B teams who need to coach without listening to every call, SalesLens is an AI
coaching assistant that surfaces objections, competitor mentions and coaching moments with the exact quote and
timestamp. Unlike enterprise conversation-intelligence suites, it is coaching-first, set up in under a day, and
priced for mid-market teams.

## Differentiation
Coaching workflow first (a queue, not a dashboard), evidence on every insight (verbatim quote + timestamp),
time-to-value under one day, privacy controls customers can see (retention, consent attestation, deletion).

## V1 / MVP
Orgs and roles · upload + Zoom import with consent attestation · diarized transcription · AI insights with
evidence · manager review queue with notes and sharing · rep coaching feed · team trends · trials, plans and
audio-hour metering · retention, export, deletion, audit log · weekly digest.

## Exclusions
- Real-time call assist (complexity, latency, consent)
- CRM write-back and CRM linking (ADR-011; REQ-015 COULD for V1.1)
- Training models on customer data (REQ-016)
- Meeting platforms other than Zoom (ADR-011)
- SAML SSO/SCIM (ADR-003 revisit trigger)

## Requirements
| ID | Requirement | Priority |
|---|---|---|
| REQ-001 | Isolated organizations with Admin/Manager/Rep roles | MUST |
| REQ-002 | Magic link + Google/Microsoft OIDC; invitations | MUST |
| REQ-003 | Upload (≤ 3 h) and Zoom cloud-recording import | MUST |
| REQ-004 | Diarized transcription distinguishing rep vs prospect | MUST |
| REQ-005 | Objections, competitors, coaching moments with quote, timestamp, confidence | MUST |
| REQ-006 | Manager review queue: accept/dismiss/edit, note, share | MUST |
| REQ-007 | Reps see only their own data unless granted | MUST |
| REQ-008 | Trends by team and rep | MUST |
| REQ-009 | Trial, plans, seats, audio-hour allowance | MUST |
| REQ-010 | Consent attestation and org consent policy notice | MUST |
| REQ-011 | Retention controls, export, deletion | MUST |
| REQ-012 | Objection precision ≥ 0.85, recall ≥ 0.80 before launch | MUST |
| REQ-013 | Weekly digest and share notifications | SHOULD |
| REQ-014 | Audit log | SHOULD |
| REQ-015 | CRM deal linking | COULD |
| REQ-016 | No real-time assist, CRM write-back or training on customer data | WONT |

## Feature map
| Feature | Requirements | Node |
|---|---|---|
| F001 Organizations, authentication and roles | REQ-001, REQ-002, REQ-007 | N002 (+ N003 isolation) |
| F002 Call ingestion and Zoom import | REQ-003, REQ-010 | N004 |
| F003 Transcription pipeline | REQ-004 | N005 |
| F004 Insight extraction | REQ-005, REQ-012 | N007 (eval harness N006) |
| F005 Manager review queue | REQ-006 | N008 |
| F006 Rep coaching view | REQ-007 | N009 |
| F007 Team trends | REQ-008 | N010 |
| F008 Billing and usage metering | REQ-009 | N011 |
| F009 Data governance and audit log | REQ-011, REQ-014 | N012 |
| F010 Notifications | REQ-013 | N013 |

## Success metrics
- **North star:** managers who action ≥ 3 insights per week (EXP-001 target ≥ 60% in the pilot).
- **Inputs:** time from first upload to first insight (< 1 hour); calls ingested per team per week; share rate.
- **Guardrails:** insight dismiss rate (< 40%), AI cost per audio hour (≤ COST.md budget), cross-tenant incidents (0).

## Assumptions
| ID | Assumption | Confidence | Validation |
|---|---|---|---|
| A-001 | Managers act on a weekly queue | 60 | EXP-001 |
| A-002 | Managed STT diarization is good enough | 55 | N005 spike |
| A-003 | LLM extraction reaches thresholds | 60 | N006/N007 eval |
| A-004 | Customers will upload/connect Zoom with attestation | 65 | Pilot activation |
| A-005 | Processing cost < 15% of seat revenue | 50 | COST.md + pilot metering |
| A-006 | Mid-market teams without CI tools are the ICP | 65 | Pilot recruitment |

## Risks
R-001 recording consent (legal) · R-002 cross-tenant exposure · R-003 wrong insights erode trust · R-004 AI cost ·
R-005 provider changes · R-006 prompt injection · R-007 crowded market · R-008 GDPR/residency. See risks.yaml.

## Kill criteria
EXP-001 (5 design-partner teams, 4 weeks): if fewer than 25% of managers action ≥ 3 insights per week, stop the
manager-queue bet and interview for a rep self-coaching repositioning before building further.
