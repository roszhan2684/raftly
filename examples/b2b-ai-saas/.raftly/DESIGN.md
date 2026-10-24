# Design Document — SalesLens

## Experience principles
- **Action over analytics**: the first screen asks a manager to act, not to interpret charts.
- **Evidence everywhere**: every insight shows the quote, the timestamp and a play button.
- **Respect the rep**: coaching is shared deliberately, never automatically broadcast.
- **Calm density**: a pro tool for weekly use. Dense lists, clear hierarchy, keyboard-first triage.

## Primary user, job and context
Frontline sales manager on a laptop, weekly (Monday 1:1 prep, 15–30 minutes), plus quick checks during the week.
Reps check their feed on laptop or phone (responsive web).

## Information architecture
Entities: Organization › Teams › Reps › Calls › Transcript › Insights › Coaching notes.
Top-level navigation: **Queue** (managers' home) · **Calls** · **Trends** · **Settings** (Admins). Reps: **My coaching** · **My calls**.

## Navigation
Left sidebar on desktop, bottom bar on narrow screens; the org switcher in the sidebar header; a global search for calls (V1.1).

## Key flows
1. Manager triage: Queue → item → listen to the snippet → accept/edit/dismiss → add note → share.
2. Ingest: Upload → attest consent → progress → "Transcribing…" → ready notification.
3. Rep learning: notification/email → My coaching → note with quote + audio → reply/mark read.
4. Leader insight: Trends → spike in "pricing objection" → drill into evidence.

## Design direction options

### Option A — Coaching queue (recommended)
An inbox-style queue of insights grouped by rep, with filters (type, team) and keyboard triage; detail panel on the right.
```text
| Queue ▾ team: West  type: all        | [quote + 30s audio]          |
| ● Dana  · objection: pricing  0.92   | "Honestly the price is..."   |
| ● Dana  · competitor: Acme    0.97   | context transcript ...        |
| ● Lee   · coaching: no next step     | [accept] [edit] [dismiss]     |
|                                      | note: ______  [share with rep]|
```
Strengths: maps to the core job; generates quality signals (accept/dismiss). Weaknesses: less overview on landing.

### Option B — Call-centric library
A call list → call page with transcript, timeline markers and an insights panel.
Strengths: familiar from recording tools. Weaknesses: managers still pick calls to review, which is the work we're removing.

### Option C — Team dashboard first
KPIs and trends on landing; drill into calls.
Strengths: leader-friendly. Weaknesses: indirect path to action; risks becoming shelfware.

## Chosen direction
**A as the manager home, B as the call detail view, C as the Trends tab** (ADR-009, confidence 70). Validated by EXP-001.

## Key screens

### SCR-queue — Coaching queue (manager home)
- Purpose: triage new insights. Primary action: accept/share. Secondary: dismiss, edit category, open the call.
- Data: rep, insight type/category, confidence, call date, quote preview; the detail panel shows quote, audio snippet, context.
- States: default · empty ("You're all caught up") · loading (skeleton rows) · error (retry; cached list kept) · success (toast "Shared with Dana").
- Permissions: Manager (own teams), Admin (all).
- Desktop: two-pane. Tablet: list → detail push. Mobile: list → full-screen detail.
- Keyboard: j/k move, Enter open, a accept, d dismiss, e edit, s share, ? help.
- Accessibility: listbox semantics with an active descendant; audio player with labelled controls; confidence as text.
- Analytics: `insight_actioned{action}` (no content).

### SCR-call-detail — Call
- Purpose: full context. Data: metadata, audio player, transcript with speaker labels, timeline markers, insights list.
- States: processing (step + estimate) · failed (reason + retry) · ready · insights unavailable (retry).
- Permissions: per visibility rules. Responsive: transcript below the player on mobile.
- Accessibility: transcript as a list of labelled segments; click-to-seek via buttons.

### SCR-upload — Upload
Drag-and-drop + file picker, consent attestation (org policy text), resumable progress, limits explained. Errors explain the format/duration limits.

### SCR-rep-feed — My coaching
Shared notes as cards (manager, quote, audio, note, reply). Empty: "No coaching yet…". Read status.

### SCR-trends — Trends
Period/team filters, objection categories over time (line), competitor share (bar), per-rep table; every chart has a table alternative and a summary sentence; small-sample warnings.

### SCR-org-settings / SCR-audit-log / SCR-integrations / SCR-billing / SCR-signin / SCR-notification-settings
Standard settings patterns; destructive actions require typed confirmation; every list has empty/loading/error states.

## Responsive behaviour
≥ 1100 px two-pane; 700–1099 px single pane with push navigation; < 700 px mobile layout for reps' feed and quick manager triage.

## States
Processing states are explicit (uploading → transcribing → analyzing → ready) with honest time estimates; AI failures say "Insights unavailable" rather than showing nothing.

## Accessibility
WCAG 2.2 AA target; keyboard-first triage; colour never the only signal (confidence and status in text); captions/transcript for all audio.

## OSS component choices
| Need | Choice | Licence | Why / rejected alternatives |
|---|---|---|---|
| Accessible primitives (dialogs, menus, listbox) | Headless accessible primitives library (evaluate React Aria vs Radix at N008) | Apache-2.0 / MIT (verify) | building accessible listbox/dialog correctly is non-trivial |
| Tables (members, per-rep) | Native table + small internal helpers | — | data volumes are small; a table library is not justified in V1 |
| Charts (trends) | Evaluate a lightweight chart library vs internal SVG at N010 | verify | two chart types only |
| Audio player | Native `<audio>` with custom accessible controls | — | sufficient |
