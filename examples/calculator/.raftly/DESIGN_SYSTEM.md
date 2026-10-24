# Design System — Tally

## Typography
System font stack (SF Pro on iOS, Roboto on Android, `system-ui` on web): no font download, native feel.
Digits use tabular figures. Scale: result 56/48/40 (auto-shrink steps), expression 22, key labels 28,
body 16, caption 13. Weights 400/500/600.

## Spacing
4-pt base: 4, 8, 12, 16, 24, 32. Keypad gap 12 (mobile), 10 (desktop).

## Radius
Keys 16 (fully rounded on phones at 1:1 aspect ratio), panels 20, toasts 12. Adjust per project preferences if the founder states any (preferences stay project-only).

## Colour semantics
| Token | Light | Dark | Use | Contrast checked |
|---|---|---|---|---|
| `surface` | #F7F7F8 | #0E0F12 | app background | — |
| `surface-key` | #FFFFFF | #1C1E24 | digit keys | vs text 15:1 / 14:1 |
| `surface-op` | #E9ECF5 | #262A35 | operator keys | vs text ≥ 7:1 |
| `accent` | #2851D8 | #8AA6FF | `=` key, focus, links | vs accent-ink ≥ 4.5:1 |
| `accent-ink` | #FFFFFF | #0E0F12 | text on accent | — |
| `text` | #111318 | #F1F3F7 | primary text | AA both themes |
| `text-muted` | #5A6070 | #A3AAB8 | expression line, preview | ≥ 4.5:1 on surface |
| `danger-text` | #B42318 | #FF8A80 | error message | ≥ 4.5:1 on surface |
| `focus` | #2851D8 | #8AA6FF | focus ring 2 px + 2 px offset | ≥ 3:1 vs adjacent |

The contrast values are design targets. The automated token test (F005) is the evidence.

## Elevation
Flat keys with a 1-px border in light (`#E3E5EA`); in dark, the surface step is enough. History sheet: a single shadow level.

## Layout
Max keypad width 420 px; display/keypad split 35/65 on phones; side panel 320 px on desktop.

## Components
| Component | Variants | States | Source |
|---|---|---|---|
| Key | digit, operator, equals, utility | default, pressed, focus-visible, disabled | internal |
| Display | expression line, result line | typing, preview, evaluated, error | internal |
| HistoryEntry | — | default, pressed, focus | internal |
| Sheet/Panel | bottom sheet, side panel | open, closed | internal |
| Toast | info | visible (2 s), announced | internal |

## States
Pressed: 8% darken (light) / lighten (dark) plus scale 0.97 (removed under reduced motion). Focus-visible: 2-px focus ring.

## Motion
Press feedback 80 ms ease-out; sheet 220 ms with a standard deceleration curve; no motion under `prefers-reduced-motion` / Reduce Motion.

## Accessibility
Minimum targets 44 pt / 48 dp; focus never hidden; text scales to 200% (keypad reflows to scroll if needed).

## Theme
Follows the system light/dark setting live. No manual toggle in V1.

## Icons
A small internal SVG set (copy, history, backspace, close) drawn on a 24-px grid; no icon font.

## Token examples
```css
:root {
  --surface: #F7F7F8; --surface-key: #FFFFFF; --surface-op: #E9ECF5;
  --accent: #2851D8; --accent-ink: #FFFFFF; --text: #111318; --text-muted: #5A6070;
  --danger-text: #B42318; --focus: #2851D8; --radius-key: 16px; --space-3: 12px;
}
@media (prefers-color-scheme: dark) {
  :root { --surface: #0E0F12; --surface-key: #1C1E24; --surface-op: #262A35; --accent: #8AA6FF;
          --accent-ink: #0E0F12; --text: #F1F3F7; --text-muted: #A3AAB8; --danger-text: #FF8A80; --focus: #8AA6FF; }
}
```
