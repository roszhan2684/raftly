# Raftly workflow (detailed)

This is the operating procedure behind SKILL.md. `raftly` = `python3 "${CLAUDE_SKILL_DIR}/scripts/engine.py"`.

## Contents
1. First-invocation algorithm
2. Greenfield: stage by stage
3. Planning: build graph, features, prompts
4. Blueprint Completion Gate and deliverables
5. Resume (later invocations)
6. Existing repositories (REVIEW / RECOVERY)
7. Requirement changes
8. Execution contract (BUILD)
9. Context discipline

---

## 1. First-invocation algorithm

```text
START /raftly
  raftly context                      (repo inspection + state + next action; read-only)
  read core/CONSTITUTION.md          (once per session)
  .raftly present?
    NO  -> infer GREENFIELD / REVIEW / RECOVERY from repo + request
           raftly init ... (existing code: --mode REVIEW|RECOVERY, stage ASSESSMENT; never touch code)
    YES -> schema current? (context says needs_migration -> raftly migrate --dry-run, then migrate)
           integrity errors? -> fix first (raftly validate)
           infer mode from intent; respect recorded decisions
  parse goal -> unknowns -> research needs -> route to senior role -> authority model
  record (scripts) -> update graph/docs -> raftly validate
  blueprint coherent? -> raftly validate --blueprint-gate -> BLUEPRINT_COMPLETE -> deliverables, prompts, artifact, deck
  execution requested? -> execution contract (§8)
  report: what changed, decisions, blockers, readiness, next action
END
```

Do as much as the request allows in one invocation. Don't stop after each stage to ask permission.
Stop only for genuine FOUNDER decisions, and batch those.

## 2. Greenfield, stage by stage

### INTAKE
- Restate the idea in one sentence and classify it: `product_type` (e.g. `consumer-utility`,
  `b2b-saas`, `devtool`, `marketplace`, `healthcare-saas`, `internal-tool`, `ai-app`, `mobile-game`).
- Build the **profile** honestly. It decides which production checks apply:

| Flag | Set true when |
|---|---|
| `surfaces` | list of `web`, `ios`, `android`, `mobile` (cross-platform), `desktop`, `cli`, `api`, `library`, `extension` |
| `backend` | the product needs a server you operate (not merely static hosting) |
| `accounts` | users sign in |
| `personal_data` | you store or process personal data on a server or in third-party services |
| `sensitive_data` | `phi`, `financial`, `payment_card`, `children`, `biometric`, `precise_location`, `government_id`, `credentials` |
| `payments` | you charge money in-product |
| `multi_tenant` | multiple customer organisations share the system |
| `ai` | LLM/ML features in the product |
| `public_site`, `email`, `file_uploads`, `integrations`, `analytics` | as named |
| `regulated` | e.g. `[HIPAA]`, `[GDPR]`, `[PCI]` when likely applicable |

- `raftly init --name "<Name>" --product-type <type> --summary "<user's idea>" --profile surfaces=[web] backend=true ...`
- `raftly state stage RESEARCH` (or straight to PRODUCT when nothing needs researching).

### RESEARCH
- List the open questions. Each one is *researchable* (current docs, licensing, competitors,
  regulations), *assumable* (record as an assumption with a validation method) or *founder-only*.
- Research the researchable ones that are material (see research-engine.md). Write `RESEARCH.md`
  from `templates/docs/RESEARCH.md`. Put longer notes in `.raftly/research/<topic>.md`.
- Record assumptions: `raftly records add assumption --statement ... --confidence 40 --impact high --impact-if-false ... --validation ...`.

### PRODUCT
- Product Strategy + Director of Product: problem, ICP, jobs, current workflow, differentiation, V1 scope,
  explicit exclusions, success metrics, kill criteria.
- Requirements: `raftly records add requirement --statement "..." --priority MUST --rationale "..."`.
  Write them as observable outcomes, not implementation.
