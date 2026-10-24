# Contributing to Raftly

Thanks for helping. Raftly is a product-building operating system for Claude. Contributions should make `/raftly`
more correct, more honest, or simpler, not merely bigger.

## Contribution policy (interim)

**External code contributions are not accepted yet** (owner decision, 2026-10-24). The project is licensed under
Apache-2.0. Before contributions open, the owner will choose contributor terms (a DCO sign-off is the usual fit for
Apache-2.0; see `docs/LICENSING_STRATEGY.md`). Until then, please open issues for bugs, ideas and proposals. Don't send
pull requests with code.

When contributions open, every contributor will need to confirm that they have the right to submit their contribution under
the project's terms, and that it contains no proprietary employer or client code and no third-party material without its license.

## Ground rules

- Read `skills/raftly/core/CONSTITUTION.md`. Changes that weaken evidence rules, honesty about compliance, or the learning firewall will not be accepted.
- No hosted backend, telemetry, or paid dependency. Scripts use the Python standard library (3.9+).
- Keep `skills/raftly/SKILL.md` lean (under 500 lines). Detailed behaviour belongs in `skills/raftly/references/`, linked from SKILL.md.
- Deterministic work belongs in scripts with tests. Judgment belongs in references.

## Development

```bash
git clone <your fork> raftly
cd raftly
python3 -m unittest discover -s tests -t .      # unit + integration tests
python3 scripts/check_release.py                # release checks (manifests, links, secrets, examples)
python3 evals/grade.py --examples     # deterministic eval assertions on shipped examples
claude --plugin-dir .                           # try /raftly locally in Claude Code
claude plugin validate .                        # official manifest validation (if you have the CLI)
```

Optional linting, if you have ruff: `ruff check scripts tests evals`.

## Changing schemas

1. Edit `schemas/*.schema.json` and `skills/raftly/scripts/forgelib/model.py` together (a test keeps them in sync).
2. Bump `SCHEMA_VERSION` in `skills/raftly/scripts/forgelib/__init__.py` when existing projects would no longer validate.
3. Add a migration to `MIGRATIONS` in `skills/raftly/scripts/migrate_schema.py` with tests. Never reinterpret prior decisions silently.
4. Regenerate the examples if needed and run the full test suite.

## Learning proposals from projects

Projects never modify Raftly. `learning.py propose` writes a sanitized proposal into the project. If you submit one as a PR:
it must be generally applicable, contain no private project information, not conflict with the Constitution, and include tests or evals for the new behaviour.

## Pull requests

- Describe the user-visible behaviour change and the evidence (tests, eval results).
- Update `CHANGELOG.md` under `[Unreleased]`.
- CI must pass.
