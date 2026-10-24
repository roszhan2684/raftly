# Brand clearance: Raftly (formerly "ForgeAI")

> Research notes by the implementer, **not legal clearance and not legal advice**. A U.S. trademark attorney should perform
> or confirm clearance before filing or making a major brand investment.

**Status: name chosen, NOT YET CLEARED. Release blocker.**

| | |
|---|---|
| Chosen name | **Raftly** (command `/raftly`, plugin `raftly`, repo `raftly`, project folder `.raftly/`) |
| Chosen by | the owner, 2026-10-24, after three screening rounds (below) |
| Previous working name | ForgeAI (abandoned: crowded in AI software, see "Findings") |
| Applied with | `scripts/rebrand.py` (older `.forge/` project folders are still read and are moved by `raftly migrate`) |
| Brand config | `skills/raftly/core/brand.yaml` (status PROVISIONAL until clearance) |

### Raftly: known risks and next steps

- **Nearest existing name: RaftLabs**, an "AI-first software development and growth marketing company" (custom apps, MVPs,
  voice AI; Wilmington, Delaware per its Clutch profile). It shares the root "Raft" and works in a related field (software
  services vs a developer tool). Also seen: RaftWorks (a product studio). Ask counsel to weigh this specifically.
- The GitHub account `raftly` is **taken**: use a different owner account or organisation for the repository (the repository lives at `roszhan2684/raftly`).
- `raftly.com` is **registered** by someone else. `raftly.dev`, `raftly.io` and `raftly.ai` were unregistered on 2026-10-24.
  Register the ones you want now.
- npm `raftly` and PyPI `raftly` were free on 2026-10-24. Consider reserving them only if you'll publish there (placeholder
  packages can violate registry policies; check them first).
- USPTO / state / common-law searches for RAFTLY and similar marks (RAFT, RAFTLY, RAFT LABS) in Classes 9 and 42: **not done**. Attorney task.

## Findings for the previous name "ForgeAI" (web research, 2026-10-24)

| Where | Finding | Relevance |
|---|---|---|
| forgeai.com | Active company "ForgeAI": a "semantic control layer for enterprise AI" covering agent orchestration, governance, audit trails and human review. Footer: "© 2022–2026 ForgeAI.com · all rights reserved". No trademark symbols shown. Profiled on Village.ai as London-based. | **High.** Same name, AI software, overlapping themes (governance, deterministic checks, agent orchestration) and plausibly overlapping customers (developers and engineering teams). |
| docs.foji.io | "ForgeAI" by FojiSoft: a no-code AI/ML platform. | Medium: same name, AI software. |
| g2.com / metaschool.so | "ForgeAI": an AI-agent builder for business operations, with API/SDK. | Medium-high: same name, AI agents, developer API. |
| Product Hunt / Capterra | "Forge AI": SMB sales and marketing automation with an AI phone agent. | Medium: same sound, AI software. |
| craft.co | "Forge.AI" (Cambridge, MA, founded 2017): the ANVIL intelligence platform. | Low-medium. |
| USPTO (via news syndication) | An application for **FORGE** (filed 2025-03-06) was published for opposition. Its goods/services were not confirmed. | Medium: "Forge" is a crowded root mark; check classes. |
| USPTO, per the owner's handoff document | A standard-character **FORGEAI** application reportedly filed 2026-10-02 for AI server hardware/software. | **Not independently verified** by the implementer (the USPTO search tools could not be queried here). Verify in USPTO trademark search / TSDR. |
| GitHub | The account `forgeai` exists; 522 repositories contain "forgeai" in the name (e.g. `forgeai-dev/ForgeAI`). | Repository naming and confusion risk; not legal priority by itself. |
| npm / PyPI | `forgeai` unclaimed on both; `forge-ai` taken on both. | Package-name availability only. |
| VS Code Marketplace | No extension found for "forgeai". | Low. |
| Claude Code plugin ecosystem | A community skill `plugin-forge` (softaworks/agent-toolkit) exists. Built-in skills named `forge` were not found. | `/forge` may collide with other installed skills; Claude Code namespacing (`/forgeai:forge`) mitigates collisions technically, not legally. |
| Minecraft "ForgeAI" mentioned in the handoff | Not found in this search (many AI mods exist for the Minecraft *Forge* mod loader, which itself makes "Forge" crowded in developer tooling). | Low-medium. |

Sources: forgeai.com; docs.foji.io/wiki/Category:ForgeAI; g2.com/products/forgeai; metaschool.so/ai-agents/forgeai;
village.ai/company/forge-ai; hunted.space/product/forge-ai; capterra.co.uk (FORGE AI); craft.co/forge-ai; htsyndication.com
(USPTO publishes trademark "FORGE" for opposition); skillselion.com (plugin-forge); registry.npmjs.org; pypi.org; api.github.com.

## Implementer assessment (non-legal)

"ForgeAI" is a **crowded name in AI software**, with at least one active company (forgeai.com) in a closely related space. The
likelihood-of-confusion factors (similar mark, related goods/services, overlapping channels) point toward material risk.
Recommendation: **plan to rename before any branded public launch** unless counsel concludes otherwise. Choose a distinctive,
non-descriptive name (coined words clear more easily than "AI"/"Forge"/"Build" combinations), then repeat this search for it.

## Replacement candidates (screened 2026-10-24)

