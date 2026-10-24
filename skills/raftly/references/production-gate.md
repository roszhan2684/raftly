# Production gate, readiness scoring, Forgotten 20%

Role: **Launch Director** (`launch-director`), synthesising security, SRE, QA, privacy and product.

## Catalog and applicability

The checks live in `core/production-gate.yaml` (45 checks) and `core/forgotten-20.yaml` (29 checks).
Each has an `applies_when` rule evaluated against `state.yaml` `project.profile`. `raftly gate init` creates
`.raftly/gate.yaml` with applicable checks as UNVERIFIED and the rest as **NOT_APPLICABLE**, with the reason.
A simple calculator is never penalised for lacking Kubernetes or a database: N/A is valid.

Re-run `raftly gate init` after profile changes. Recorded statuses and evidence are preserved.
Add product-specific checks with `raftly gate add --id G-CUSTOM-... --title ... --category ... --severity major`.

## Statuses

PASS · WARNING · FAIL · UNVERIFIED · NOT_APPLICABLE.
- **PASS/WARNING require evidence ids** (`--evidence EV-003`). No evidence means no PASS. PASS on failing evidence is refused.
- A blocker can only be set NOT_APPLICABLE by citing a decision: `--na-reason "decision: ADR-001 client-only, no server"`.
- UNVERIFIED is honest and better than a guess.

## Readiness scoring (deterministic: `raftly gate score`)

- Weights: blocker 3, major 2, minor 1. Values: PASS 1.0, WARNING 0.5, FAIL 0. UNVERIFIED and N/A are excluded from the score.
- **coverage** = verified weight / applicable weight (verified = PASS/WARNING/FAIL).
- **score** = Σ(weight × value) / verified weight. It is shown only when coverage ≥ 60%; otherwise it reads "UNVERIFIED".
- **Readiness**:
  - `NOT_READY`: any blocker FAIL.
  - `INSUFFICIENT_EVIDENCE`: coverage < 60% or any blocker UNVERIFIED.
  - `READY_WITH_WARNINGS`: no blocker FAIL/UNVERIFIED, but some WARNING/FAIL/UNVERIFIED remains.
  - `READY`: every applicable check PASS.
- Completeness (how much is built) and quality (how well it is verified) are reported separately: build
  progress comes from the graph, readiness from the gate.

## `/raftly launch` procedure

1. `raftly context`; `raftly gate init` (refresh).
2. For each applicable check, find or produce **real** evidence: run the test suite, audit dependencies
   (`npm audit` / `pip-audit`), check headers on the deployed URL, perform the restore drill, review the
   legal pages, run the accessibility pass. Record each with `raftly evidence record --subject G-... ...`
   (or against the feature/test entity), then `raftly gate set G-... PASS|WARNING|FAIL --evidence EV-...`.
3. Things you can't verify from here (store review status, professional legal review): leave UNVERIFIED and
   list what is needed.
4. Forgotten-20 audit: `raftly gate report --group forgotten-20`. Walk each applicable item the same way.
5. `raftly gate report --write` (updates LAUNCH.md and `state.production`). Then fill LAUNCH.md: launch plan,
   rollback, owners, support path, remaining risks.
6. If the founder wants to launch at NOT_READY or INSUFFICIENT_EVIDENCE: record a FOUNDER ADR accepting the
   specific risks, then `raftly state stage LAUNCHED --override-reason "..."`. The override is logged; blockers
   stay visible.
7. Launch deck (presentation-generation.md).

## Independent review

For high-stakes launches, run the `raftly-launch-reviewer` (and `raftly-security-reviewer`) agents for an
independent pass over the gate evidence before declaring readiness.