- Experiments with kill criteria: `raftly records add experiment ...` for the riskiest assumptions.
- Write `PRODUCT.md` (template). Then `raftly state blueprint product COMPLETE`.

### DESIGN
- When the product has a UI, follow ux-design.md: IA, navigation, **2–3 genuinely different directions**
  for the main UI decision (they must differ in interaction model or IA, not just colour), recommend one,
  and record an ADR (`--owner design-director`). Then key screens with full state specs, responsive
  behaviour, accessibility, and design-system tokens.
- The design direction is usually RECOMMEND (reversible). It becomes FOUNDER only when brand direction
  is a genuine business choice between equally valid options.
- Write `DESIGN.md` and `DESIGN_SYSTEM.md`, then `raftly state blueprint design COMPLETE`. For a headless
  API, library or CLI, use `NOT_APPLICABLE` and document the developer experience in PRODUCT.md instead.

### ARCHITECTURE
- Architect + engineers: the simplest viable architecture, recorded in ADRs. Every Type-1 choice gets options,
  evidence, consequences and a revisit trigger.
- Build vs OSS vs managed vs paid for each meaningful subsystem (architecture.md §Build-vs-buy).
  Record chosen dependencies: `raftly records add dependency --name ... --license MIT --status ADOPTED --chosen-by ADR-003`.
- Data (data.md): `DATA_MODEL.md` when there is persistent data. Set `raftly state blueprint data NOT_APPLICABLE` when none.
- Security and privacy (security.md, privacy-compliance.md): `SECURITY.md`, plus `PRIVACY.md` and
  `COMPLIANCE_READINESS.md` when relevant. Record risks: `raftly records add risk ...`.
- Write `ARCHITECTURE.md`. Then mark the architecture, data and security sections COMPLETE or NOT_APPLICABLE.

### PLANNING
See §3.

## 3. Planning: build graph, features, prompts

1. **Capabilities, not weeks.** List the capabilities the product needs. Create nodes in dependency order:
   `raftly graph add --name "Calculation engine" --type foundation --dod "Engine pure and UI-free;Precision rules tested"`
   then `raftly graph add --name "Keypad UI" --type feature --depends N001`.
   Types: foundation, feature, security, data, ops, quality, design, integration, launch, migration, research.
2. **Feature specs** for every significant feature:
   `raftly records new feature --name "History" --priority SHOULD --node N003 --requirements REQ-004`.
   Then fill every section of `.raftly/features/F00x-*.md` (template: `templates/records/feature.md`).
   Every MUST requirement must map to at least one feature.
3. **Prompts**: one or more per node: `raftly records new prompt --title "History" --node N003 --role "Staff Frontend Engineer"`.
   Fill the generated `.raftly/prompts/00x-*.md` completely: files to read, objective, tasks, out of scope,
   edge cases, security and accessibility requirements, tests, verification, state updates, escalation rules.
   Each prompt must work on its own in a fresh Claude session.
4. **Test strategy**: put it in BUILD.md under a `## Test strategy` heading (qa.md).
5. **Production gate**: `raftly gate init` instantiates only the checks that apply to the profile.
6. `raftly graph render` writes the graph section into BUILD.md. Fill in the rest of BUILD.md from the template.
7. `raftly state blueprint build COMPLETE`.

## 4. Blueprint Completion Gate and deliverables

`raftly validate --blueprint-gate` checks: all six sections resolved, the core documents exist, MUST
requirements map to features, ADRs exist, assumptions exist, the graph is valid with prompts, BUILD.md has a
test strategy, and the gate is initialised. When it passes:

1. `raftly state stage BLUEPRINT_COMPLETE` (the stage and the blueprint status are set together).
2. Generate or refresh the package (documents.md): PRODUCT, DESIGN, DESIGN_SYSTEM, ARCHITECTURE, DECISIONS
   (`raftly decisions book`), BUILD, EXECUTIVE, SECURITY, plus whichever supporting documents apply.
   Register each with `raftly state doc <FILE> CURRENT`.
