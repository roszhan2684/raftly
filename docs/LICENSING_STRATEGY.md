# Licensing strategy and IP decision record

> Product and legal-risk planning, **not legal advice**. Final choices should be reviewed by a qualified attorney.
> Status: **License chosen: Apache-2.0** (owner, 2026-10-24). Counsel review recommended. Tracked in `legal/release-gate.yaml`.

## Why there is no license yet

The owner wants Raftly to be (1) public, free and easy to use, and (2) protected against people taking it, rebranding it
and selling it. Read literally, these goals conflict: every license recognised as "open source" permits copying,
modification, redistribution and commercial use. So the LICENSE file currently grants nothing, and the owner chooses
consciously between the paths below. MIT was deliberately not chosen by default.

## What each tool can and cannot do

| Tool | Protects | Does not protect |
|---|---|---|
| Copyright (automatic) | the exact source code, documentation, skill text, templates, original artwork | the idea of an AI product-building skill, workflows, methods, architecture patterns, functionality, the name, the `/raftly` command |
| License terms | what others may do with *this* code and docs | independent re-implementations |
| Trademark | the brand (name, logo) for specified goods/services, once cleared and used or registered | the code; anything if the name is not distinctive or clear |
| Patent | a genuinely novel, non-obvious technical invention, if filed in time | ideas, business methods or prompt workflows as such |
| Trade secret | only material kept confidential | anything published in a public repository |

No license or registration makes public software impossible to copy. The realistic goal is clear ownership, clear permissions,
evidence of authorship, and a brand that is hard to impersonate.

## Options

| Option | Example licenses | Adoption | Control | Is it "open source"? |
|---|---|---|---|---|
| A. Open source | Apache-2.0 (explicit patent grant, notice preservation), MIT, MPL-2.0, GPL-3.0, AGPL-3.0 | highest | low: forks and commercial use allowed; protect the brand via trademark | yes |
| B. Source-available | PolyForm Shield 1.0.0, PolyForm Noncommercial 1.0.0, PolyForm Small Business 1.0.0, Elastic License 2.0, Business Source License 1.1, Functional Source License 1.1 | medium | medium-high: free use allowed, competing or commercial redistribution restricted | **no** (must not be marketed as open source) |
| C. All rights reserved | (no license) | low: users can't be sure they may install or copy it | highest | no |
| D. Dual license | e.g. a community license (B) + a paid commercial license | medium | high | depends on the community license |

Short descriptions of the source-available candidates (verify the current official texts before choosing):
- **PolyForm Shield 1.0.0**: broad permission to use, modify and distribute, except to provide a product that competes with the software.
- **PolyForm Noncommercial 1.0.0**: noncommercial use only (this would block professional teams from using Raftly at work, likely too narrow for the goal).
- **PolyForm Small Business 1.0.0**: free for small businesses below a size threshold; others need a commercial license.
- **Elastic License 2.0**: use and modify, but no providing it as a managed service, no circumventing license-key features, no removing notices.
- **Business Source License 1.1**: source-available with an "additional use grant"; converts to a named open-source license after a change date.
- **Functional Source License 1.1**: permits everything except competing commercial use; each release converts to Apache-2.0 or MIT after two years.

Standardised licenses (PolyForm, FSL, ELv2, BSL) are preferable to a custom-drafted license: they're familiar to developers
and lawyers, and they have been reviewed publicly.

## Implementer recommendation (for discussion with counsel)

Two realistic paths, matching the handoff document §14:

1. **Growth-first:** Apache-2.0, plus a trademark strategy (clear a distinctive name, then file) and a `TRADEMARK_POLICY.md`.
   Forks are legal, but they can't use the brand or imply affiliation. Best for community adoption.
2. **Control-first:** Functional Source License 1.1 (Apache-2.0 future grant) or PolyForm Shield 1.0.0. Anyone can install and use
   Raftly for free, including at work. Rebranding it as a competing product is not permitted. Optionally add a commercial license later (dual licensing).

If the main fear is "someone takes Raftly, renames it and sells it", path 2 addresses that in the license, while path 1 addresses
it only through the brand. Either way, **brand clearance comes first** (see `docs/BRAND_CLEARANCE.md`), because neither path
protects a name that can't be cleared.

## Contributor policy (needed before accepting external pull requests)

| Option | Effect | Friction | Fits |
|---|---|---|---|
| Not accepting external code yet | ownership stays simple; issues and discussion still welcome | none | now, until the license is chosen |
| DCO (Signed-off-by) | contributors certify they have the right to submit under the project license | low | path 1 |
| CLA (license grant to the owner) | owner can relicense or dual-license contributions | medium | path 2 / dual licensing |
| Copyright assignment | strongest central ownership | high | rarely needed |

Current interim policy (CONTRIBUTING.md): external code contributions are not accepted until this decision is made.

## Trademark symbols

- `TM` may be used to claim an unregistered mark where appropriate, once the name is chosen.
- **Never use the registered-trademark symbol (R in a circle)** unless the mark is federally registered for the relevant goods/services. A pending application does not qualify. `scripts/check_release.py` fails if that symbol appears anywhere in the repository.

## README legal statement (adapt after the decisions)

> Raftly source code and original documentation are protected by applicable copyright law and are licensed only under the
> terms in this repository's LICENSE file. Raftly and related branding may be protected separately under trademark law. The
> source-code license does not grant rights to imply endorsement or official affiliation except as expressly stated.
> Third-party components remain subject to their respective licenses.

## Decision log

| Decision | Status | Chosen | Date | Reviewed by counsel |
|---|---|---|---|---|
| Copyright holder (individual / company) | DECIDED (name pending) | the owner, as an individual | 2026-10-24 | — |
| License model and license | DECIDED | open source, Apache-2.0 (growth-first) | 2026-10-24 | recommended |
| Contributor policy | DECIDED (interim) | no external code yet; DCO likely when contributions open | 2026-10-24 | — |
| Brand (keep "ForgeAI" or rename) | DECIDED: renamed | **Raftly** (preliminary screen; attorney clearance pending) | 2026-10-24 | before filing |
| Trademark filing | NOT STARTED | — | — | — |
| Copyright registration | NOT STARTED | — | — | — |
| Patent consultation | NOT STARTED (only if a genuinely novel technical invention is identified) | — | — | — |
