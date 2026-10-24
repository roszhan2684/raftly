# The deliverable package

Generate after BLUEPRINT COMPLETE, and refresh whenever the underlying state changes (`raftly state doc <FILE> CURRENT`).
Templates live in `${CLAUDE_SKILL_DIR}/templates/docs/`. Copy a template into the documents folder (`docs/` in a new
project, `.raftly/` in an existing repository; `raftly context` prints it), then fill **every**
section. Write "Not applicable: <reason>" rather than leaving `TBD`. The validator warns about
leftover placeholders.

## Required (when relevant)

| Document | Purpose | Key contents |
|---|---|---|
| `PRODUCT.md` | what and why | vision, problem, ICP/users, jobs, workflows, positioning, differentiation, V1, exclusions, requirements, feature map, success metrics, assumptions, risks, kill criteria |
| `DESIGN.md` | experience | principles, IA, flows, navigation, key screens (full specs), direction options considered, chosen direction, responsive, states, accessibility, OSS component choices |
| `DESIGN_SYSTEM.md` | tokens and components | typography, spacing, radius, colour semantics, elevation, layout, components, states, motion, accessibility, theme, icons, token examples |
| `ARCHITECTURE.md` | system | context, overview diagram, boundaries, stack (with ADR links), data, security, integrations, reliability, environments, failure behaviour, scaling assumptions |
| `DIAGRAMS.md` | five product diagrams | system architecture, user flow, screen map, data model, critical-path sequence, as Mermaid; see diagrams.md |
| `DECISIONS.md` | decision book | `raftly decisions book` generates the table; add a short intro and the open founder decisions |
| `BUILD.md` | execution guide | build graph (`raftly graph render`), phases, feature order, acceptance gates, test strategy, release requirements |
| `EXECUTIVE.md` | one-page summary | what, who, why, V1, architecture, plan, risks, launch |
| `SECURITY.md` | security posture | see security.md |

## Supporting (generate as relevant)

`DATA_MODEL.md` (persistent data) · `LAUNCH.md` (gate report + plan) · `GTM.md` · `PRIVACY.md` ·
`COMPLIANCE_READINESS.md` (regulated domains) · `COST.md` (material costs) · `MIGRATION.md` (migrations) ·
`RESEARCH.md` · `HANDOFF.md` (`raftly handoff`).

Don't create meaningless documents for categories that don't apply. Mark them in state instead:
`raftly state doc GTM.md NOT_APPLICABLE --reason "personal utility, no GTM"`.

## Quality rules (spec §58)

- No contradictions between documents. When one changes, mark the dependants STALE and refresh them.
- Clearly separate **current** from **proposed** (essential in REVIEW/RECOVERY).
- IDs everywhere: REQ, F, ADR, N, A, R. Refer to them; don't restate their content.
- Concise enough to use. Tables over prose for registries, prose for reasoning.
- Assumptions are labelled as assumptions. Unverified research is labelled "not verified".
- Readiness language for security and compliance. No certification claims.
- `raftly validate` reports zero errors before you announce the package.
