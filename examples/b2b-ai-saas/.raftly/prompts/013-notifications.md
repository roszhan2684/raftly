# Prompt 013 — Notifications

> Build-graph node: **N013** · Features: F010
> Self-contained implementation prompt. Paste into Claude Code, or run `/raftly build next`.

## Role to activate
Staff Backend Engineer

## Files to read first
- `.raftly/state.yaml`
- `.raftly/ARCHITECTURE.md` (module boundaries)
- `.raftly/features/F010-notifications.md`
- `.raftly/dependencies.yaml` (email provider PROPOSED)

## Objective
Weekly manager digests and rep share notifications that build the coaching habit.

## Scope
Choose and adopt the transactional email provider (licence/terms, deliverability, cost), authenticate the sending domain, the digest job, share notifications, preferences and unsubscribe, and bounce handling.

## Dependencies
N008 VERIFIED or COMPLETE.

## Architecture / design constraints
- Minimal personal data in emails (org setting controls quotes).
- Timezone-aware scheduling.

## Implementation tasks
1. Record the provider decision (RECOMMEND ADR) and update dependencies.yaml.
2. SPF, DKIM and DMARC for the sending domain; verify.
3. Digest builder + weekly job; share notification.
4. Preferences API/UI and one-click unsubscribe.
5. Bounce/complaint webhook → suppression.

## Explicitly out of scope
- Slack notifications

## Edge cases
- No new insights (skip)
- Bounced addresses
- Multi-org users

## Security / accessibility requirements
- G-EMAIL-DOMAIN and G-F20-EMAIL-AUTH evidence
- Plain-text alternatives

## Tests required
- Digest builder unit tests
- Preference enforcement
- Bounce handling

## Verification steps
- Record DNS verification evidence

## After implementation (state and evidence updates)
1. Run relevant tests/checks; keep the exact commands and outputs.
2. Compare the implementation with the feature acceptance criteria.
3. Record evidence: `raftly evidence record --subject F010 --kind test --result PASS|FAIL --summary "..." --command "..."`; register entities (`API-*`, `TBL-*`, `TEST-*`) and link them (`raftly evidence link`).
4. Update status: `raftly graph set-status N013 IMPLEMENTED_UNVERIFIED`, then `VERIFIED` only with passing verification evidence.
5. Record any deviation as an ADR, debt item or risk.
6. Do not mark COMPLETE unless verification passed and the Definition of Done is checked.

## Escalate instead of changing autonomously
- Any change to Type-1 decisions: ADR-001 (modular monolith), ADR-002 (Postgres + RLS tenancy), ADR-003 (auth), ADR-006/ADR-007 (AI providers).
- New third-party services or dependencies not in `dependencies.yaml`.
- Anything that weakens tenant isolation, consent handling or retention.
