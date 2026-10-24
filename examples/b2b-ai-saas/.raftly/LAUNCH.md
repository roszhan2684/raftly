# Launch Readiness — SalesLens

## Launch plan
1. Design-partner pilot (EXP-001): 5 teams, 4 weeks, free, with signed pilot terms and DPA.
2. Decide on EXP-001 (proceed / reposition).
3. Paid launch to the waitlist; public launch after 4 weeks of stable SLOs.

## Rollback
Application: redeploy the previous web/worker release (one CI action); feature flags for extraction prompt versions.
Database: expand/contract migrations; restore from PITR only for data-corruption incidents (drill recorded in N014).

## Owners and support
Founder/eng lead on-call for alerts during the pilot; support inbox and in-app help link (G-SUPPORT).

## Production gate
<!-- generated:gate:start -->
**Production gate: INSUFFICIENT_EVIDENCE**

- Evidence coverage: 0% of applicable weight · Score: UNVERIFIED (insufficient evidence)
- Counts: NOT_APPLICABLE 3, UNVERIFIED 42
- Blockers without evidence: G-PRODUCT-SCOPE, G-PRODUCT-FLOWS, G-AUTH, G-AUTHZ-SERVER, G-TENANT-ISOLATION, G-BACKUPS, G-SEC-SECRETS, G-SEC-INPUT, G-SEC-UPLOADS, G-SEC-WEBHOOKS, G-PRIV-SENSITIVE, G-COMPLIANCE-READINESS, G-TEST-AUTOMATED, G-ROLLBACK, G-BILLING, G-AI-EVALS

