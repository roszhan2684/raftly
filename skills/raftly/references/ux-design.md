# UX research, product design, design systems

Roles: **Principal UX Researcher**, **Design Director**, **Staff Design Systems Engineer**.
UI/UX is a first-class Raftly stage, not decoration after architecture.

## Design process (spec §11.1)

1. Primary user. 2. Primary job. 3. Frequency and context of use (glanceable? all-day tool? one-handed on a phone?).
4. Primary entities (what the user manipulates). 5. Information density (dense pro tool vs calm consumer app).
6. Information architecture. 7. Navigation model. 8. **2–3 meaningful directions** for major UI architecture
decisions. 9. Research OSS components and patterns. 10. Evaluate accessibility. 11. Recommend one direction.
12. Record the design decision (ADR, owner `design-director`). 13. Responsive behaviour. 14. Interaction states.
15. Design-system tokens. 16. Specify each key screen.

## Design directions

Directions must differ in **interaction model or information architecture**, not only in colour or
typography. For each one: name, one-paragraph concept, layout sketch (ASCII is fine), strengths,
weaknesses, accessibility notes, and the user it suits best. Then Raftly's recommendation and why.

Example: calculator
- **A. Native minimal**: a single screen that mirrors platform calculator conventions; history behind a
  gesture. Lowest learning cost; little differentiation.
- **B. Modern utility**: a keypad with a live expression line (shows `12 × (3 + 4)` as you type and a
  preview result), a tape-style history drawer, copy on tap. Differentiates through clarity and fewer
  errors. **Recommended.**
- **C. Workspace/history-first**: a split view with persistent, editable history lines (notebook-like)
  that can be re-run. Great for power users, heavier on mobile; offer as a desktop/tablet layout later.

Example: B2B coaching
- **A. Inbox/queue**: coaching opportunities as a triage queue (manager workflow first).
- **B. Call-centric**: a call library with transcript, timeline markers and insights panel.
- **C. Team dashboard**: aggregate trends first, then drill into calls.
The recommendation follows the primary job. If that is "managers act on coaching moments weekly", A is
the landing view and B is the detail view.

## Screen specification (every important screen)

screen ID/name (`SCR-...`) · purpose · primary actor · primary action · secondary actions · data shown ·
hierarchy · states (default, **empty**, **loading**, **error**, success feedback, partial/offline) ·
permissions · desktop / tablet / mobile behaviour · keyboard behaviour · accessibility (focus order,
labels, announcements) · analytics (only if justified). Register screens as evidence entities:
`raftly evidence entity --id SCR-history --name "History drawer"`.

## Accessibility baseline

Target **WCAG 2.2 AA**: contrast (4.5:1 text, 3:1 large text and UI), full keyboard operability and
visible focus, touch targets around 44×44 pt (iOS) / 48×48 dp (Android), screen-reader labels and live-region
announcements for dynamic results, reduced motion, text scaling to 200% without loss, no information
carried by colour alone. Accessibility is part of each feature's Definition of Done.

## References policy (spec §11.3)

References are evidence, not templates. Extract workflow conventions, information hierarchy, interaction
patterns and terminology. Never clone a competitor's interface or copy proprietary assets.

## OSS component evaluation (spec §11.4)

For non-trivial components (tables, command palettes, charts, rich editors, date pickers, drag-and-drop,
forms, dialogs, mobile primitives), compare candidates on licence (prefer MIT/Apache-2.0/BSD), maintenance
(release recency, open-issue health), accessibility, functionality, framework fit, customisation,
performance and bundle size, and dependency cost.

**Building internally is a legitimate senior decision** for trivial components. A calculator keypad is a
grid of buttons. A dependency adds nothing but weight. Record the choice in `dependencies.yaml` (adopted)
or in the ADR (rejected alternatives).

Frequently credible starting points (verify the current state before recommending): headless/accessible
primitives (e.g. Radix UI, React Aria), shadcn/ui-style copy-in components, TanStack Table, cmdk, Recharts or
visx, Tiptap or Lexical, dnd-kit, React Hook Form. These are candidates to evaluate, not defaults.

## Design system (DESIGN_SYSTEM.md)

typography scale · spacing scale (4/8-based) · radius · colour **semantics** (surface, text, accent,
success, warning, danger, focus) with light/dark values and contrast checked · elevation · layout grid and
breakpoints · component inventory with states · motion (durations, easing, reduced-motion behaviour) ·
iconography strategy · theming · token examples (CSS variables or JSON).
If the founder states a preference ("no rounded buttons"), apply it **to this project's tokens** and record
it as a PROJECT_ONLY learning. It is never a global rule.

If `.raftly/brand/tokens.json` exists (`{"accent": "#hex", "font": "..."}`), the blueprint and deck use it.
