# `.raftly/` reference

JSON Schemas live in `${CLAUDE_SKILL_DIR}/schemas/`. `raftly validate` checks all of them plus cross-references.

## Directory (create only what applies)

```text
.raftly/
├── state.yaml            canonical state (mode, stage, blueprint, execution, production, documents, counts, history)
├── requirements.yaml     REQ-xxx: statement, priority, status, features, decisions, supersedes/superseded_by
├── assumptions.yaml      A-xxx: statement, confidence, impact_if_false, validation_method, state
├── risks.yaml            R-xxx: category, statement, probability, impact, severity, mitigation, owner_role, status
├── dependencies.yaml     name, version, purpose, license, kind, chosen_by, status, lock_in, last_review
├── experiments.yaml      EXP-xxx: hypothesis, thresholds, window, on_success/on_failure, status
├── build-graph.yaml      N-xxx nodes: type, depends_on, status, features, prompts, definition_of_done, blockers
├── evidence.yaml         entities (SCR/API/TBL/TEST/...), links (relations), records (EV-xxx results)
├── gate.yaml             production + forgotten-20 checks with status/evidence
├── PROJECT.md EXECUTIVE.md PRODUCT.md RESEARCH.md DESIGN.md DESIGN_SYSTEM.md ARCHITECTURE.md
├── DATA_MODEL.md SECURITY.md BUILD.md LAUNCH.md DECISIONS.md HANDOFF.md (+ GTM/PRIVACY/COMPLIANCE_READINESS/COST/MIGRATION)
├── decisions/ADR-xxx-*.md        frontmatter: id,title,owner_role,date,status,decision_type,impact,reversibility,type1,confidence,affects,supersedes,superseded_by,evidence,revisit_trigger,override
├── features/Fxxx-*.md            frontmatter: id,name,status,priority,owner_role,node,requirements,decisions,depends_on,screens,evidence_status
├── prompts/NNN-*.md              self-contained implementation prompts
├── debt/DEBT-xxx-*.md            frontmatter: id,title,type,risk,status,owner_role,introduced_by,fix_trigger,affects
├── learnings/L-xxx-*.md          frontmatter: id,title,outcome,kind,+firewall dimensions,candidate
├── learning-candidates/LC-xxx-*.md and proposals/
├── postmortems/PM-xxx-*.md       frontmatter: id,title,severity,status,date,affects,learning
├── research/  design/  brand/tokens.json
└── .backup/                      created by migrate_schema.py
```

## Enums

- **mode**: GREENFIELD BUILD REVIEW RECOVERY MIGRATION SCALE LAUNCH OPERATE HANDOFF DOCTOR
- **stage**: INTAKE ASSESSMENT RESEARCH PRODUCT DESIGN ARCHITECTURE PLANNING BLUEPRINT_COMPLETE BUILDING VERIFYING LAUNCH_READINESS LAUNCHED OPERATING
- **blueprint section**: NOT_STARTED IN_PROGRESS COMPLETE NOT_APPLICABLE (sections: product design architecture data security build)
- **work status**: NOT_STARTED PLANNED IN_PROGRESS PARTIAL BLOCKED IMPLEMENTED_UNVERIFIED VERIFIED COMPLETE DROPPED
- **decision**: type AUTO/RECOMMEND/FOUNDER; status PROPOSED/ACCEPTED/SUPERSEDED/REJECTED/DEPRECATED; impact and reversibility low/medium/high
- **gate**: PASS WARNING FAIL UNVERIFIED NOT_APPLICABLE; severity blocker/major/minor
- **evidence kind**: test e2e manual review metric audit (verification) · build lint research doc (supporting); result PASS/FAIL/INFO
- **owner roles**: see `core/roles.yaml`

## Stage rules (enforced by `raftly state stage`)

- BUILDING and later require BLUEPRINT_COMPLETE first (except from ASSESSMENT for existing repos).
- BLUEPRINT_COMPLETE requires the Blueprint Completion Gate (`raftly validate --blueprint-gate`).
- LAUNCHED requires LAUNCH_READINESS and gate readiness READY or READY_WITH_WARNINGS, or `--override-reason` (logged).
- Going back to an earlier planning stage is allowed (requirement changes). INTAKE cannot be re-entered.

## Versioning

`state.yaml forge.version` (plugin semver) and `forge.schema_version` (integer). Older schemas: run
`raftly migrate --dry-run`, then `raftly migrate` (backup in `.raftly/.backup/`, history preserved, decisions never reinterpreted).
