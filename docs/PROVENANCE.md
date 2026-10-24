# Provenance and authorship record

Kept to document human authorship and AI assistance accurately (handoff §12). Update it as the project evolves.

## Human direction (repository owner)

- Wrote the product and implementation specification (`ForgeAI_COMPLETE_BUILD_SPEC.md`) and the distribution/IP/legal
  addendum (`ForgeAI_DISTRIBUTION_IP_LEGAL_HANDOFF.md`), dated 2026-10-24. Together they define the product concept, its
  principles, the required capabilities, the repository structure and the release requirements. Place the originals in
  `docs/specs/`.
- Chose to build the project, set its goals and constraints, and will review, select, edit and approve the implementation
  before release.

## AI-assisted implementation

- On 2026-10-24, Claude Code (model `claude-opus-5-5`) generated the initial implementation from those specifications: the
  scripts, schemas, skill and reference text, templates, examples, evals, tests and documentation.
- Purely AI-generated material may not receive the same copyright protection as human-authored expression. The owner's
  selection, arrangement, modification and review are what should be documented. Make substantive human edits in commits
  that show the change (don't squash the history), and keep this file current.

## What was not used

- No code, text, templates, assets or documentation from the `/brag` skill or any other project were copied.
- No proprietary, client or employer code is included.
- External documentation consulted for verification (Claude Code docs, library pages) was summarised, not reproduced. See
  `THIRD_PARTY_NOTICES.md`.

## Record of significant human changes

| Date | Author | Change |
|---|---|---|
| 2026-10-24 | owner | Specifications and addendum (direction, requirements) |
| 2026-10-24 | owner | Decisions: copyright holder (individual), Apache-2.0, no external code yet, rename ForgeAI → Raftly (chosen from screened candidates) |
| | | |