3. Blueprint artifact (artifact-generation.md) and deck (presentation-generation.md).
4. Unresolved founder decisions stay listed in `blueprint.open_founder_decisions`. Report them clearly.
5. `raftly validate` must show zero errors. Resolve placeholder warnings in core documents.

## 5. Resume (later invocations)

- Trust state. Don't re-plan what is decided. Read the context output, then only the files the next step needs.
- With no new instruction, do the recommended next action: continue the blueprint gaps, build the next
  node, or run the gate.
- If the user's new message changes scope, use the Requirement Change Engine (§7). Don't silently edit
  old documents.
- Stale documents (`documents.*.status = STALE`) must be refreshed before they are used as a source.

## 6. Existing repositories (REVIEW / RECOVERY)

1. Use `raftly context` and `raftly inspect` for the stack, boundaries, tests, CI and signals. Read the README,
   the main entry points and the data layer. Don't read everything.
2. Infer the product, its users, the architecture, and the main flows. Record inferences as **assumptions**
   (with confidence) and never as facts.
3. `raftly init --mode RECOVERY|REVIEW --stage ASSESSMENT ...`. **No code changes in this step.**
4. Write `PROJECT.md` findings and an `ARCHITECTURE.md` describing **what exists**, labelled "current",
   kept separate from "proposed". Record existing major choices as ADRs with `--status ACCEPTED` and a note
   "inferred from repository".
5. Build a recovery graph: verification nodes for what exists (`IMPLEMENTED_UNVERIFIED`), repair nodes
   for broken flows, then missing capabilities.
6. Ask only the business-critical questions you cannot infer. Respect the existing architecture.
   Propose change only where there is material risk (architecture.md §Drift).

## 7. Requirement changes

`raftly records change-requirement REQ-00x --statement "<new>" --reason "<why>"` will:
- create the new requirement and supersede the old one (history preserved),
- list impacted features, decisions, nodes and linked entities (screens, APIs, tables, tests, metrics),
- mark affected documents STALE and log the event.

Then you: assess legal, billing and migration impact, update feature specs, write superseding ADRs where
decisions change, add nodes and prompts, re-render BUILD.md, refresh stale documents, and record risks.
Example: per-seat → usage-based pricing touches billing integration, metering data, entitlement checks,
the pricing page, terms, analytics and tests.

## 8. Execution contract (BUILD)

1. `raftly context` → `raftly graph next`.
2. Read the node's prompt(s) plus only the ADRs and features they reference. Inspect the existing code.
3. Confirm the node is unblocked (dependencies VERIFIED or COMPLETE).
4. `raftly graph set-status N00x IN_PROGRESS`; also `raftly records feature-status F00x IN_PROGRESS`.
5. Implement. Stay inside the architecture's boundaries. New dependencies need a reason and a dependencies record.
6. Run tests, lint and build. Record the actual results:
   `raftly evidence record --subject F00x --kind test --result PASS --summary "34 passed" --command "npm test"`.
   Register test entities and link them: `raftly evidence entity --id TEST-history ...`, then `raftly evidence link TEST-history F00x --rel verifies`.
7. Check every acceptance criterion and DoD item. Tick `[x]` only with evidence, `[~]` with a reason for N/A.
8. Deviations become ADRs, debt (`raftly records new debt ...`) or risks.
9. Statuses: IMPLEMENTED_UNVERIFIED → VERIFIED → COMPLETE, for the feature and the node.
10. `raftly graph render`, `raftly validate`, then report the next unblocked node.

If tests fail: record FAIL evidence, keep the status honest (PARTIAL or IMPLEMENTED_UNVERIFIED), fix or report.

## 9. Context discipline

- `state.yaml` is the index. Don't load every document.
- Load references only for the active role or stage.
- For explain and why questions use `raftly evidence why <ID>`, `raftly decisions list` and the specific ADR.
- Use `--json` output when you need exact data. Use the text output for quick orientation.
