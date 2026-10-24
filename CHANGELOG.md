# Changelog

All notable changes to ForgeAI are documented here. The project follows [Semantic Versioning](https://semver.org/).
Project state files carry their own `schema_version`. Schema changes ship with a migration in `skills/forge/scripts/migrate_schema.py`.

## [Unreleased]

## [0.1.0] - 2026-10-24

First public release, published at the owner's request while attorney brand clearance is still pending (see
`legal/release-gate.yaml`).

### Release
- Repository: github.com/roszhan2684/raftly (also its own plugin marketplace: `/plugin marketplace add roszhan2684/raftly`).
- Marketing and docs website on GitHub Pages (`site/`, deployed by `.github/workflows/pages.yml`), with privacy and terms pages.
- Listing icon and directory metadata (homepage, repository, docs, support, privacy, terms URLs) in `plugin.json`.
- `claude plugin validate --strict .` passes on Claude Code 2.1.310. A local-marketplace install was verified in an isolated config.
- Copyright: Roszhan Raj Meenakshi Sundhresan. License: Apache-2.0.

### Renamed (2026-10-24)
- **ForgeAI → Raftly.** The owner chose to rename after the brand screen found "ForgeAI"/"Forge AI" crowded in AI software.
  Plugin `raftly`, skill `/raftly` (namespaced `/raftly:raftly`), project folder `.raftly/` (older `.forge/` folders are still
  read and are moved by `raftly migrate`), agents `raftly-*-reviewer`. The engine entry point is now the brand-neutral
  `scripts/engine.py`, and the state block is now `engine:`. Done with `scripts/rebrand.py`; see docs/BRAND_CLEARANCE.md.

Initial version. **Not yet publicly released.** Blocked on the owner's decisions about license, copyright holder, brand
clearance and contributor policy (`legal/release-gate.yaml`).

### Changed (distribution/IP addendum)
- `skills/raftly/` is now self-contained (engine scripts, core catalogs, schemas, templates), so the skill works as a plugin
  or copied as a personal skill. Repository-maintenance tools stay in top-level `scripts/`.
- The MIT license was withdrawn before release; the owner then chose Apache-2.0 (2026-10-24). LICENSE holds the verbatim
  Apache-2.0 text and NOTICE holds the copyright line (holder name pending).
- Brand identifiers are centralised in `skills/raftly/core/brand.yaml`, with a `scripts/rebrand.py` maintainer tool.
- JSON Schema `$id`s are relative (no domain the project doesn't own).

### Added (distribution/IP addendum)
- `NOTICE`, `THIRD_PARTY_NOTICES.md`, `legal/release-gate.yaml`, `docs/LICENSING_STRATEGY.md`, `docs/BRAND_CLEARANCE.md`,
  `docs/IP_REGISTRATION_CHECKLIST.md`, `docs/PROVENANCE.md`, `docs/specs/`.
- `check_release.py --release` enforces the legal/IP release blockers, refuses the registered-trademark symbol, and refuses an open-source license
  text before a license decision is recorded.

### Added
- Claude Code plugin `raftly` with the `/raftly` skill (bare `/raftly`, or the namespaced `/raftly:raftly`).
- Forge Constitution (`skills/forge/core/CONSTITUTION.md`), 22-role senior role registry, production-gate (45 checks) and Forgotten-20% (29 checks) catalogues with profile-based applicability.
- Progressive-disclosure reference library (26 files) covering workflow, modes, decision authority, research, roles, product, UX/design, architecture, frontend, mobile, backend, data, AI, security, privacy/compliance, platform/SRE, QA, GTM, Definition of Done, evidence graph, learning, production gate, documents, artifact and presentation generation, schemas.
- Deterministic project engine (Python standard library only): `engine.py` (context, doctor, dispatcher), `init_project.py`, `inspect_repo.py`, `state.py`, `validate_project.py`, `build_graph.py`, `evidence.py`, `records.py` (incl. the Requirement Change Engine), `decisions.py` (ADRs, founder overrides, Decision Book), `gate.py`, `learning.py` (Learning Firewall), `render_blueprint.py`, `render_deck.py`, `generate_handoff.py`, `migrate_schema.py`, `check_release.py`.
- Vendored YAML-subset reader/writer and JSON Schema validator. 15 JSON schemas for `.forge/` files.
- Evidence-gated statuses: VERIFIED/COMPLETE and gate PASS require recorded passing evidence.
- Document, record and deck templates.
- Three optional independent review agents (security, quality, launch).
- Examples: Calculator (client-only utility) and SalesLens (multi-tenant B2B AI SaaS), each with a full `.forge/` blueprint, rendered HTML blueprint and deck source.
- Evals: `evals/evals.json` (12 scenarios), deterministic grader, and a native Claude Code plugin evaluation suite with scaffolded fixtures.
- Unit and integration tests (`unittest`), GitHub Actions CI with no API keys.