Coined names built from building-craft words (the product builds the *foundation and structure* of a product). Screening
method: exact-term web search; npm and PyPI registry lookups; GitHub account lookup and repository-name search; `.com` and
`.io`/`.ai` WHOIS; `.dev` RDAP (Google Registry). Thirty-nine candidates were screened. Most coined `.com` domains were already
registered (for example keelmark, ordvane, kavrel, vellumark, arbitect, stonewright, quillwright, archwyn), and several had
existing GitHub accounts or packages (keelmark, tolvane, kavrel, quorvex, mortisan, corbelia, keelwright, ateliera).

| Name | Meaning | Web (exact term) | npm | PyPI | GitHub account | GitHub repos named | .com | .dev | .io | .ai |
|---|---|---|---|---|---|---|---|---|---|---|
| **Trellisan** | trellis (the frame that guides growth) + artisan | no results | free | free | free | 0 | unregistered | unregistered | unregistered | unregistered |
| **Plinthory** | plinth (the base a structure stands on) | no results | free | free | free | 0 | unregistered | unregistered | unregistered | unregistered |
| **Quoinwright** | quoin (cornerstone) + wright (maker); said "coin-wright" | no results | free | free | free | 0 | unregistered | unregistered | unregistered | unregistered |
| **Ashlarix** | ashlar (precisely dressed building stone) | no results | free | free | free | 0 | unregistered | unregistered | unregistered | unregistered |

Also clean on the registry/GitHub/.com checks but not shortlisted: lintelry, mullionix, purlinary, corbelwright, soffitly.

These results show only that the screened sources showed no use **on that date**. They are not a trademark search: the USPTO
database, state registrations and common-law use were **not** searched. Register the domains and handles you choose promptly,
and have counsel run a full search before filing or launching.

### Round 2: easy to pronounce (owner request)

Clean on the same checks: **Tolvenna** ("tol-VEN-uh"), **Belvenna**, **Joistwell**, **Plinthwell** (near "PlumbWell", a plumbing
company). Thirty-plus more were screened; most had a registered `.com` or an existing GitHub account.

### Round 3: five or six letters (owner request)

Real English words of this length (joist, plinth, lintel, gable, quoin, dowel, tenon, purlin, corbel, soffit, ashlar, trowel,
mortar, rafter) are taken almost everywhere: npm/PyPI names, GitHub accounts, and `.com`/`.dev`/`.io`/`.ai`. So at this length the
realistic bar is: no software/AI product with that name, free npm/PyPI names, and a free `.dev`/`.io`/`.ai`. The `.com` would need to be
bought from its holder (or use a variant such as `get<name>.com`).

| Name | Said | Meaning | npm | PyPI | GitHub account | Repos named | .com | .dev | .io | .ai | Nearest existing name |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Hewly** | HEW-lee | to hew = shape by cutting (craftsmanship) | free | free | free | 0 | registered (looks parked) | free | free | free | Hyly.AI (property software; different spelling) |
| Struta | STROO-tuh | strut = structural support | free | free | free | 18 | registered (looks parked) | free | free | free | Strata Identity, Struto (similar sound) |
| Raftly | RAFT-lee | raft = a building foundation | free | free | taken | 4 | registered | free | free | free | RaftLabs (AI/software agency, similar root) |
| Hingly | HING-lee | hinge = what lets things move | free | free | taken | 5 | registered | free | free | free | Hinge (dating app; well-known brand) |
| Kilny | KIL-nee | kiln | free | free | free | 6 | registered | free | free | free | **Kiln AI** (AI dev tool): rejected |

## Clearance checklist (Raftly)

- [ ] USPTO search: RAFTLY, RAFT LY, RAFT, RAFTLABS and confusingly similar spellings/sounds, in software/AI/developer-tool classes (e.g. Classes 9 and 42)
- [ ] Counsel's view on RaftLabs (similar root, related field)
- [ ] State registrations and common-law use (web, company registries)
- [ ] GitHub, npm, PyPI, VS Code Marketplace, Claude plugin/skills listings, app stores
- [ ] Register domains (raftly.dev / .io / .ai were free on 2026-10-24) and a GitHub organisation
- [ ] Attorney clearance opinion before filing or a major brand investment
- [ ] Decision recorded in `legal/release-gate.yaml` (`brand_clearance.status`) and in `docs/LICENSING_STRATEGY.md`

A GitHub username or domain alone is **not** legal clearance.

## Rename plan (technical)

The brand is centralised in `skills/raftly/core/brand.yaml`. This is how ForgeAI → Raftly was done. To rename again:

```bash
python3 scripts/rebrand.py --display-name "NewName" --plugin-name newname --skill-command newcmd            # dry run
python3 scripts/rebrand.py --display-name "NewName" --plugin-name newname --skill-command newcmd --apply --replace-text
python3 -m unittest discover -s tests -t . && python3 scripts/check_release.py
```

This updates the manifests, SKILL.md `name` and the skill directory, and the human-facing docs. It leaves the history alone
(CHANGELOG, this file, example `.forge/` state).

The rename also moves the project folder (`.raftly/` → `.<new>/`). The old folder name is added to `legacy_state_dirs`, so
existing projects keep loading and `<command> migrate` moves them. Brand-neutral internals never change: `scripts/engine.py`,
the `engine:` block in `state.yaml`, the `forgelib` package name (internal only) and the role ids.
