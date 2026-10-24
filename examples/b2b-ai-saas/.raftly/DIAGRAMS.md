# Product Diagrams — SalesLens

These diagrams render as pictures on GitHub and in most Markdown viewers that support Mermaid. Each one is
drawn from a recorded decision; nothing here goes beyond ARCHITECTURE.md, DESIGN.md, DATA_MODEL.md and the ADRs.
The transcription provider and the email provider are not chosen yet and are labelled that way.

## 1. System architecture
A TypeScript modular monolith (ADR-001): a `web` process and a `worker` process share the domain modules.
PostgreSQL with row-level security holds all relational data and the job queue (ADR-002, ADR-005). Audio
lives in object storage under per-tenant prefixes (ADR-004). AI calls go through provider interfaces
(ADR-006, ADR-007) and are gated by the eval harness (ADR-008). Zoom is the only integration (ADR-011).
Everything runs in one cloud region; dashed boxes are third parties, outside our trust boundary.

```mermaid
flowchart LR
  browser(["Browser: admins, managers, reps"])
  web["web: Next.js UI + API routes"]
  worker["worker: pg-boss consumers"]
  db[("PostgreSQL: RLS tenancy + job queue")]
  obj[("Object storage: org/{id}/...")]
  zoom["Zoom API + webhooks"]:::ext
  stripe["Stripe Billing"]:::ext
  stt["Speech-to-text: provider undecided"]:::ext
  llm["LLM API: Anthropic"]:::ext
  mail["Email: provider undecided"]:::ext
  browser -->|HTTPS| web
  browser -->|presigned upload| obj
  web -->|"reads, writes, enqueues"| db
  db -->|jobs| worker
  worker -->|reads audio| obj
  worker -->|import recordings| zoom
  worker -->|TranscriptionProvider| stt
  worker -->|ExtractionProvider| llm
  worker -->|report usage| stripe
  worker -->|digests| mail
  zoom -. verified webhooks .-> web
  stripe -. verified webhooks .-> web
  classDef ext stroke-dasharray: 5 5
```

## 2. User flow
The manager triage flow from DESIGN.md, from a call arriving to a rep reading shared coaching, including
the processing-failure branch.

```mermaid
flowchart TD
  start([Call arrives]) --> src{"Source"}
  src -->|upload| consent["Attest recording consent"]
  src -->|Zoom import| consent
  consent --> process["Transcribe, then extract insights"]
  process -->|ready| queue["Manager's coaching queue"]
  process -->|failed| failed["Call shows reason + retry"]
  failed --> process
  queue --> review{"Review insight with quote + audio"}
  review -->|dismiss with reason| queue
  review -->|accept or edit| note["Add coaching note"]
  note --> share["Share with the rep"]
  share --> rep["Rep sees it in My coaching"]
  rep --> reply([Rep replies or marks read])
```

## 3. Screen map and navigation
Direction A, coaching queue first (ADR-009). Managers land on the queue; reps land on My coaching;
settings screens are admin-only.

```mermaid
flowchart LR
  signin["Sign in"] --> role{"Role"}
  role -->|manager| queue["Coaching queue (home)"]
  role -->|rep| feed["My coaching"]
  role -->|admin| queue
  queue --> callDetail["Call detail: audio, transcript, insights"]
  calls["Calls list"] --> callDetail
  queue --> calls
  calls --> upload["Upload + consent"]
  queue --> trends["Trends"]
  trends -->|drill into evidence| callDetail
  feed --> mycalls["My calls"] --> callDetail
  queue --> settings["Settings (admin)"]
  settings --> integrations["Integrations: Zoom"]
  settings --> billing["Billing"]
  settings --> audit["Audit log"]
  settings --> org["Org settings: retention, consent"]
```

## 4. Data model
Shared schema with `org_id` on every tenant table and RLS policies (ADR-002, DATA_MODEL.md). Billing and
governance tables are summarised.

```mermaid
erDiagram
  ORGS ||--o{ MEMBERSHIPS : has
  ORGS ||--o{ TEAMS : has
  TEAMS ||--o{ TEAM_MEMBERS : has
  ORGS ||--o{ CALLS : owns
  CALLS ||--o| TRANSCRIPTS : has
  TRANSCRIPTS ||--o{ TRANSCRIPT_SEGMENTS : has
  CALLS ||--o{ INSIGHTS : yields
  INSIGHTS ||--o{ INSIGHT_REVIEWS : reviewed_by
  INSIGHTS ||--o{ COACHING_NOTES : shared_as
  CALLS }o--|| CONSENT_ATTESTATIONS : requires
  ORGS ||--o{ USAGE_EVENTS : meters
  ORGS ||--o{ AUDIT_EVENTS : logs
  ORGS {
    uuid id PK
    text name
    int retention_audio_days
    enum status
  }
  CALLS {
    uuid id PK
    uuid org_id FK
    uuid rep_user_id FK
    enum source
    text storage_key
    text content_hash
    enum status
    uuid consent_attestation_id FK
  }
  INSIGHTS {
    uuid id PK
    uuid org_id FK
    uuid call_id FK
    text type
    text quote
    float confidence
    text prompt_version
  }
  COACHING_NOTES {
    uuid id PK
    uuid org_id FK
    uuid insight_id FK
    uuid author_id FK
    timestamp shared_at
    timestamp read_at
  }
```

## 5. Critical path sequence
Upload to insights: the path every customer depends on. Retries with backoff and a dead-letter queue for
the speech provider; invalid AI output is discarded, not shown (ARCHITECTURE.md failure behaviour).

```mermaid
sequenceDiagram
  actor M as Manager
  participant W as web
  participant S as Object storage
  participant DB as PostgreSQL
  participant K as worker
  participant T as Speech-to-text
  participant L as LLM
  M->>W: start upload + attest consent
  W->>DB: save call, attestation (org_id, RLS)
  W-->>M: presigned upload URL
  M->>S: upload audio (resumable)
  W->>DB: enqueue transcribe job
  K->>DB: claim job
  K->>T: transcribe(audio)
  alt provider down or timeout
    T-->>K: error
    K->>DB: retry with backoff, dead-letter after 3
    W-->>M: Transcribing... delayed
  else transcript ready
    T-->>K: segments
    K->>L: extract insights (structured output)
    alt invalid output
      L-->>K: fails schema
      K->>K: discard, retry, then fallback model
    else valid
      L-->>K: insights with quotes + timestamps
      K->>DB: save insights, usage event
      W-->>M: queue updated, ready notification
    end
  end
```
