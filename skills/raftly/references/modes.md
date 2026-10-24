# Operating modes

Raftly infers the mode on every invocation, stores it in `state.yaml` (`raftly state mode <MODE> --reason`),
and shows it in the first line of every report. One public skill handles all of them.

| Mode | Entry signals | Objective | Primary outputs | Typical stage |
|---|---|---|---|---|
| GREENFIELD | idea, empty/docs-only repo | idea → validated blueprint | full deliverable package | INTAKE → BLUEPRINT_COMPLETE |
| BUILD | `.raftly/` with unfinished graph; "build next" | implement unblocked nodes with evidence | code, evidence, status updates | BUILDING / VERIFYING |
| REVIEW | "review this", PR, architecture review; existing working code | judge implementation vs requirements/decisions | findings, drift report, ADRs/debt/risks | ASSESSMENT or current |
| RECOVERY | partially built / broken / AI-generated repo | diagnose and repair without rewrite | recovery graph, repair prompts | ASSESSMENT → BUILDING |
| MIGRATION | change DB/auth/framework/provider | safe migration with rollback | MIGRATION.md, ADR, migration nodes | PLANNING → BUILDING |
| SCALE | more load/customers/regions/compliance | prepare system for materially larger demand | capacity plan, ADRs, nodes | PLANNING |
| LAUNCH | "ready to launch?", `/raftly launch` | evidence-gated readiness | gate report, LAUNCH.md, launch deck | LAUNCH_READINESS |
| OPERATE | incidents, metrics, feedback, tickets | learn from production | postmortems, assumption updates, graph changes | OPERATING |
| HANDOFF | "onboard a new engineer" | transferable understanding | HANDOFF.md | any |
| DOCTOR | "what's wrong with this repo?" | health diagnosis, minimal changes | doctor report | any |

## Mode playbooks

### REVIEW
- Read the relevant ADRs, feature specs and acceptance criteria. Compare them with the code.
- Report findings in this order: correctness/security blockers → requirement gaps → architecture drift →
  quality issues → nits (omit nits unless asked).
- For each finding give planned / actual / risk / recommended fix / "change code or change the decision?".
- Record material findings: debt (`architecture_violation`, `defect`), risks, or a superseding ADR.
- "No change needed" is a valid, recordable outcome.

### RECOVERY
- Never start with a rewrite. Inventory what works (mark nodes IMPLEMENTED_UNVERIFIED and verify them),
  what is broken (repair nodes), and what is missing.
- Common AI-generated-repo failure patterns to check: UI with no persistence, auth checked only in the
  frontend, hard-coded secrets, missing migrations, mock data in production paths, no error states,
  duplicated logic, dead dependencies, tests that assert nothing.
- Stabilise first (tests around critical flows), then repair, then extend.

### MIGRATION
Mandatory plan (MIGRATION.md from template, platform-sre.md §Rollback): forward migration, backward
compatibility (expand/contract), backup, phased or canary strategy, application rollback, data rollback or
a compensating strategy, verification queries, and the failure trigger that aborts. A superseding ADR
records why. Destructive steps without backup and rollback reasoning are forbidden.

### SCALE
Quantify first: current load, target load, the bottleneck evidence. Don't add caches, queues or services
without a measured or credibly projected need. Update the cost estimates (architecture.md §Cost).

### LAUNCH
`raftly gate init` (refresh) → collect evidence for each applicable check → `raftly gate set ...` →
`raftly gate report --write` → Forgotten-20 audit → LAUNCH.md and the launch deck. Readiness comes from
evidence only (production-gate.md). Never write a fake PASS.

### OPERATE
Production feedback loop: observation → evidence → hypothesis → affected assumption (`raftly records update A-00x state=INVALIDATED`)
→ product impact → priority → build graph update. One complaint is a data point, not a trend.
Incidents: `raftly records new postmortem --title ... --severity SEV2`. Fill it in, add a regression guardrail,
and run the Learning Firewall on any generalizable lesson.

### HANDOFF
`raftly handoff` writes a deterministic skeleton. Complete the _Needs input_ sections: setup, deploy,
dangerous areas with explanations, and priorities with reasons.

### DOCTOR
`raftly doctor` gives a deterministic report: integrity, failing blockers, unverified requirements, UI-only
features, high debt, repo signals. Add judgment on architecture integrity, dependency health, test health,
security, docs and production readiness. **Don't create unnecessary work.** List the top issues in severity
order. If nothing material is wrong, say "Recommendation: no change."

## Read-only intents (any mode)

- **Explain** ("why PostgreSQL?", "why does endpoint X exist?"): answer from ADRs (`raftly decisions list`,
  then read the ADR), from evidence (`raftly evidence why API-x`) and from requirements. Cite IDs. If no
  recorded rationale exists, say so and offer to record one.
- **Replay**: tell the story in date order from `state.yaml` history, ADR dates, requirement supersessions,
  postmortems and gate evaluations: idea → decisions → features → changes → incidents → launch gates.
