# Examples

Full Raftly outputs you can open, validate and re-render. Each one is a real `.raftly/` directory produced with the Raftly scripts,
plus `artifacts/` (HTML blueprint and deck source).

| Example | Prompt | Shows |
|---|---|---|
| [calculator](calculator/) | "I want to build a calculator mobile app and website." | Simplicity: client-only, 16 of 45 production checks apply, three real design directions, calculator semantics, a project-only learning |
| [b2b-ai-saas](b2b-ai-saas/) | "Build a B2B AI sales coaching platform that ingests sales calls…" | Multi-tenancy, RBAC, AI evals, billing, compliance readiness, GTM, open founder decision |

Other scenarios (healthcare, broken-repo recovery, Firebase migration, launch gate, requirement change, override,
preference, resume) are defined as runnable evals in [../evals](../evals/README.md), with fixtures in `evals/cases/*/`.

```bash
cd examples/calculator
python3 ../../skills/raftly/scripts/engine.py context            # what Raftly sees on resume
python3 ../../skills/raftly/scripts/engine.py validate           # integrity
python3 ../../skills/raftly/scripts/engine.py graph next         # next unblocked node
python3 ../../skills/raftly/scripts/engine.py blueprint          # re-render artifacts/blueprint.html
```

Note: research marked **Not verified** in these examples was not re-checked at authoring time and must be verified before it is relied on.
