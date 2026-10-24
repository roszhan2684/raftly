---
marp: true
theme: default
paginate: true
header: "SalesLens"
style: |
  section { font-family: system-ui, sans-serif; }
  h1 { color: #4338CA; }
---

# SalesLens

An AI coaching assistant that ingests sales calls (upload or Zoom), transcribes them, and surfaces objections, competitor mentions and coaching moments, each with the exact quote and timestamp, in a manager review queue.

<!--
Speaker notes: One-sentence vision. Who it is for and why now.
-->

---

# Problem

Sales managers are expected to coach, but reviewing calls is slow: a manager with eight reps doing 15 calls a week cannot listen to 120 hours of audio. Coaching becomes anecdotal, objections go unnoticed until deals are lost, and competitive shifts surface late.

<!--
Speaker notes: The pain in the user's words; evidence from RESEARCH.md.
-->

---

# Who it's for

- **ICP (A-006):** B2B sales teams of 10–100 reps without an enterprise conversation-intelligence tool, recording calls on Zoom.
- **Buyer:** VP or Head of Sales. **Admin:** RevOps or a sales manager. **Primary user:** frontline sales managers. **Secondary user:** reps.

<!--
Speaker notes: Primary user / ICP and the job they hire the product for.
-->

---

# Today's workflow and its pain

**Today:** a manager listens to a few random calls at double speed, takes notes, and coaches from memory; reps rarely revisit their own calls.

<!--
Speaker notes: What users do today and where it breaks.
-->

---

# Proposed solution

Orgs and roles · upload + Zoom import with consent attestation · diarized transcription · AI insights with evidence · manager review queue with notes and sharing · rep coaching feed · team trends · trials, plans and audio-hour metering · retention, export, deletion, audit log · weekly digest.

<!--
Speaker notes: Scope of V1 and what is explicitly excluded.
-->

---

# Core experience

- **Action over analytics**: the first screen asks a manager to act, not to interpret charts.
- **Evidence everywhere**: every insight shows the quote, the timestamp and a play button.
- **Respect the rep**: coaching is shared deliberately, never automatically broadcast.
- **Calm density**: a pro tool for weekly use. Dense lists, clear hierarchy, keyboard-first triage.

<!--
Speaker notes: The main flow end to end.
-->

---

# Design direction

**A as the manager home, B as the call detail view, C as the Trends tab** (ADR-009, confidence 70). Validated by EXP-001.

<!--
Speaker notes: Options considered and why this direction won.
-->

---

# Architecture

A TypeScript modular monolith (ADR-001): the `web` process (Next.js UI + API routes) and the `worker` process (pg-boss consumers) share domain modules. PostgreSQL holds all relational data with row-level-security tenancy (ADR-002) and the job queue (ADR-005).

<!--
Speaker notes: Simplest architecture that satisfies the requirements; Type-1 decisions.
-->

---

# Build plan

- **Phase 0:** Platform foundation
- **Phase 1:** Identity and organizations, AI eval harness and golden dataset
- **Phase 2:** RBAC and tenant isolation
- **Phase 3:** Call ingestion and storage, Billing and usage metering
- **Phase 4:** Transcription pipeline, Data governance
- **Phase 5:** Insight extraction
- **Phase 6:** Manager review queue, Team trends
- **Phase 7:** Rep coaching view, Notifications
- **Phase 8:** Launch readiness

<!--
Speaker notes: Dependency-ordered build graph: 14 capabilities, 10 feature specs. No calendar promises.
-->

---

# Security, privacy & compliance

SalesLens processes confidential sales conversations containing personal data of customers' employees and prospects. The security posture focuses on tenant isolation, server-side authorization, protection of recordings and integration credentials, webhook integrity, and AI-specific risks.

<!--
Speaker notes: Readiness, not certification. Items needing professional review are flagged.
-->

---

# Business & go-to-market

For sales managers at growing B2B teams who need to coach without listening to every call, SalesLens is a coaching-first AI assistant that surfaces objections, competitor mentions and coaching moments with the exact quote.

<!--
Speaker notes: Positioning, channels, pricing inputs.
-->

---

# Launch plan & risks

- **HIGH** Recordings contain third-party personal data and recording-consent laws differ by jurisdiction → Consent attestation and policy notice (REQ-010), retention controls, DPA, legal review before launch
- **HIGH** Cross-tenant data exposure through a query, job, search or storage path → Postgres row-level security + tenant-scoped repository, per-tenant storage prefixes, isolation tests on every data path (ADR-002)
- **HIGH** Hallucinated or wrong insights erode manager trust → Evidence quotes with timestamps, confidence thresholds, human review queue, eval gating (ADR-007, ADR-008)
- **HIGH** Transcription and LLM costs per audio hour erode margin → Per-org audio allowance, metering, cost alerts, model selection by eval and cost

**Untested assumptions (labelled, not facts):**
- A-001 (confidence 60): Sales managers at 10–100 rep teams will act on a weekly coaching queue
- A-002 (confidence 55): Managed speech-to-text diarization is accurate enough to attribute objections to prospects
- A-003 (confidence 60): LLM extraction can reach objection precision ≥ 0.85 and recall ≥ 0.80

<!--
Speaker notes: Top risks with mitigations; what would make us stop (kill criteria).
-->
