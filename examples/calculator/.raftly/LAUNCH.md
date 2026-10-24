# Launch Readiness — Tally

## Launch plan
1. Closed beta (TestFlight / Play internal testing / unlisted web URL) with 20 users for 2 weeks (EXP-001).
2. Decide on EXP-001: proceed, or stop investing beyond V1 (kill criteria).
3. Public release: web first (instant rollback), then the stores with phased release.

## Rollback
- Web: redeploy the previous static build (one CI job); service worker updates on the next launch.
- Stores: halt the phased release; ship a fix build. Rehearsed in N006 (G-ROLLBACK).

## Owners and support
Founder/maintainer owns releases and the support inbox; the support contact is shown in the app's About sheet and in the store listings (G-SUPPORT).

## Production gate
<!-- generated:gate:start -->
**Production gate: INSUFFICIENT_EVIDENCE**

- Evidence coverage: 0% of applicable weight · Score: UNVERIFIED (insufficient evidence)
- Counts: NOT_APPLICABLE 29, UNVERIFIED 16
- Blockers without evidence: G-PRODUCT-SCOPE, G-PRODUCT-FLOWS, G-SEC-SECRETS, G-TEST-AUTOMATED, G-ROLLBACK

| Check | Category | Severity | Status | Evidence / note |
|---|---|---|---|---|
| G-A11Y — Accessibility checks (WCAG 2.2 AA target) on key flows | accessibility | major | UNVERIFIED |  |
| G-CLIENT-ERRORS — Client crash/error visibility decided (tooling or explicit privacy-preserving opt-out) | monitoring | minor | UNVERIFIED |  |
| G-LEGAL-DOCS — Privacy policy / terms published (requires professional review) | legal | major | UNVERIFIED |  |
| G-PERF — Performance budget defined and met | performance | major | UNVERIFIED |  |
| G-PRODUCT-FLOWS — Core user flows verified end-to-end | product | blocker | UNVERIFIED |  |
| G-PRODUCT-SCOPE — All MUST requirements are implemented and verified | product | blocker | UNVERIFIED |  |
| G-ROLLBACK — Rollback path defined and rehearsed (previous build / deploy revert / store release) | rollback | blocker | UNVERIFIED |  |
| G-SEC-DEPS — Dependency audit shows no known critical/high vulnerabilities without mitigation | security | major | UNVERIFIED |  |
| G-SEC-HEADERS — Security headers and CSP configured for the web surface | security | major | UNVERIFIED |  |
| G-SEC-SECRETS — No secrets in source control; secrets managed per environment | security | blocker | UNVERIFIED |  |
| G-SEO — Public site metadata, sitemap, robots and performance | seo | minor | UNVERIFIED |  |
| G-STORE — App store listing, privacy labels and review requirements satisfied | distribution | major | UNVERIFIED |  |
| G-SUPPORT — Support/contact path visible to users | support | minor | UNVERIFIED |  |
| G-TEST-AUTOMATED — Automated test suite passes in CI | testing | blocker | UNVERIFIED |  |
| G-TEST-PLATFORMS — Platform/device matrix verified | testing | major | UNVERIFIED |  |
| G-TEST-REGRESSION — Regression coverage on critical paths | testing | major | UNVERIFIED |  |
| G-AI-COST — Inference cost budget, per-tenant limits and cost alerts | ai | major | N/A | profile does not match: ai |
| G-AI-EVALS — AI eval suite meets agreed thresholds on a versioned dataset | ai | blocker | N/A | profile does not match: ai |
| G-AI-FALLBACK — Fallback/degradation defined for model errors, timeouts and low confidence | ai | major | N/A | profile does not match: ai |
| G-ALERTS — Alerts on SLO/critical failures routed to an owner | alerts | major | N/A | profile does not match: backend |
| G-ANALYTICS — Analytics events verified; consent where required; internal traffic filtered | analytics | minor | N/A | profile does not match: analytics |
| G-AUTH — Authentication implemented with secure session handling | auth | blocker | N/A | profile does not match: accounts |
| G-AUTHZ-SERVER — Authorization enforced server-side on every protected operation | authorization | blocker | N/A | profile does not match: backend and accounts |
| G-BACKUPS — Automated backups configured for all persistent stores | backups | blocker | N/A | profile does not match: backend |
| G-BILLING — Billing lifecycle verified incl. failed payments, refunds, cancellation | billing | blocker | N/A | profile does not match: payments |
| G-COMPLIANCE-READINESS — Compliance readiness checklist complete and reviewed by a qualified professional | compliance | blocker | N/A | profile does not match: regulated:any or sensitive:phi or sensitive:payment_card |
| G-DATA-EXPORT-DELETE — User data export and deletion paths work | privacy | major | N/A | profile does not match: personal_data |
| G-DATA-MIGRATIONS — Schema migrations versioned, tested, with rollback or compensation plan | data-migrations | major | N/A | profile does not match: backend |
| G-EMAIL-DOMAIN — Sending domain authenticated (SPF, DKIM, DMARC) | email | major | N/A | profile does not match: email |
| G-ENV-PARITY — Staging environment with configuration parity | environments | minor | N/A | profile does not match: backend |
| G-HEALTH — Health checks and readiness probes | monitoring | major | N/A | profile does not match: backend |
| G-INCIDENT — Incident response path: owner, contact, runbook | incident-response | major | N/A | profile does not match: backend |
| G-LOGS — Structured logs with correlation ids; no secrets in logs | logs | major | N/A | profile does not match: backend |
| G-MONITORING — Error tracking and service monitoring in production | monitoring | major | N/A | profile does not match: backend |
| G-PRIV-INVENTORY — Personal-data inventory, purpose and retention documented | privacy | major | N/A | profile does not match: personal_data |
| G-PRIV-LOGGING — Sensitive/personal data excluded or redacted from logs and analytics | privacy | major | N/A | profile does not match: personal_data |
| G-PRIV-SENSITIVE — Sensitive data classes have access control, encryption and audit trail | privacy | blocker | N/A | profile does not match: sensitive:any |
| G-RESTORE — Restore from backup verified at least once | restore | major | N/A | profile does not match: backend |
| G-SEC-AI — Prompt-injection, data-leakage and output-handling controls in place | security | major | N/A | profile does not match: ai |
| G-SEC-INPUT — Input validated at every trust boundary; injection risks addressed | security | blocker | N/A | profile does not match: backend |
| G-SEC-RATE — Rate limiting on authentication and expensive endpoints | rate-limits | major | N/A | profile does not match: backend |
| G-SEC-THREAT-MODEL — Threat model reviewed against the implemented system | security | major | N/A | profile does not match: backend |
| G-SEC-UPLOADS — File uploads restricted (type, size, scanning, storage isolation) | security | blocker | N/A | profile does not match: file_uploads |
| G-SEC-WEBHOOKS — Inbound webhooks verified (signature) and processed idempotently | security | blocker | N/A | profile does not match: payments or integrations |
| G-TENANT-ISOLATION — Tenant isolation verified by tests (cross-tenant access denied) | tenant-isolation | blocker | N/A | profile does not match: multi_tenant |