| Check | Category | Severity | Status | Evidence / note |
|---|---|---|---|---|
| G-A11Y — Accessibility checks (WCAG 2.2 AA target) on key flows | accessibility | major | UNVERIFIED |  |
| G-AI-COST — Inference cost budget, per-tenant limits and cost alerts | ai | major | UNVERIFIED |  |
| G-AI-EVALS — AI eval suite meets agreed thresholds on a versioned dataset | ai | blocker | UNVERIFIED |  |
| G-AI-FALLBACK — Fallback/degradation defined for model errors, timeouts and low confidence | ai | major | UNVERIFIED |  |
| G-ALERTS — Alerts on SLO/critical failures routed to an owner | alerts | major | UNVERIFIED |  |
| G-ANALYTICS — Analytics events verified; consent where required; internal traffic filtered | analytics | minor | UNVERIFIED |  |
| G-AUTH — Authentication implemented with secure session handling | auth | blocker | UNVERIFIED |  |
| G-AUTHZ-SERVER — Authorization enforced server-side on every protected operation | authorization | blocker | UNVERIFIED |  |
| G-BACKUPS — Automated backups configured for all persistent stores | backups | blocker | UNVERIFIED |  |
| G-BILLING — Billing lifecycle verified incl. failed payments, refunds, cancellation | billing | blocker | UNVERIFIED |  |
| G-COMPLIANCE-READINESS — Compliance readiness checklist complete and reviewed by a qualified professional | compliance | blocker | UNVERIFIED |  |
| G-DATA-EXPORT-DELETE — User data export and deletion paths work | privacy | major | UNVERIFIED |  |
| G-DATA-MIGRATIONS — Schema migrations versioned, tested, with rollback or compensation plan | data-migrations | major | UNVERIFIED |  |
| G-EMAIL-DOMAIN — Sending domain authenticated (SPF, DKIM, DMARC) | email | major | UNVERIFIED |  |
| G-ENV-PARITY — Staging environment with configuration parity | environments | minor | UNVERIFIED |  |
| G-HEALTH — Health checks and readiness probes | monitoring | major | UNVERIFIED |  |
| G-INCIDENT — Incident response path: owner, contact, runbook | incident-response | major | UNVERIFIED |  |
| G-LEGAL-DOCS — Privacy policy / terms published (requires professional review) | legal | major | UNVERIFIED |  |
| G-LOGS — Structured logs with correlation ids; no secrets in logs | logs | major | UNVERIFIED |  |
| G-MONITORING — Error tracking and service monitoring in production | monitoring | major | UNVERIFIED |  |
| G-PERF — Performance budget defined and met | performance | major | UNVERIFIED |  |
| G-PRIV-INVENTORY — Personal-data inventory, purpose and retention documented | privacy | major | UNVERIFIED |  |
| G-PRIV-LOGGING — Sensitive/personal data excluded or redacted from logs and analytics | privacy | major | UNVERIFIED |  |
| G-PRIV-SENSITIVE — Sensitive data classes have access control, encryption and audit trail | privacy | blocker | UNVERIFIED |  |
| G-PRODUCT-FLOWS — Core user flows verified end-to-end | product | blocker | UNVERIFIED |  |
| G-PRODUCT-SCOPE — All MUST requirements are implemented and verified | product | blocker | UNVERIFIED |  |
| G-RESTORE — Restore from backup verified at least once | restore | major | UNVERIFIED |  |
| G-ROLLBACK — Rollback path defined and rehearsed (previous build / deploy revert / store release) | rollback | blocker | UNVERIFIED |  |
| G-SEC-AI — Prompt-injection, data-leakage and output-handling controls in place | security | major | UNVERIFIED |  |
| G-SEC-DEPS — Dependency audit shows no known critical/high vulnerabilities without mitigation | security | major | UNVERIFIED |  |
| G-SEC-HEADERS — Security headers and CSP configured for the web surface | security | major | UNVERIFIED |  |
| G-SEC-INPUT — Input validated at every trust boundary; injection risks addressed | security | blocker | UNVERIFIED |  |
| G-SEC-RATE — Rate limiting on authentication and expensive endpoints | rate-limits | major | UNVERIFIED |  |
| G-SEC-SECRETS — No secrets in source control; secrets managed per environment | security | blocker | UNVERIFIED |  |
| G-SEC-THREAT-MODEL — Threat model reviewed against the implemented system | security | major | UNVERIFIED |  |
| G-SEC-UPLOADS — File uploads restricted (type, size, scanning, storage isolation) | security | blocker | UNVERIFIED |  |
| G-SEC-WEBHOOKS — Inbound webhooks verified (signature) and processed idempotently | security | blocker | UNVERIFIED |  |
| G-SEO — Public site metadata, sitemap, robots and performance | seo | minor | UNVERIFIED |  |
| G-SUPPORT — Support/contact path visible to users | support | minor | UNVERIFIED |  |
| G-TENANT-ISOLATION — Tenant isolation verified by tests (cross-tenant access denied) | tenant-isolation | blocker | UNVERIFIED |  |
| G-TEST-AUTOMATED — Automated test suite passes in CI | testing | blocker | UNVERIFIED |  |
| G-TEST-REGRESSION — Regression coverage on critical paths | testing | major | UNVERIFIED |  |
| G-CLIENT-ERRORS — Client crash/error visibility decided (tooling or explicit privacy-preserving opt-out) | monitoring | minor | N/A | profile does not match: ui and not backend |
| G-STORE — App store listing, privacy labels and review requirements satisfied | distribution | major | N/A | profile does not match: surface:ios or surface:android or surface:mobile |
| G-TEST-PLATFORMS — Platform/device matrix verified | testing | major | N/A | profile does not match: surface:ios or surface:android or surface:mobile or surface:desktop |

Scores are derived from gate statuses (weights: blocker 3, major 2, minor 1; PASS 1, WARNING 0.5, FAIL 0; UNVERIFIED and N/A excluded). No evidence means no PASS.
<!-- generated:gate:end -->

## Forgotten 20% audit
<!-- generated:forgotten20:start -->
**Forgotten 20% audit**

- Evidence coverage: 0% of applicable weight · Score: UNVERIFIED (insufficient evidence)
- Counts: NOT_APPLICABLE 1, UNVERIFIED 28

