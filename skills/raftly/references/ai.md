# AI / ML engineering

Role: **Principal AI/ML Engineer** (`ai-ml`), with security and privacy.

## First question: does this need a model?

Use deterministic code when rules are known (parsing, maths, routing). Use an LLM where the task is
language understanding, generation, or fuzzy classification, and where errors can be tolerated or caught.

## Model and provider selection (research required)

Model capabilities, context limits, pricing, rate limits and data-use terms change frequently. **Research
current provider documentation**; never hard-code assumptions from memory into decisions. Compare
quality on *your* eval set, latency (p50/p95), cost per unit of work, structured-output support,
tool use, context length, data retention and training terms, region availability, and SLAs.

Put a thin **provider abstraction** around calls (one interface, prompt templates versioned in code) so
switching is a configuration and eval exercise, not a rewrite. Record the choice as an ADR with a revisit trigger.

## Evals (G-AI-EVALS is a launch blocker for AI products)

- Build a **versioned golden dataset** from realistic, consented or synthetic inputs, with expected labels
  or rubrics. Start with 50–200 cases covering the main categories and the edge cases.
- Define metrics per task: precision/recall for detection (e.g. objections), exact-match or schema validity
  for extraction, rubric scores for generation, and the hallucination rate (claims without support in
  the source).
- Set **thresholds before launch** and gate prompt or model changes on them (regression evals in CI on a
  sample; full runs before release).
- Record eval runs as evidence: `raftly evidence record --subject F00x --kind test --result PASS --summary "objection recall 0.86 ≥ 0.80 on eval-v3"`.

## Prompting and outputs

Version prompts. Use structured outputs (JSON schema) for anything parsed downstream, and validate them.
Ground answers in retrieved source text and require evidence spans (e.g. transcript timestamps) so users can verify.

## RAG (when retrieval is needed)

Chunking aligned to the document structure, metadata for tenant/permission filtering **at query time**,
hybrid search where keyword precision matters, and evaluation of retrieval quality separately from
generation quality.

## Safety and security

- **Prompt injection**: treat retrieved and user-supplied content as data; never let it change system
  instructions or trigger privileged tools; constrain tools by allow-list; require human approval for
  consequential actions.
- **Data leakage**: tenant isolation in retrieval; no cross-tenant few-shot examples; redact PII before
  sending where feasible; honour provider zero-retention options if required.
- **Output handling**: escape and sanitise model output before rendering; never execute it.

## Fallback and degradation

Timeouts and retries with backoff; queue long jobs; a low-confidence path (flag for human review rather
than presenting it as fact); a provider-outage behaviour (retry later, degrade, or switch to a secondary
provider if justified).

## Observability for AI features

Completion success rate, schema-validation failure rate, p95 latency, tokens and **cost per job and per
tenant**, retry count, user rejection/edit rate, hallucination reports, and eval score over time. Enforce
per-tenant budgets and alerts (G-AI-COST).

## Human-in-the-loop

Make the human approve, edit or dismiss AI findings where stakes warrant it, and log the decisions as a
quality signal and future eval data (with consent and retention rules).
