# Raftly evals

Three layers:

| Layer | What | Cost | Runs in CI |
|---|---|---|---|
| `evals.json` | Scenario catalogue: prompt, expected behaviour, deterministic structural assertions | — | yes (via the grader on the examples) |
| `grade.py` | Deterministic grader for a `.raftly/` directory | free | yes: `python3 evals/grade.py --examples` |
| `cases/` | Native [Claude Code plugin evaluation](https://code.claude.com/docs/en/plugin-evals) suite: real `/raftly` runs graded by tool-use, file regex and LLM rubrics | model usage | no (needs Claude credentials) |

## Run the live suite

Use Claude Code's plugin evaluation runner ([docs](https://code.claude.com/docs/en/plugin-evals)) from the repository root, which is the plugin root:

- pass `--scaffold` so the existing-repo cases are seeded from their fixtures and examples;
- pass `--case 01-calculator` to run one case.

The cases need write and Bash tools (they create `.raftly/` and run `engine.py`). Grant them as described in the
plugin evaluation docs ("Grant tools"). Each case also has a deterministic counterpart in `evals.json`. After a live run you can
grade the produced workspace:

```bash
python3 evals/grade.py --scenario calculator --root <workspace>
python3 evals/grade.py --scenario recovery --root <workspace> --fixture evals/cases/04-recovery-broken-repo/fixture
```

`results/` directories written by the runner are gitignored.

## Scenarios

1. Calculator (simplicity) · 2. B2B AI SaaS · 3. Healthcare (PHI, readiness language) · 4. Broken repo (RECOVERY) ·
5. Unnecessary blockchain · 6. Preference stays project-only · 7. Firebase → Postgres migration · 8. Launch gate ·
9. UI component choice · 10. Requirement change (pricing) · 11. Resume (Demo C) · 12. Founder override (Demo D).