Scores are derived from gate statuses (weights: blocker 3, major 2, minor 1; PASS 1, WARNING 0.5, FAIL 0; UNVERIFIED and N/A excluded). No evidence means no PASS.
<!-- generated:gate:end -->

## Forgotten 20% audit
<!-- generated:forgotten20:start -->
**Forgotten 20% audit**

- Evidence coverage: 0% of applicable weight · Score: UNVERIFIED (insufficient evidence)
- Counts: NOT_APPLICABLE 17, UNVERIFIED 12

| Check | Category | Severity | Status | Evidence / note |
|---|---|---|---|---|
| G-F20-404-500 — Custom 404/500 pages | ui | minor | UNVERIFIED |  |
| G-F20-A11Y — Keyboard, screen reader, contrast, reduced motion | accessibility | major | UNVERIFIED |  |
| G-F20-CSP — CSP and security headers | security | minor | UNVERIFIED |  |
| G-F20-EMPTY — Empty states that explain the next action | ui-states | minor | UNVERIFIED |  |
| G-F20-ERRORS — Error states with recovery path | ui-states | major | UNVERIFIED |  |
| G-F20-LEGAL-PAGES — Privacy/legal pages linked in product | legal | major | UNVERIFIED |  |
| G-F20-LOADING — Loading states on every async view | ui-states | minor | UNVERIFIED |  |
| G-F20-META-ICONS — Favicons, app icons, social preview images | brand | minor | UNVERIFIED |  |
| G-F20-OFFLINE — Offline / poor-network behaviour | mobile | minor | UNVERIFIED |  |
| G-F20-RESPONSIVE — Responsive behaviour at phone/tablet/desktop widths | ui | minor | UNVERIFIED |  |
| G-F20-SECRETS — Secrets inventory and rotation path | security | major | UNVERIFIED |  |
| G-F20-SUPPORT — Support contact | support | minor | UNVERIFIED |  |
| G-F20-ACCOUNT-DELETION — Account and organization deletion | accounts | major | N/A | profile does not match: accounts |
| G-F20-ANALYTICS-FILTER — Analytics excludes internal/test traffic | analytics | minor | N/A | profile does not match: analytics |
| G-F20-AUDIT-LOG — Audit log for admin and sensitive actions | security | major | N/A | profile does not match: multi_tenant or sensitive:any |
| G-F20-DATA-EXPORT — User data export | privacy | major | N/A | profile does not match: personal_data |
| G-F20-EMAIL-AUTH — Email authentication (SPF/DKIM/DMARC) | email | major | N/A | profile does not match: email |
| G-F20-FAILED-PAYMENTS — Failed payments / dunning | billing | major | N/A | profile does not match: payments |
| G-F20-HEALTH — Health check endpoint | ops | minor | N/A | profile does not match: backend |
| G-F20-MIGRATIONS — Migrations rehearsed on production-like data | data | major | N/A | profile does not match: backend |
| G-F20-PASSWORD-RESET — Password reset / account recovery | accounts | major | N/A | profile does not match: accounts |
| G-F20-RATE-LIMIT — Rate limiting | security | minor | N/A | profile does not match: backend |
| G-F20-RESTORE-DRILL — Backup restore drill | data | major | N/A | profile does not match: backend |
| G-F20-RETRIES — Retries with backoff for external calls | reliability | minor | N/A | profile does not match: backend or integrations |
| G-F20-STAGING — Staging environment | ops | minor | N/A | profile does not match: backend |
| G-F20-TIME — UTC storage and timezone-correct display | data | minor | N/A | profile does not match: backend |
| G-F20-TRIAL-EXPIRY — Trial expiry behaviour | billing | major | N/A | profile does not match: payments |
| G-F20-VERIFICATION — Email/identity verification | accounts | major | N/A | profile does not match: accounts |
| G-F20-WEBHOOK-IDEMPOTENCY — Webhook idempotency and replay protection | integrations | major | N/A | profile does not match: payments or integrations |

Scores are derived from gate statuses (weights: blocker 3, major 2, minor 1; PASS 1, WARNING 0.5, FAIL 0; UNVERIFIED and N/A excluded). No evidence means no PASS.
<!-- generated:forgotten20:end -->

## Remaining risks
R-003 crowded category (accepted; EXP-001 decides), R-004 store review (re-verify guidelines before submission).

## Next phase
After V1: consider a tablet/desktop workspace layout (direction C) and a scientific mode if beta and reviews ask for them.
