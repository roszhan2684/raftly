# Presentation generation

Two decks: a **Product Blueprint Deck** after BLUEPRINT COMPLETE, and an optional **Launch Deck** near release.
Content comes from `.raftly/` documents. Missing content is labelled, never invented.

## Choosing the output

1. If the host offers a slide-deck tool, artifact type or presentation skill (for example a `.pptx` skill
   or a slides artifact), use it, feeding it the content below. Don't produce a file format the user
   didn't ask for when a native deck type exists.
2. Otherwise run `raftly deck` (blueprint) or `raftly deck --kind launch`. This writes Marp-compatible Markdown with
   speaker notes to `artifacts/deck.md` / `artifacts/launch-deck.md`. It renders with Marp,
   Slidev or reveal-md, and reads fine as plain Markdown.
3. Then edit the generated source for flow and clarity. Keep facts tied to Raftly state.

## Product Blueprint Deck (12 slides)

1. Product vision · 2. Problem · 3. ICP/user · 4. Existing workflow and pain · 5. Proposed solution (V1 + exclusions) ·
6. Core user experience · 7. Screens and design direction (options → choice) · 8. Architecture (simplest viable;
Type-1 decisions) · 9. Build plan (dependency phases, not dates) · 10. Security/compliance (readiness language) ·
11. Business/GTM · 12. Launch plan and risks (top risks, untested assumptions, kill criteria).

## Launch Deck (12 slides)

1. Product · 2. Customer problem · 3. Final solution · 4. Demo/screens · 5. Capabilities (feature status) ·
6. Architecture · 7. Reliability/security · 8. Metrics/evidence (only recorded evidence) · 9. Production
readiness (gate result; UNVERIFIED shown honestly) · 10. Launch strategy · 11. Remaining risks · 12. Next phase.

## Slide rules (spec §58)

One message per slide. No walls of text (≤ 5 bullets, ≤ ~12 words each). Diagrams and screens over prose
(the build graph and the architecture diagram). Label assumptions as assumptions. Consistent branding: use
`.raftly/brand/tokens.json` or DESIGN_SYSTEM.md tokens. Speaker notes carry the detail. Templates:
`${CLAUDE_SKILL_DIR}/templates/deck/`.
