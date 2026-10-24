# Design Document — Tally

## Experience principles
- **See before you commit**: the expression and a live preview are always visible.
- **Familiar first**: standard keypad layout; nothing to learn.
- **One-handed and glanceable** on phones; **typeable** on desktops.
- **Quiet**: no ads, prompts or upsells; motion only for feedback.

## Primary user, job and context
Quick, frequent, short sessions (seconds to a minute), often one-handed, sometimes in noisy or bright
environments. Low information density: one number matters at a time.

## Information architecture
Entities: the current expression, the result, history entries. One primary screen (SCR-main) plus a
history surface (SCR-history). No settings screen in V1 (theme follows the system; haptics follow the system).

## Navigation
Single screen. History opens as a drawer (mobile: swipe up or a button; web: a side panel on wide layouts,
a drawer on narrow ones). The keyboard shortcuts dialog (`?`) on web.

## Key flows
1. Calculate: tap or type → watch the preview → `=` → result.
2. Reuse: open history → tap a result → it is inserted into the current expression.
3. Copy: tap copy (or long-press the result, or Cmd/Ctrl+C) → "Copied".

## Design direction options

### Option A — Native minimal
Mirrors platform calculators: one result line, keypad, history hidden behind a gesture.
```text
|            1,284 |
| C  ±  %  ÷ |
| 7  8  9  × | ...
```
Strengths: zero learning. Weaknesses: indistinguishable from the built-in app (R-003); hides the expression.
Accessibility: simple. Best for: users satisfied with what they have (that is, not our ICP).

### Option B — Modern utility (recommended)
Two-line display: the expression line (`12 × (3 + 4)`) and a large result with a live preview in a muted tone
until `=`. A history drawer is one swipe away; copy sits next to the result.
```text
|      12 × (3 + 4) |
|              = 84 |  [copy]
| C  (  )  ÷ |
| 7  8  9  × |
| 4  5  6  − |
| 1  2  3  + |
| ±  0  .  = |   [history ▲]
```
Strengths: makes precedence and percent visible (R-005), and expresses the differentiators. Weaknesses: a busier
display, which needs careful type scale. Accessibility: two announcement streams (debounce). Best for: our ICP.

### Option C — Workspace / history-first
A notebook-like list of calculation lines that can be edited and re-run, with the keypad below.
Strengths: power-user reuse. Weaknesses: cramped on phones; more build effort. Best for: tablet/desktop
power users. Post-V1 candidate.

## Chosen direction
**Option B: Modern utility** (ADR-005, RECOMMEND, confidence 75). It makes the product's promise visible
without sacrificing familiarity. Validate in EXP-001 interviews.

## Key screens

### SCR-main — Calculator
- Purpose: enter and evaluate expressions.
- Primary actor / action: end user / tap `=`. Secondary: copy, clear, backspace, open history.
- Data shown and hierarchy: result (largest) → expression → keypad. The preview uses the muted text token until evaluated.
- States: default `0` · typing (expression + preview) · evaluated · error ("Can't divide by zero", in the danger text token, no modal) · empty (shows `0`) · no loading state (local).
- Permissions: none.
- Desktop: keypad max width 420 px, centred; history as a side panel ≥ 900 px. Tablet: same as desktop at ≥ 700 px. Mobile: full-bleed keypad; display takes the top 35%.
- Keyboard (web): see F004; `?` opens shortcuts.
- Accessibility: labelled keys, live region for results (debounced 400 ms while typing), 44pt/48dp targets, reflow at 200% text.
- Analytics: none (ADR-008).

### SCR-history — History
- Purpose: reuse past results.
- Primary action: tap a result to insert it. Secondary: restore the expression, copy, clear all.
- Data: expression, result, relative time; newest first; max 100.
- States: empty ("Your calculations will appear here. History stays on this device.") · list · storage-unavailable note · confirm-clear inline.
- Desktop/tablet: side panel; mobile: bottom sheet at 70% height.
- Keyboard: focus trap while modal, Escape closes, arrow keys move between entries.
- Accessibility: entries announced as "12 times 7 equals 84, 2 minutes ago".

## Responsive behaviour
Breakpoints: < 700 px phone layout; 700–899 px tablet; ≥ 900 px desktop with the history panel. Landscape
phone keeps the basic keypad (no scientific mode).

## States
Global patterns: errors inline in the result line; toasts only for "Copied"; no blocking dialogs except
the clear-history confirmation (inline).

## Accessibility
Target WCAG 2.2 AA (REQ-005): contrast verified per token pair; full keyboard on web; screen-reader labels and
announcements; reduced motion removes press animations; haptics are optional.

## OSS component choices
| Need | Choice | Licence | Why / rejected alternatives |
|---|---|---|---|
| Keypad, display, drawer | Internal components | — | ADR-007: trivial components; a library adds weight without benefit |
| Haptics | expo-haptics | MIT | Platform haptics from the chosen runtime |
| Clipboard | expo-clipboard | MIT | Same |
