# Product strategy and product direction

Roles: **Head of Product Strategy** (`product-strategy`) and **Director of Product** (`product-director`).

## Strategy: is this the right problem?

1. **Problem statement**: who hurts, when, how often, and what it costs them today. Use the user's words.
2. **ICP / primary user**: be specific enough that you could find 10 of them. For B2B, separate buyer, admin and end user.
3. **Jobs to be done**: "When <situation>, I want to <motivation>, so I can <outcome>."
4. **Current workflow**: what they do today (tools, workarounds) and where it breaks.
5. **Differentiation**: why this beats the status quo and the obvious alternatives, in terms of outcomes,
   not features. Competitor research identifies expectations and gaps; it is never a template to copy.
6. **Validation strategy**: the riskiest assumptions and the cheapest way to test each one (interviews,
   concierge test, landing page, prototype, usage data).
7. **Success and failure criteria**: measurable, time-boxed.

For utilities and small personal tools, keep strategy proportionate: a paragraph each, no market sizing theatre.

## Product direction: what exactly is V1?

- **MVP scope**: the smallest product that delivers the core job end-to-end with production quality.
  An MVP is a thin, complete slice, not a broken wide one.
- **Explicit exclusions**: list what is deliberately not in V1 and why. Deferring is a decision.
- **Prioritisation**: MoSCoW (`MUST/SHOULD/COULD/WONT`) for requirements; sequence by dependency and risk
  reduction, not by excitement.
- **Requirements** are observable outcomes: "Results are correct to 15 significant digits for decimal input",
  not "use decimal.js". Implementation choices belong in ADRs.
  `raftly records add requirement --statement "..." --priority MUST --rationale "..."`
- **User stories and acceptance criteria** live in feature specs (Given/When/Then is fine).
- **Workflows**: the primary flow end-to-end, plus the alternate and error paths users will actually hit.

## Challenge mandate (Constitution 11)

Push back, respectfully and concretely, when:
- a feature has no user outcome ("add AI" with no job attached);
- a technology is requested for its own sake (blockchain, microservices, Kubernetes for a small app);
- scope grows without evidence of need;
- a requirement contradicts privacy, security or accessibility obligations.

Pattern: name the underlying need, then the cost of the request, then the simpler alternative, then
record a RECOMMEND ADR. The founder may override, and the override is recorded.

## Kill criteria and experiments (spec §30)

For each product bet:
`raftly records add experiment --hypothesis "..." --metric "..." --success "≥30% of trial orgs upload 3+ calls in week 1" --failure "<10% ..." --window "first 30 trial orgs" --on-success "..." --on-failure "..."`.
When an experiment fails its agreed threshold, Raftly recommends stopping or deprioritising the work
(update the experiment status and the affected nodes). Sunk cost is not a reason to continue.

## Success metrics

- One **north-star outcome metric** tied to the core job.
- 2–4 **input metrics** that the team can move.
- **Guardrail metrics** (error rate, churn, cost per user).
- Instrument only what you will use. Analytics on a privacy-first utility can legitimately be "none".

## PRODUCT.md must include

vision · problem · ICP/users · jobs · workflows · positioning · differentiation · V1/MVP · exclusions ·
requirements (table of REQ ids) · feature map (F ids → REQ ids) · success metrics · assumptions (A ids) ·
risks (R ids) · kill criteria (EXP ids). Template: `templates/docs/PRODUCT.md`.

## Example calibration

- **Calculator app + website**: consumer utility. ICP is "anyone doing quick everyday math". The real
  differentiators are correctness (decimal precision, predictable semantics), speed, offline use, history
  and polish. Exclude accounts, sync, a scientific mode (defer), ads and analytics in V1.
- **B2B AI sales coaching**: buyer = sales leader, admin = RevOps, user = reps and managers. Core job:
  "find coaching moments without listening to every call". MVP: ingest calls → transcribe → detect
  objections, competitors and coaching moments with evidence snippets → manager review queue. Exclude
  real-time call assist, CRM write-back and custom model training in V1.
