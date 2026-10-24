**GREENFIELD · BLUEPRINT_COMPLETE · Calculator (mobile + web) blueprint ready**

**[Head of Product Strategy]** Consumer utility. The differentiators are correctness, speed, offline use and polish,
not features. V1: arithmetic with correct precedence, decimal-exact results, history, copy, keyboard input on web,
haptics on mobile, light/dark theme, fully offline. Deferred: scientific mode, unit conversion, accounts and sync, ads.

**Decisions made**
- ADR-001 Client-only architecture: no backend, auth or database (RECOMMEND, 92). Server-side launch checks are N/A.
- ADR-002 One shared TypeScript engine, separate from the UI (AUTO-level, recorded because it shapes the build graph).
- ADR-003 Decimal arithmetic instead of binary floats (RECOMMEND, 90): `0.1 + 0.2` must equal `0.3`.
- ADR-004 Expo + React Native Web for one codebase across iOS, Android and web (RECOMMEND, 72; research checked, see RESEARCH.md).
- ADR-005 Design direction B "Modern utility" (live expression line + history drawer) over native-minimal and workspace (RECOMMEND, 75).

**What changed**: `.raftly/` initialised with 9 requirements, 6 features, 7 build nodes and 7 prompts. PRODUCT, DESIGN,
DESIGN_SYSTEM, ARCHITECTURE, SECURITY, BUILD, EXECUTIVE and DECISIONS written. Blueprint at `artifacts/blueprint.html`,
deck source at `artifacts/deck.md`.

**Open founder decisions**: none.

**Readiness**: blueprint COMPLETE · build 0% · production INSUFFICIENT_EVIDENCE (16 applicable checks, 29 N/A for a client-only app).

**Next action**: `/raftly build next` starts N001 "Calculation engine" (prompt 001).
