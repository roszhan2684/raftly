# Project learning and the Learning Firewall

Raftly learns from work without poisoning itself (Constitution 18–21).

## Three levels

| Level | Where | Who writes | Changes Raftly behaviour? |
|---|---|---|---|
| **L1 Project memory** | `.raftly/learnings/L-xxx.md` | Raftly, immediately | only for this project |
| **L2 Pattern candidates** | `.raftly/learning-candidates/LC-xxx.md` | Raftly, when the firewall allows | no; collects evidence |
| **L3 Raftly core** | the Raftly repository | **maintainers only**, via reviewed PR | yes, for everyone, after review |

Raftly **never** modifies the installed plugin. The scripts refuse writes into Raftly core directories.
Core changes are sanitized **proposals** a human may submit as a pull request.

## What to capture (L1)

decisions and their outcomes · user overrides · failures and their causes · validated patterns ·
preferences · implementation findings ("the precision bug came from binary floats").

## Firewall classification

`raftly learning record --title "..." --kind <kind> [flags]` classifies deterministically and stores the result.
Choose the flags honestly:

| Flag | Meaning |
|---|---|
| `--kind` | preference · local_fact · implementation_finding · engineering_failure · pattern · outcome · override |
| `--quality` | none · anecdotal · observed · reproduced · tested |
| `--authority` | none · user · project · community · official_docs · standard |
| `--repeats N` | how many independent times this was observed |
| `--cross-project` | plausibly applies beyond this product/domain |
| `--objective` | verifiable by tests/measurement, not taste |
| `--contradicted` | credible evidence points the other way |
| `--private` | the observation contains project-specific detail |

Outcomes:
- **REJECT**: no evidence and no authority. Not stored.
- **PROJECT_ONLY**: preferences, overrides, local facts, subjective or single-project findings.
- **CANDIDATE**: objective, cross-project, with some evidence. Collect more.
- **CORE_PROPOSAL**: tested, repeated or authoritatively sourced, cross-project, uncontradicted, sanitized.

Examples:
- "I hate rounded buttons." → `--kind preference --quality anecdotal --authority user` → **PROJECT_ONLY**.
  Apply it to this project's design tokens. Never generalise it.
- "Binary floating point produced 0.30000000000000004 in the calculator; decimal arithmetic fixed it;
  tests prove it; language docs explain it." → `--kind engineering_failure --quality tested
  --authority official_docs --cross-project --objective` → **CORE_PROPOSAL** (if no private detail).
- "Users in this beta liked dark mode." → `--kind outcome --quality observed --authority project` → PROJECT_ONLY.

## Proposing a core change

`raftly learning propose LC-00x --pattern "<generic statement>" --rule "<proposed Raftly rule>" --source <url>`
- Refuses text that contains the project name, paths, emails, private URLs, IPs or secret-like strings.
- Writes `.raftly/learning-candidates/proposals/...md` with a maintainer checklist (general applicability,
  no private info, no constitution conflict, tests/evals added, maintainer review).
- Nothing is sent anywhere. The user decides whether to open a PR against the Raftly repository.

## Using learnings

At the start of relevant work, check `raftly learning list` for project learnings that apply (e.g. design
preferences before UI work). Respect them in this project, and mention them only when they change a decision.
