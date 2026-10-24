# Prompt 006 — Offline, PWA and store builds

> Build-graph node: **N006** · Features: F006

## Role to activate
Staff Platform Engineer + Staff Mobile Engineer.

## Files to read first
- `.raftly/features/F006-offline-and-distribution.md`
- `.raftly/decisions/ADR-001-*.md`, `ADR-004-*.md`, `ADR-008-*.md`
- `.raftly/SECURITY.md` (headers/CSP), `.raftly/LAUNCH.md` (rollback)

## Objective
Offline-capable static web deployment and signed store builds, with a rehearsed rollback.

## Scope
Service worker precache for the web export, web security headers/CSP on the chosen static host, SEO metadata, iOS/Android signed builds via Expo's build service, a CI release workflow, a rollback runbook.

## Dependencies
N003 VERIFIED or COMPLETE.

## Architecture / design constraints
No runtime network calls; no third-party scripts; cache names versioned. Choose a static host that supports custom headers (record a RECOMMEND ADR for the host choice).

## Implementation tasks
1. Service worker with precache of the app shell and assets; activate-on-next-launch update strategy.
2. Static host configuration: CSP (`default-src 'self'`), HSTS, X-Content-Type-Options, Referrer-Policy, Permissions-Policy.
3. `<head>` metadata: title, description, canonical, Open Graph image, sitemap.xml, robots.txt (G-SEO).
4. Store builds for iOS and Android; privacy labels "Data Not Collected"; a privacy policy page (draft, needs review).
5. CI release workflow; rollback runbook in LAUNCH.md; rehearse one rollback.

## Explicitly out of scope
Analytics, crash SDKs (ADR-008), OTA channels beyond store policy.

## Edge cases
First visit offline; stale caches; store phased release halted.

## Security / accessibility requirements
Headers verified on the deployed URL (G-SEC-HEADERS); store listing accessibility claims accurate.

## Tests required
Lighthouse offline/PWA audit; airplane-mode tests on devices; a header check; a proxy check showing zero native network requests.

## Verification steps
Record evidence for each check and link it to the gate (`raftly gate set G-SEC-HEADERS PASS --evidence EV-...`, `G-ROLLBACK`, `G-SEO`).

## After implementation (state and evidence updates)
1. Run the relevant tests/checks and keep the exact commands and outputs.
2. Compare the implementation with every acceptance criterion in the feature spec(s).
3. Record evidence: `raftly evidence record --subject F006 --kind test --result PASS|FAIL --summary "..." --command "..."` (and `--kind manual` for device checks, saying what was checked on which device).
4. Update status: `raftly graph set-status N006 IMPLEMENTED_UNVERIFIED`, then `VERIFIED` only with passing verification evidence; `raftly records feature-status F006 ...` likewise.
5. Record any deviation as an ADR, debt item or risk.
6. Do not mark COMPLETE unless verification passed and the Definition of Done is checked.

## Escalate instead of changing autonomously
- Any change to ADR-001 (client-only) or ADR-004 (Expo + React Native Web): both are Type-1.
- Any new dependency not in `dependencies.yaml`.
- Any change to calculator semantics in ADR-006 (product decision).
- Anything that weakens accessibility (REQ-005).
