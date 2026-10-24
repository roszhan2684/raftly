# Evidence graph

Raftly links intent → implementation → verification so it can answer "why does this exist?", "what breaks
if we remove it?", "which requirements have no tests?" and "which features are UI-only?".

Chain: Requirement → Decision → Design → Feature → Screen/Component → API → Service → Table → Test → Metric.

## IDs

| Kind | Format | Where |
|---|---|---|
| Requirement | `REQ-001` | requirements.yaml |
| Decision | `ADR-001` | decisions/ |
| Feature | `F001` | features/ |
| Build node | `N001` | build-graph.yaml |
| Assumption / Risk | `A-001` / `R-001` | assumptions.yaml / risks.yaml |
| Debt / Learning / Candidate / Postmortem | `DEBT-001` / `L-001` / `LC-001` / `PM-001` | md records |
| Evidence record | `EV-001` | evidence.yaml `records` |
| Experiment | `EXP-001` | experiments.yaml |
| Implementation entities | `SCR-*`, `CMP-*`, `API-*`, `SVC-*`, `TBL-*`, `TEST-*`, `MET-*`, `JOB-*`, `INT-*` | evidence.yaml `entities` |

Entity ids are readable slugs: `API-calls-create`, `TBL-calls`, `TEST-engine-precision`, `MET-p95-analysis-latency`.

## Relations (`raftly evidence link FROM TO --rel R`)

| Relation | Direction (FROM → TO) | Example |
|---|---|---|
| justifies | requirement/decision → thing it motivates | `REQ-002 → F003` |
| implements | implementation → feature/requirement | `SVC-analysis → F004` |
| renders | screen/component → feature | `SCR-review-queue → F005` |
| exposes | API → feature | `API-calls-create → F002` |
| persists | table → feature | `TBL-insights → F004` |
| verifies | test → feature/requirement/API | `TEST-tenant-isolation → F001` |
| measures | metric → feature/assumption | `MET-activation → A-002` |
| validates | evidence/metric → assumption | |
| depends_on | any → dependency | |
| mitigates | feature/decision → risk | `F001 → R-003` |
| supersedes | new → old | written by change-requirement |

Requirement → feature, feature → node, and decision → feature links are **implicit** from the registries
(`requirements.yaml features`, feature frontmatter `node`/`requirements`/`decisions`). Don't duplicate them.

## Recording while building

1. Register what you build: `raftly evidence entity --id API-calls-create --name "POST /api/calls" --path src/api/calls.ts --status EXISTS`.
2. Link it: `raftly evidence link API-calls-create F002 --rel exposes`.
3. Register tests and link them with `verifies`.
4. Attach **real** results: `raftly evidence record --subject TEST-calls-api --kind test --result PASS --summary "18 passed" --command "pnpm test api/calls"`.
   A passing record on a `TEST-*` entity verifies whatever that test `verifies`.
5. A later FAIL on the same subject revokes verification until a newer PASS.

## Queries

`raftly evidence why API-calls-create` · `raftly evidence impact TBL-calls` · `raftly evidence untested` ·
`raftly evidence ui-only` (only meaningful with a backend) · `raftly evidence for F002`.
Use them for Explain answers and impact analysis. Cite the ids in replies.

v0.1 links are recorded explicitly. Automatic AST-based tracing is a v0.2 candidate.
