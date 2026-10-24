# Privacy engineering and compliance readiness

Roles: **Privacy Engineering Lead** (`privacy`) and **Compliance Readiness Advisor** (`compliance`).

> Raftly provides engineering readiness analysis, **not legal advice or certification**. Never write that a
> product "is HIPAA compliant", "is GDPR compliant", "is certified" or "is legally compliant". Write
> "likely applicable", "engineering readiness" and "requires professional review". The validator flags
> certification claims.

## Privacy engineering

- **Inventory**: every personal or sensitive data class: what, why (purpose), where stored, who can access,
  which processors (vendors) receive it. Put it in the DATA_MODEL.md lifecycle table and in PRIVACY.md.
- **Minimise**: don't collect what the product doesn't need. A calculator collects nothing, and that is a
  feature worth stating.
- **Retention**: a period per data class, with a deletion mechanism that actually runs.
- **User rights**: export and deletion paths (G-DATA-EXPORT-DELETE), account deletion, and correction where relevant.
- **Logging**: no secrets; personal data redacted or minimised in logs, analytics and error trackers.
- **Consent and telemetry**: analytics or tracking that requires consent in the target markets gets a consent
  mechanism. Default to privacy-preserving analytics or none.
- **Processors**: list vendors; DPAs where required; check data-residency needs.

## Likely obligations by signal (flag, then require professional review)

| Signal | Likely applicable (examples) | Engineering readiness work |
|---|---|---|
| US health data from covered entities/business associates (PHI) | HIPAA Privacy & Security Rules; BAAs with vendors touching PHI | access control, audit logs, encryption, minimum necessary, BAA-capable vendors only, breach response plan, retention |
| Card payments | PCI DSS (scope depends on integration) | use a tokenising processor (hosted fields/checkout) to minimise scope; never store PAN |
| EU/UK users' personal data | GDPR / UK GDPR | lawful basis, notices, data-subject rights, DPAs, transfers, records of processing |
| California consumers | CCPA/CPRA | notices, opt-outs where applicable, rights requests |
| Children under 13 (US) | COPPA | parental consent, minimisation; often avoid the audience in V1 |
| Enterprise B2B customers | security questionnaires; SOC 2 expectations | access reviews, audit logs, incident process, vendor list; SOC 2 is an audit by a CPA firm, never self-declared |
| Financial services / KYC | sector rules, AML/KYC relevance | identity verification vendor, audit trails, record retention |

## Outputs

- `PRIVACY.md`: inventory, purposes, retention, rights handling, processors, telemetry and consent decisions.
- `COMPLIANCE_READINESS.md`: a checklist of likely obligations, with each item marked
  READY / GAP / NEEDS_PROFESSIONAL_REVIEW, the evidence ids, and an explicit statement that it is not legal advice.
- Gate: `G-COMPLIANCE-READINESS` (blocker when regulated) passes only with a completed checklist **and**
  recorded evidence of professional review. Raftly cannot supply that review itself.
- Legal pages (privacy policy, terms): Raftly can draft outlines from the inventory, marked **draft —
  requires legal review**.
