# Example: SalesLens (B2B AI sales coaching)

Prompt: `/raftly Build a B2B AI sales coaching platform that ingests sales calls and identifies objections, competitors, and coaching opportunities.`

- **State:** GREENFIELD · BLUEPRINT_COMPLETE · build 0% · readiness INSUFFICIENT_EVIDENCE · 42 applicable production checks
- **Key decisions:** modular monolith (ADR-001), Postgres + RLS tenancy (ADR-002, Type-1), Auth.js + own org model (ADR-003), pg-boss queue (ADR-005), STT via spike (ADR-006), LLM extraction with evidence quotes (ADR-007), eval gating (ADR-008), queue-first design (ADR-009), Stripe (ADR-010), Zoom-only (ADR-011), retention + consent (ADR-012)
- **Open founder decision:** pricing model (per-seat + allowance vs usage-based)
- **Build graph:** 14 nodes, 9 phases · **Prompts:** `.raftly/prompts/001…014`
- **Open:** [artifacts/blueprint.html](artifacts/blueprint.html) · [artifacts/deck.md](artifacts/deck.md) · [.raftly/EXECUTIVE.md](.raftly/EXECUTIVE.md)

Walkthrough: [docs/walkthrough-b2b-saas.md](../../docs/walkthrough-b2b-saas.md).
