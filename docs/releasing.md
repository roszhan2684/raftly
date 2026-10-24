# Releasing Raftly

## Checklist (spec §61, §72)

1. `python3 -m unittest discover -s tests -t .` passes.
2. `python3 scripts/check_release.py` passes (manifests, frontmatter, links, secrets, local paths, examples, versions).
3. `python3 evals/grade.py --examples` passes.
4. `claude plugin validate .` reports "Validation passed" (run locally; requires the Claude Code CLI).
5. Live evals (optional but recommended): `claude plugin eval . --scaffold`.
6. Clean-install test:
   ```bash
   git clone <repo> /tmp/raftly-clean && cd /tmp/raftly-clean && python3 scripts/check_release.py
   mkdir /tmp/raftly-demo && cd /tmp/raftly-demo && claude --plugin-dir /tmp/raftly-clean
   # in Claude Code: /raftly I want to build a calculator mobile app and website.
   ```
   Then confirm `/raftly` resumes after restarting Claude Code (Demo C), and that the override (Demo D), preference (Demo E) and `/raftly launch` (Demo F) behave as described in the evals.
7. Marketplace install test from GitHub: `/plugin marketplace add roszhan2684/raftly` → `/plugin install raftly@raftly` → `/raftly`.
8. Update `CHANGELOG.md`; bump the version in `.claude-plugin/plugin.json`, `skills/raftly/scripts/forgelib/__init__.py` and `skills/raftly/SKILL.md` (`metadata.version`) together.
9. Tag: `git tag v0.1.0 && git push origin main --tags`, then create a GitHub release with the changelog section.

## Versioning

The plugin follows semver. Project state carries `engine.schema_version`. Bump it only with a migration in
`skills/raftly/scripts/migrate_schema.py` and tests. Users get updates through `/plugin` (the manifest `version` pins installs until it changes).

## Legal / IP release checklist (distribution/IP/legal handoff §27)

`python3 scripts/check_release.py --release` enforces the machine-checkable items via `legal/release-gate.yaml`. Don't publish
until it passes **and** every box below is ticked:

- [ ] Legal owner (copyright holder) identified; `legal_owner` set; placeholders in `LICENSE` and `NOTICE` replaced
- [ ] Copyright notice added (`NOTICE`, README legal section)
- [ ] Final license consciously selected (`docs/LICENSING_STRATEGY.md`) and its full official text in `LICENSE`
- [ ] The license model matches the wording everywhere (never call a source-available license "open source")
- [ ] No accidental MIT/Apache license if the owner wants resale/rebranding restrictions
- [ ] `THIRD_PARTY_NOTICES.md` reviewed by the owner (`third_party_review.owner_reviewed: true`)
- [ ] Nothing copied from `/brag` or other projects beyond their license terms (`docs/PROVENANCE.md`)
- [ ] Git history retained (no squashing away the authorship record)
- [ ] No employer/client/proprietary code; no private project data
- [ ] Brand clearance performed (`docs/BRAND_CLEARANCE.md`); "Raftly" conflict assessed; rename via `scripts/rebrand.py` if needed
- [ ] Trademark attorney consultation considered before filing
- [ ] No registered-trademark symbol unless a registration exists (enforced by `check_release.py`)
- [ ] Contributor policy set (`contributor_policy`) and reflected in `CONTRIBUTING.md`; `CLA.md` added if a CLA is chosen
- [ ] `SECURITY.md` present; README privacy claims accurate (no backend, no telemetry)
- [ ] Copyright registration considered (`docs/IP_REGISTRATION_CHECKLIST.md`)
- [ ] Patent consultation considered only if counsel identifies a genuinely novel technical invention

## Install verification (handoff §4, §34)

Record the results in `legal/release-gate.yaml` → `install_verified` (with the Claude Code version and the date):

1. `claude plugin validate .` → "Validation passed" → `plugin_validate: true`
2. From GitHub: `/plugin marketplace add roszhan2684/raftly` → `/plugin install <plugin>@<marketplace>` → `/raftly` works in a fresh project → `marketplace_install: true`
3. Manual: `cp -R skills/raftly ~/.claude/skills/raftly` → `/raftly` works → `manual_skill_copy: true`
4. Only document a skills-CLI command (e.g. `npx skills add ...`) after it has been tested; it isn't documented in Claude Code's docs as of 2026-10-24.
