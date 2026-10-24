User: "Use MongoDB instead of PostgreSQL."

**BUILD · ARCHITECTURE · Override recorded: MongoDB replaces PostgreSQL (ADR-011 supersedes ADR-004)**

**[Principal Data Engineer]** Understood. Proceeding with MongoDB. Raftly's original recommendation is preserved in ADR-004.
Consequences, now recorded:
- Tenant isolation moves from row-level security to a mandatory scoped repository. New risk R-012 (high) and a cross-tenant test is required.
- Reporting joins (coaching trends by team) become aggregation pipelines. +1 node for the analytics read model.
- Transactions are available but need replica-set deployment. Hosting choice ADR-007 is unaffected.

Updated: ADR-011 (FOUNDER), R-012, F004/F007 data notes, prompts 004 and 007, ARCHITECTURE.md (marked CURRENT).
I won't re-argue this unless new evidence materially changes the risk.

**Next action**: continue N003 with the MongoDB data layer.
