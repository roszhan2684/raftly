# Research note — architecture options

Workload estimate for V1 (assumption, refine with pilot data): 30 orgs × 20 reps × 15 calls/week × 40 min average
≈ 6,000 audio hours per month at the top of the V1 range, i.e. ~9,000 calls per month, or roughly one call every
5 minutes on average with weekday peaks. Each call needs one transcription job (minutes) and several extraction
calls (seconds each).

Conclusion: one web deployable plus one worker pool comfortably handles this. Postgres serves as the queue and the
store. No independent scaling or team boundary justifies services (ADR-001). Revisit at sustained throughput limits.
