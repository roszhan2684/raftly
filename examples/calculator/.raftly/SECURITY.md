# Security — Tally

## Summary
Tally is a client-only app with no backend, no accounts and no data collection (ADR-001, ADR-008). Its attack
surface is limited to the input parser, the web delivery chain and dependencies. Server-side controls are not
applicable. This document describes readiness, not a certification. Evidence for each control is collected in
N006/N007 and recorded in gate.yaml.

## Threat model
| Asset | Actor | Entry point | Threat | Control | Status |
|---|---|---|---|---|---|
| Device integrity | malicious paste | paste / keyboard input | code injection via evaluation | tokenizer + parser only; input is never run as code (F001) | planned |
| Users of the website | network attacker / third-party script | web delivery | script injection, tampering | HTTPS + HSTS, strict CSP `default-src 'self'`, no third-party scripts | planned (N006) |
| Build integrity | compromised dependency | npm supply chain | malicious package | lockfile, minimal dependencies, audit in CI | planned |
| User trust | — | store listing | inaccurate privacy disclosure | "Data Not Collected" verified by a proxy check (no network calls) | planned (N006) |

## Controls
| Control | Applies? | Status | Evidence |
|---|---|---|---|
| No secrets in source or bundle | yes | UNVERIFIED | secrets scan (N007) |
| Dependency audit | yes | UNVERIFIED | audit report (N007) |
| CSP and security headers | yes (web) | UNVERIFIED | header check on the deployed URL (N006) |
| Safe expression parsing | yes | UNVERIFIED | engine tests + fuzzing (N001) |
| Authentication / authorisation / tenant isolation | no | NOT_APPLICABLE | ADR-001 |
| Rate limiting, backups, monitoring | no | NOT_APPLICABLE | ADR-001 |

## Data protection
No personal data is collected or transmitted. History stays on the device and is removed with app data.

## Secrets management
None at runtime. Store signing credentials live in the build service's secret storage, never in the repository.

## Dependency policy
Lockfile committed; dependencies limited to dependencies.yaml; an audit runs in CI; updates reviewed monthly or on advisories.

## Incident contact and disclosure
A security contact address on the website and in the store listings (to be created in N006). Fix, then release through the normal path.

## Open risks
R-002 (web performance, indirect), R-004 (store review). There are no open security risks of high severity.

## Requires professional review
None at this risk level. The privacy policy text needs a human review before publishing (G-LEGAL-DOCS).
