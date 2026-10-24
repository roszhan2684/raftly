# Compliance Readiness — SalesLens

> This checklist is engineering readiness guidance produced by Raftly. It is **not legal advice and not a
> certification**. Items marked NEEDS_PROFESSIONAL_REVIEW require a qualified professional.

| Obligation (likely applicable) | Why it may apply | Item | Status | Evidence |
|---|---|---|---|---|
| Call-recording consent laws | recordings include prospects in many jurisdictions; some require all-party consent | consent attestation + policy notice (REQ-010); customer guidance article | GAP (planned N004) | — |
| Call-recording consent laws | as above | review of attestation language and customer responsibilities | NEEDS_PROFESSIONAL_REVIEW | — |
| GDPR / UK GDPR (EU/UK customers) | personal data of employees and prospects | DPA template; subprocessor list; records of processing; transfer mechanism | NEEDS_PROFESSIONAL_REVIEW | — |
| GDPR data-subject rights | as above | export/deletion tooling (F009) | GAP (planned N012) | — |
| GDPR data residency expectations | EU customers may require EU hosting | founder decision when the first EU customer appears (R-008) | GAP (deferred) | — |
| CCPA/CPRA (California) | personal data of California residents | service-provider terms; rights requests handling | NEEDS_PROFESSIONAL_REVIEW | — |
| Employment/works-council rules (some EU countries) | coaching insights about employees | customer-facing guidance; feature toggles (reps see insights) | NEEDS_PROFESSIONAL_REVIEW | — |
| AI transparency expectations | AI-generated insights about people | label AI insights; human review before sharing (F005) | GAP (planned N008) | — |
| Enterprise security questionnaires / SOC 2 expectations | B2B buyers | security overview, audit log, access controls; SOC 2 requires an independent auditor (not self-declared) | GAP (post-launch roadmap) | — |
| PCI DSS | card payments | Stripe-hosted checkout keeps card data off our systems; confirm the SAQ type with Stripe documentation | NEEDS_PROFESSIONAL_REVIEW | — |

## Professional review
Before the paid launch, a privacy/technology lawyer reviews the DPA, terms, privacy policy, consent language and
subprocessor list. Their written confirmation is recorded as evidence for G-COMPLIANCE-READINESS and G-LEGAL-DOCS.
