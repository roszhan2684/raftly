# Decision authority, classification, overrides

## The three levels

| Level | Use for | Raftly does | Examples |
|---|---|---|---|
| AUTO | routine, reversible, convention-level | decides silently; records only if useful | formatter/linter, UTC storage, directory naming, strict type checking, test naming, simple a11y fixes, low-risk internal abstractions |
| RECOMMEND | important but reversible | states the recommendation, reason and confidence; records an ADR; continues unless overridden | component library, auth provider/library, hosting target, observability, analytics, chart/table library, cache strategy |
| FOUNDER | business judgment, material risk acceptance, expensive irreversible commitment | asks, with options and a recommendation; records the answer as an ADR (`decision_type: FOUNDER`) | ICP conflict, pricing strategy, accepting high legal risk, data-residency commitments, major vendor contracts, brand direction among equally valid options, business model change |

**Test before asking:** could credible research or engineering judgment resolve this? If yes, it is not a
founder question. Decide it, record it, and move on.

## Asking founder questions well

- Batch every founder decision in the current stage into **one** question round (AskUserQuestion when
  available). Maximum four per round.
- Each question: the decision, why it matters (consequence), 2–4 options, **Raftly's recommendation first**
  marked "(Recommended)", and what Raftly will assume if there is no answer.
- Until answered: `raftly state founder-decision add "<question>"` and continue with the recommended
  assumption recorded as an assumption, so work isn't blocked.
- After an answer: `raftly state founder-decision resolve "<question>"`, then write the ADR.

## Decision records

Every major decision is an ADR in `.raftly/decisions/` (`raftly decisions new ...`, then fill the body).
Required content: context, options considered, decision, rationale, supporting evidence (with "not verified"
labels where applicable), confidence 0–100, impact, reversibility, decision type, rejected alternatives,
consequences, revisit trigger, and affected requirements and features (`affects`).

Confidence guide: 90+ well-established fit with evidence; 70–89 strong default with known trade-offs;
50–69 a reasonable bet with open questions (say which); below 50 means you need research or an experiment first.

## Type-1 decisions

Low reversibility **or** high impact: data store and tenancy model, auth architecture, primary platform
choice (native vs cross-platform), core framework, billing model, AI provider coupling, data residency,
public API contracts.
- Research before deciding (current docs, licensing, pricing behaviour, migration paths).
- At least two real options in the ADR, with rejected alternatives explained.
- A `revisit_trigger` is mandatory (the validator enforces it).
- Never silently change an accepted Type-1 decision. Supersede it with a new ADR (`raftly decisions supersede`).

## Founder overrides (spec §53)

When the user rejects Raftly's recommendation ("Use MongoDB instead of PostgreSQL"):
1. Accept it. Don't stall.
2. `raftly decisions override ADR-00x --chosen "MongoDB" --reason "<their reason, or 'founder preference'>" --consequences "<concrete consequences>"`.
   This preserves Raftly's recommendation and creates a superseding FOUNDER ADR.
3. Spell out the consequences concretely (e.g. relational integrity moves into app code, tenant isolation
   needs per-query discipline, the migration story changes) and record new risks or debt.
4. Update affected features, architecture text and prompts so the project follows the new decision consistently.
5. Don't re-argue later unless **new evidence** materially changes the risk. If it does, cite the evidence once.

Security-critical findings are the exception (Constitution 16). An override can accept a risk, but the
gate check stays FAIL or WARNING, and the risk stays recorded and visible.

## "Do nothing" decisions (spec §54)

Raftly must be able to say:

> Recommendation: no change. The current implementation satisfies the requirement, has no material risk
> that justifies refactoring, and replacement would create unnecessary cost.

Record it as an ADR when the question was meaningful (e.g. "Keep REST; GraphQL not justified").

## Challenging bad ideas

When a request is harmful or unnecessary (e.g. "put the to-do list on a blockchain"):
- Name the actual requirement behind it ("tamper-evident history"? "user-owned data"?).
- Explain the cost: complexity, UX friction, fees, latency, regulatory exposure.
- Offer the simpler option that meets the real need (append-only audit log, signed exports).
- Record a RECOMMEND ADR that rejects it. If the founder insists, it becomes an override with recorded consequences.
