---
id: F006
name: Offline and distribution
status: PLANNED
priority: MUST
owner_role: mobile
node: N006
requirements:
  - REQ-004
decisions:
  - ADR-001
  - ADR-004
  - ADR-008
depends_on:
  - F002
screens: []
evidence_status: NONE
updated_at: 2026-10-24
---
# F006 — Offline and distribution

## Product goal
Tally works anywhere without a connection and reaches users on the App Store, Google Play and the web (REQ-004).

## User story / jobs
As a user on a plane or a bad connection, I want the calculator to just work, so I never depend on a network.

## Actors
End user; the release engineer (platform role).

## Entry conditions
The app is installed (native) or the site has been loaded once (web).

## Main flow
1. Native: all code and assets are bundled; no network calls at runtime.
2. Web: a static export served with a service worker that precaches the app shell and assets; offline loads work after the first visit.
3. Releases: signed iOS/Android builds through Expo's build tooling; the web is deployed to a static host with immutable asset hashes.

## Alternative flows
Service worker update available → the new version activates on the next launch (no forced reload mid-calculation).

## State model
Not applicable.

## Data model implications
None.

## API / contracts
Not applicable: no network API exists.

## Permissions
None requested at runtime (haptics need no permission).

## UI / screens
None new. A store listing and the website `<head>` metadata (SEO, G-SEO) are part of this feature.

## Edge cases
- First visit offline (web): the browser's offline page (cannot be avoided); documented.
- Stale service-worker cache: versioned cache names; old caches are cleaned on activate.

## Error behavior
None at runtime (no network dependency).

## Empty / loading states
Web first load shows the app shell immediately (static HTML).

## Analytics / metrics
None (ADR-008).

## Security / privacy requirements
CSP and security headers on the web host (G-SEC-HEADERS); no third-party scripts; store privacy labels "Data Not Collected"; privacy policy page stating that no data is collected (requires review, G-LEGAL-DOCS).

## Accessibility requirements
Store listing text and screenshots describe accessibility support accurately.

## Observability
Platform store vitals (crash rates provided by the stores) are reviewed manually; no SDK (ADR-008).

## Dependencies
F002; Expo build tooling; a static host (choice deferred: any host serving static files with custom headers).

## Out of scope
Over-the-air update channels beyond store policy; desktop app stores.

## Tests
- Web: Lighthouse PWA/offline audit; manual airplane-mode test after the first load
- Native: airplane-mode test on iOS and Android devices
- Release: rollback rehearsal (redeploy the previous web build; halt a phased store release)

## Acceptance criteria
- [ ] Web works offline after one visit (Chrome, Safari, Firefox)
- [ ] Native apps make zero network requests at runtime (proxy check)
- [ ] Signed builds produced for both stores; the web deploy is reproducible from CI
- [ ] Rollback rehearsed once and recorded as evidence

## Definition of Done
Mark `[x]` when done with evidence, `[~]` when not applicable (say why).
- [ ] Requirements satisfied
- [ ] UI implemented
- [ ] Logic/persistence implemented
- [~] Authorization enforced server-side: N/A, client-only app (ADR-001)
- [ ] Validation present
- [ ] Loading / empty / error states
- [ ] Accessibility checked
- [ ] Responsive behavior checked
- [ ] Tests written and passing
- [~] Observability (logs/metrics): N/A, no telemetry by decision (ADR-008); errors are shown to the user
- [ ] Security/privacy review
- [ ] Docs updated

## Evidence status
None yet. Evidence lives in `evidence.yaml` (`raftly evidence for F006`).
