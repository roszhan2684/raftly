# Research engine

## When to research

Research when the information is **external, current, uncertain, or material** to a decision.
Don't research things you can settle with stable engineering knowledge (for example, "store timestamps in UTC").

Search triggers:
- framework/library capabilities, versions, deprecations, licences;
- platform distribution rules (app stores, browser APIs);
- pricing and free-tier limits (always current; never from memory);
- legal/regulatory obligations for the domain;
- competitor conventions and user expectations;
- AI model capabilities, limits, pricing and latency;
- security advisories for chosen dependencies.

## Categories

market · competitors · workflows · user terminology · product conventions · technical architecture ·
current framework/library docs · licensing · security · compliance · legal/regulatory · pricing/cost ·
platform distribution · design/UX patterns · open-source components · reliability/scaling · AI providers.

## Domain triggers

| Domain | Research at minimum |
|---|---|
| Healthcare | whether PHI is involved; HIPAA engineering readiness (Security/Privacy Rule safeguards); BAA needs for every vendor touching PHI; audit logging; retention; clinical workflow terminology |
| Fintech | data classification; PCI DSS scope (prefer tokenised processors to shrink scope); KYC/AML relevance; auditability; transaction integrity |
| AI products | current model features and limits; inference cost; latency; structured outputs; prompt injection; eval strategy; fallback; model/version drift; PII leakage; provider data-use terms |
| Developer tools | OAuth scopes; API rate limits; webhooks; CLI conventions; API versioning; SDK expectations |
| Mobile | store distribution and review rules; platform capabilities; background execution limits; accessibility APIs; web vs native trade-offs |
| Children / education | COPPA/age-appropriate design considerations; parental consent |
| Marketplaces / payments | money transmission considerations; payout providers; dispute flows; tax handling |
| EU users | GDPR basics: lawful basis, data subject rights, processors/DPAs, transfers |

## Source hierarchy

1. Official documentation, specifications, standards bodies, regulators, licence texts (primary).
2. Vendor engineering blogs and changelogs, reputable maintainers.
3. Well-known community sources (for conventions only).
4. Everything else: treat as a lead, not as evidence.

Competitor research is for **expectations and gaps**, never for copying proprietary design or content.

## Recording research

- `.raftly/RESEARCH.md`: a concise summary table, one row per question: question · finding · source(s) ·
  date checked · confidence · decision(s) it informs.
- `.raftly/research/<topic>.md` for longer notes, with quotes trimmed to what matters.
- Put the source URL or `research/<topic>.md` in the ADR's `evidence` list.
- Date every finding. Pricing and limits go stale fast. Write "checked YYYY-MM-DD".

## Honesty rules

- **Never manufacture search results, URLs, quotes, version numbers, prices or benchmarks.**
- If browsing or tools are unavailable, write findings as **"Not verified: from prior knowledge, re-check
  before relying"**, lower the confidence, and add a research task or assumption.
- If sources conflict, record both and explain which one you trust and why.
- If research can't resolve a material question, it becomes an assumption with a validation method,
  or a founder question if it involves business judgment.

## Research depth by decision type

| Decision | Depth |
|---|---|
| AUTO | none; engineering judgment |
| RECOMMEND | one or two primary sources confirming fit, licence and maintenance |
| Type-1 / FOUNDER | several primary sources, alternatives compared, cost and migration implications, revisit trigger |
