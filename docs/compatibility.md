# Compatibility decisions (Claude Code plugin format)

The build spec asked us to verify current Claude Code behaviour and record any differences. These checks were made
against the official documentation on **2026-10-24** (code.claude.com/docs: Skills, Plugin manifest reference,
Marketplace reference, Plugin evals).

| Topic | Spec assumption | Verified behaviour | Decision |
|---|---|---|---|
| Skill location | `skills/raftly/SKILL.md` | Plugins auto-discover `skills/<name>/SKILL.md` | Used as specified. No `commands/` directory (docs recommend skills for new plugins). |
| Invocation name | `/raftly` | Plugin skills are namespaced `/plugin-name:skill-name`; the bare `/raftly` also works unless another command uses that name | Plugin name `raftly`, skill name `raftly` → `/raftly` (bare) or `/raftly:raftly`. Documented in the README. |
| `version` in SKILL.md frontmatter | suggested | Not a documented skill field (unknown fields are ignored in Claude Code and are a hard error in other skill surfaces) | Moved to `metadata.version`. `check_release.py` enforces documented fields only. |
| `argument-hint`, `when_to_use`, `license` | — | Documented | Used. `description` + `when_to_use` kept under the 1,536-character listing limit. |
| Paths to scripts | — | `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_SKILL_DIR}` are substituted inside plugin skill content; they are **not** environment variables in Bash | SKILL.md writes commands as `python3 "${CLAUDE_SKILL_DIR}/scripts/engine.py" ...`. `${CLAUDE_SKILL_DIR}` works for plugin skills and standalone skills alike, so the skill is self-contained (see "Self-contained skill" below). |
| Dynamic context injection (`` !`cmd` ``) | — | Runs before the skill loads; a failure or a non-allowed permission check **aborts the whole invocation**; it can be disabled by policy | Not used. The skill's first step is an explicit `raftly context` call, which degrades gracefully. |
| Manifest | minimal `plugin.json` | Only `name` is required; `version` pins updates | `name`, `displayName`, `version`, `description`, `author`, `license`, `keywords`. |
| Distribution | GitHub/plugin source | A repository with `.claude-plugin/marketplace.json` can list itself (`"source": "./"`) | The repo is both the plugin and a one-plugin marketplace: `/plugin marketplace add roszhan2684/raftly`, then `/plugin install raftly@raftly`. No `npx` installer is claimed. |
| Plugin root `CLAUDE.md` | — | Not loaded as context; the validator warns | None shipped. |
| Agents | optional | `agents/*.md` auto-discovered, namespaced `raftly:<name>` | Three independent review agents. Role routing stays in references (spec §48). |
| Evals | `evals/evals.json` | `claude plugin eval` reads case directories (`prompt.md`, `graders/`, optional `case.yaml`) under `evals/`; the skill-creator format `evals/evals.json` is separate, and neither tool reads the other's files | Both shipped: `evals/evals.json` (catalogue + deterministic assertions) and `evals/cases/*` (native suite). |
| Validation | — | `claude plugin validate .` is authoritative | Run it before release (docs/releasing.md). CI runs our own structural checks because the CLI needs credentials and installation. |

Re-check these decisions when Claude Code's plugin format changes, and update this file and `scripts/check_release.py`.

## Self-contained skill (distribution/IP addendum)

Everything `/raftly` needs at runtime lives in `skills/raftly/`: `SKILL.md`, `references/`, `examples/`, `assets/`, `scripts/` (the
engine), `core/` (constitution, roles, gate catalogs, brand), `schemas/` and `templates/`. All paths in skill content use
`${CLAUDE_SKILL_DIR}`, which Claude Code substitutes for both plugin skills and standalone skills. So the same folder works:

| Install method | Status (2026-10-24) | Notes |
|---|---|---|
| Plugin via marketplace: `/plugin marketplace add roszhan2684/raftly` → `/plugin install raftly@raftly` | documented by Claude Code; install tested with the Claude Code CLI (see docs/releasing.md) | includes the optional review agents |
| Local plugin: `claude --plugin-dir <repo>` | documented; not yet tested here (CLI not installed in the build environment) | for development |
| Manual personal skill: copy `skills/raftly` → `~/.claude/skills/raftly` | documented location; engine verified to run from a copied folder | no agents; command is the bare `/raftly` |
| Skills CLI (`npx skills add ...`) | **not documented** by Claude Code; not tested | not mentioned in the README |

Repository-maintenance tools (`scripts/check_release.py`, `scripts/rebrand.py`) stay outside the skill and are not installed.

Note for other skill surfaces (claude.ai uploads, the Skills API): they accept only `name`, `description`, `license`,
`compatibility`, `metadata` and `allowed-tools` in frontmatter. `when_to_use` and `argument-hint` are Claude Code fields. The
skill targets Claude Code; trim those two fields if you package it for another surface.
