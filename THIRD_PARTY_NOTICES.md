# Third-party notices and license inventory

Status: compiled by the implementer on 2026-10-24. **Owner review pending** (see `legal/release-gate.yaml`).

## Bundled third-party code, assets or fonts

**None.** All source code, scripts, schemas, templates, stylesheets, documentation, examples and eval fixtures in this
repository were written for this project. The HTML blueprint and the website (`site/`) use system fonts only and load nothing from third-party servers. The icon artwork is original.

## Runtime requirements (not bundled)

| Component | Use | License | Notes |
|---|---|---|---|
| Python 3.9+ standard library | runs the scripts | Python Software Foundation License | provided by the user's own Python installation |
| Claude Code | host application | Anthropic terms | installed by the user; Raftly is not affiliated with Anthropic |

## Development and CI tools (not distributed with the plugin)

| Tool | Use | License | Notes |
|---|---|---|---|
| ruff 0.6.9 | linting in CI | MIT | installed in CI only |
| actions/checkout, actions/setup-python | GitHub Actions CI | MIT | referenced by `.github/workflows/ci.yml`, not copied |
| actions/configure-pages, actions/upload-pages-artifact, actions/deploy-pages | website deployment | MIT | referenced by `.github/workflows/pages.yml`, not copied |
| Pillow | generated the original icon PNGs during development | MIT-CMU (HPND) | not distributed; the icon artwork is original |
| Google Chrome (headless) | local screenshot check during development | proprietary | not used in CI; not distributed |

## Referenced, not copied

| Material | How it is used |
|---|---|
| Claude Code documentation (code.claude.com) | plugin/skill format, field names and behaviour were verified against it; summarized in our own words in `docs/compatibility.md` |
| JSON Schema (draft 2020-12) | our schemas use its keywords; `skills/raftly/scripts/forgelib/schema.py` is an independent implementation |
| YAML | `skills/raftly/scripts/forgelib/yamlio.py` is an independent implementation of a subset |
| Contributor Covenant 2.1 | linked from `CODE_OF_CONDUCT.md`, not reproduced |
| Marp / Slidev / reveal-md | output-format compatibility only (the deck is plain Markdown); nothing bundled |
| WCAG 2.2, OWASP-style security concepts | cited as general standards in the reference files |
| The `/brag` skill | **not used.** None of its code, text, templates, assets or documentation was read or copied. Raftly only shares the general distribution pattern (public repo → plugin install → slash command), which is a convention, not protected expression |

## Third parties named in examples

The example blueprints (`examples/`) name third-party products (for example Expo, React Native, decimal.js, PostgreSQL,
Auth.js, pg-boss, Stripe, Zoom, Anthropic API) as recommendations inside a fictional product plan, together with their licenses
as researched on the stated date. None of them is bundled or redistributed by this repository.

## Keeping this file current

Whenever a dependency, asset or copied snippet is added, add a row with: source, version, license, copyright notice and the
reason for including it. Prefer permissive licenses, and don't add material whose license is unclear.