| Check | Category | Severity | Status | Evidence / note |
|---|---|---|---|---|
| G-F20-404-500 — Custom 404/500 pages | ui | minor | UNVERIFIED |  |
| G-F20-A11Y — Keyboard, screen reader, contrast, reduced motion | accessibility | major | UNVERIFIED |  |
| G-F20-ACCOUNT-DELETION — Account and organization deletion | accounts | major | UNVERIFIED |  |
| G-F20-ANALYTICS-FILTER — Analytics excludes internal/test traffic | analytics | minor | UNVERIFIED |  |
| G-F20-AUDIT-LOG — Audit log for admin and sensitive actions | security | major | UNVERIFIED |  |
| G-F20-CSP — CSP and security headers | security | minor | UNVERIFIED |  |
| G-F20-DATA-EXPORT — User data export | privacy | major | UNVERIFIED |  |
| G-F20-EMAIL-AUTH — Email authentication (SPF/DKIM/DMARC) | email | major | UNVERIFIED |  |
| G-F20-EMPTY — Empty states that explain the next action | ui-states | minor | UNVERIFIED |  |
| G-F20-ERRORS — Error states with recovery path | ui-states | major | UNVERIFIED |  |
| G-F20-FAILED-PAYMENTS — Failed payments / dunning | billing | major | UNVERIFIED |  |
| G-F20-HEALTH — Health check endpoint | ops | minor | UNVERIFIED |  |
| G-F20-LEGAL-PAGES — Privacy/legal pages linked in product | legal | major | UNVERIFIED |  |
| G-F20-LOADING — Loading states on every async view | ui-states | minor | UNVERIFIED |  |
| G-F20-META-ICONS — Favicons, app icons, social preview images | brand | minor | UNVERIFIED |  |
| G-F20-MIGRATIONS — Migrations rehearsed on production-like data | data | major | UNVERIFIED |  |
| G-F20-PASSWORD-RESET — Password reset / account recovery | accounts | major | UNVERIFIED |  |
| G-F20-RATE-LIMIT — Rate limiting | security | minor | UNVERIFIED |  |
| G-F20-RESPONSIVE — Responsive behaviour at phone/tablet/desktop widths | ui | minor | UNVERIFIED |  |
| G-F20-RESTORE-DRILL — Backup restore drill | data | major | UNVERIFIED |  |
| G-F20-RETRIES — Retries with backoff for external calls | reliability | minor | UNVERIFIED |  |
| G-F20-SECRETS — Secrets inventory and rotation path | security | major | UNVERIFIED |  |
| G-F20-STAGING — Staging environment | ops | minor | UNVERIFIED |  |
| G-F20-SUPPORT — Support contact | support | minor | UNVERIFIED |  |
| G-F20-TIME — UTC storage and timezone-correct display | data | minor | UNVERIFIED |  |
| G-F20-TRIAL-EXPIRY — Trial expiry behaviour | billing | major | UNVERIFIED |  |
| G-F20-VERIFICATION — Email/identity verification | accounts | major | UNVERIFIED |  |
| G-F20-WEBHOOK-IDEMPOTENCY — Webhook idempotency and replay protection | integrations | major | UNVERIFIED |  |
| G-F20-OFFLINE — Offline / poor-network behaviour | mobile | minor | N/A | profile does not match: surface:ios or surface:android or surface:mobile |

Scores are derived from gate statuses (weights: blocker 3, major 2, minor 1; PASS 1, WARNING 0.5, FAIL 0; UNVERIFIED and N/A excluded). No evidence means no PASS.
<!-- generated:forgotten20:end -->

## Remaining risks
R-001 (legal review pending), R-004 (cost unknown until spikes), R-007 (market).

## Next phase
V1.1 candidates: CRM deal linking (REQ-015), Google Meet/Teams import, Slack notifications, talk-ratio analytics, SAML SSO.
