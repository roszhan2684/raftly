# How Raftly is built

```text
forgeai/
├── .claude-plugin/        plugin.json, marketplace.json
├── skills/raftly/          the self-contained skill (works as a plugin skill or copied to ~/.claude/skills/)
│   ├── SKILL.md           lean orchestrator
│   ├── references/        26 playbooks loaded on demand
│   ├── examples/          report shapes
│   ├── assets/            blueprint CSS
│   ├── scripts/           deterministic engine (stdlib Python); engine.py is the single entry point
│   │   └── forgelib/      yamlio, schema, model, project, graph, evidence, gate, learning, checks, docs, mdhtml, fsutil, cli, brand
│   ├── core/              CONSTITUTION.md, roles.yaml, production-gate.yaml, forgotten-20.yaml, brand.yaml
│   ├── schemas/           JSON Schemas for every .raftly file and record frontmatter
│   └── templates/         docs/, records/, deck/
├── agents/                optional independent reviewers (security, quality, launch); plugin installs only
├── scripts/               repository maintenance: check_release.py, rebrand.py
├── evals/                 evals.json, grade.py, cases/ (claude plugin eval)
├── tests/                 unittest suite + golden files
├── examples/              calculator/, b2b-ai-saas/ (full .raftly + artifacts)
├── legal/                 release-gate.yaml (legal/IP release blockers)
└── docs/                  compatibility, architecture, walkthroughs, licensing, brand clearance, provenance, releasing
```


## Division of labour

- **Claude (via SKILL.md + references)** does judgment: research, product and design decisions, architecture, writing documents and code, choosing what to verify.
- **Scripts** do bookkeeping that must be exact: IDs, links, transitions, schema validation, DAG logic, evidence rules, gate scoring, the learning firewall, rendering, migration. Claude records through scripts so the state stays consistent and honest.

## Key invariants (enforced in code)

| Invariant | Where |
|---|---|
| No VERIFIED/COMPLETE without passing verification evidence; COMPLETE needs the DoD checked | `model.work_transition_problem`, `build_graph.py`, `records.py feature-status`, `checks.validate` |
| No gate PASS/WARNING without evidence ids; blocker N/A only by citing a decision | `gate.set_status_problem` |
| BLUEPRINT_COMPLETE only when the Blueprint Completion Gate passes | `checks.blueprint_gaps`, `state.py stage` |
| LAUNCHED only from LAUNCH_READINESS with readiness READY/READY_WITH_WARNINGS or a logged override | `state.py stage` |
| Type-1 ADRs need a revisit trigger | `checks.validate`, `decisions.py status` |
| Overrides preserve the original recommendation | `decisions.py override` |
| Requirement changes supersede (never overwrite) and compute impact | `records.py change-requirement` |
| No writes into Raftly core from project scripts | `fsutil.assert_not_plugin_core` |
| Atomic writes; paths contained in the project | `fsutil.atomic_write`, `fsutil.resolve_inside` |
| Readiness derived from statuses with documented weights | `gate.score` |

## Why vendored YAML and JSON Schema

The spec requires standard-library scripts with no paid or heavy dependencies. `forgelib/yamlio.py` implements the YAML
subset Raftly writes and humans typically edit (block/flow collections, quoting, block scalars, comments), and refuses
anchors, tags and multi-documents loudly rather than misreading them. `forgelib/schema.py` implements the JSON Schema
keywords our schemas use.

## Context strategy

`SKILL.md` stays under 500 lines with the workflow first (Claude Code re-attaches the first ~5,000 tokens of a skill after
compaction). `raftly context` gives a compact snapshot so Claude doesn't read every `.raftly` file. References load per role or stage.
