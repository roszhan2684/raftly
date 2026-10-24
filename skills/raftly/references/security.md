# Security engineering

Role: **Principal Security Engineer** (`security`). Security output is **product-specific**, never a
generic checklist dump. **Never mark a product "secure."** Report evidence-backed checks and unresolved risk.

## Threat model (lightweight, per product)

1. Assets: what an attacker wants (tenant data, PHI, credentials, money, compute/AI spend).
2. Actors: anonymous internet users, authenticated users, malicious tenant admins, compromised dependencies,
   insiders.
3. Entry points: every route, webhook, upload, integration, AI input and admin action.
4. Threats by entry point (STRIDE as a prompt: spoofing, tampering, repudiation, information disclosure,
   denial of service, elevation of privilege).
5. Controls and their status; residual risk recorded as `raftly records add risk --category security ...`.

## Control areas (apply only what is relevant)

authentication (managed provider or vetted library; MFA for admins; secure sessions/cookies) ·
**server-side authorisation** on every operation · tenant isolation with tests · secrets (env/secret
manager; never in the repo or client; rotation path) · transport TLS and encryption at rest ·
input validation · file-upload restrictions (type sniffing, size limits, malware scanning where
warranted, isolated storage, signed URLs) · injection (parameterised queries, no shell interpolation) ·
SSRF (allow-list outbound fetches of user-provided URLs) · XSS (escaping, CSP) · CSRF (same-site cookies,
tokens for cookie auth) · rate limiting and abuse prevention · webhooks (signatures, replay protection,
idempotency) · dependency risk (lockfiles, audit, update cadence) · logging without secrets · admin
actions audited · audit trails for sensitive data · backups and recovery · AI prompt injection and data
leakage (ai.md).

## Client-only products

For apps with no backend (e.g. a calculator), most server controls are **NOT_APPLICABLE**. Mark them that
way with the reason. What still applies: dependency hygiene, no secrets in the bundle, CSP and security
headers for the web surface, safe handling of pasted input (no `eval` in an expression parser!), store
privacy disclosures, and supply chain (build pipeline integrity).

## Severity and the Constitution

- Blocker-severity security checks that FAIL keep the product NOT_READY. A founder may accept a risk,
  but the record stays visible (Constitution 16).
- Security findings are never downgraded because the fix is inconvenient.

## SECURITY.md must include

summary of the security posture (in readiness language) · threat model · controls table (control →
status → evidence id) · data classes and their protection · secrets management · dependency policy ·
incident contact and disclosure path · open risks (R ids) · items requiring professional review
(penetration test, compliance audit) where the product's risk warrants it.
