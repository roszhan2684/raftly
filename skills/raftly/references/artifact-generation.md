# Interactive product blueprint (artifact)

A visual blueprint is a **view** of `.raftly/`, never a competing source of truth.

## Always: the static fallback

`raftly blueprint` renders `artifacts/blueprint.html`: one self-contained file (no network, no external
fonts or scripts). It is responsive, light/dark, and accessible (landmarks, captions, status text never colour-only),
and contains:
overview (blueprint sections, build progress, readiness with no score without evidence) · product
(problem, ICP, requirements) · build graph (SVG dependency map by phase) · features (status + evidence) ·
design (chosen direction, screens) · architecture (overview, stack, dependencies) · decisions (timeline
showing overrides and superseded ADRs) · risks and assumptions · security and production readiness (gate
table, Forgotten-20 summary) · launch.

Brand: if `.raftly/brand/tokens.json` exists (`{"accent": "#hex", "accent_ink": "#hex", "font": "..."}`), the
page uses it.

Re-render after any material state change. A stale blueprint is worse than none.

## When the host supports interactive artifacts

If the current Claude surface offers an artifact or page-publishing tool, you may publish the blueprint
as an interactive artifact as well:
- Build it **from Raftly data**: run `raftly blueprint` (or the `--json` outputs of `raftly state show`,
  `raftly graph phases`, `raftly gate score`, `raftly decisions list`) and render from that. Never type the
  numbers by hand.
- Keep the same sections, honesty rules (no fake metrics, UNVERIFIED shown as such) and accessibility.
- Interactive extras that earn their place: filtering features by status, hovering graph nodes to see
  dependencies and prompts, expanding ADR rationale.
- Respect the host's publishing and privacy rules. A project blueprint may contain confidential product
  information, so keep it private unless the user asks to share it.

If no such tool exists, the static HTML is the deliverable. Never block the project on artifact tooling.

## Visual principles

Professional hierarchy, generous whitespace, one accent colour, status chips with text labels, no
gratuitous animation (respect reduced motion), meaningful empty states ("No risks recorded yet" rather than a blank).
