# Research note — AI providers (questions for N005 / N007)

Nothing here is verified yet. These are the questions the spikes must answer with dated sources:

## Speech-to-text (N005)
- Word error rate on our 30 labelled calls (sales vocabulary, accents, crosstalk).
- Diarization quality on mixed-track audio; support for multi-channel input.
- Languages supported (V1: English; note others).
- Data retention options, and contractual no-training on customer audio.
- Pricing per audio hour at our volume (fresh, dated); rate limits; batch vs streaming.
- Region availability (EU residency, R-008).

## LLM extraction (N007)
- Current models, context limits, structured-output/JSON-schema support.
- Quality on the N006 eval set per model; latency p95 per call.
- Price per million tokens (fresh, dated) → cost per audio hour (feeds COST.md and A-005).
- Data-use terms: no training on API data; zero-retention options; regional processing.
- Rate limits and batch options for off-peak processing.
