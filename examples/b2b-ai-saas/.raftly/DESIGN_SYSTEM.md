# Design System — SalesLens

## Typography
Inter (SIL Open Font License; self-hosted) for UI, tabular numerals for metrics; JetBrains Mono (OFL) for timestamps.
Scale: 28/22/18/16/14/12; body 14/20 for dense lists, 16/24 for reading the transcript.

## Spacing
4-pt base: 4, 8, 12, 16, 20, 24, 32, 48. Dense list rows 44 px minimum height.

## Radius
6 (inputs, buttons), 10 (cards, panels), 999 (chips).

## Colour semantics
| Token | Light | Dark | Use | Contrast checked |
|---|---|---|---|---|
| `bg` | #F8F9FB | #0F1115 | app background | — |
| `surface` | #FFFFFF | #171A21 | panels | — |
| `text` | #14171F | #E9ECF2 | primary text | AA |
| `text-muted` | #5B6475 | #A0A8B8 | secondary | ≥ 4.5:1 |
| `accent` | #4338CA | #A5B4FC | primary actions, focus | ≥ 4.5:1 with accent-ink |
| `objection` | #B45309 | #FBBF24 | objection chips (always with a label) | text label required |
| `competitor` | #0E7490 | #67E8F9 | competitor chips (with a label) | text label required |
| `coaching` | #6D28D9 | #C4B5FD | coaching chips (with a label) | text label required |
| `success` / `danger` | #15803D / #B91C1C | #4ADE80 / #F87171 | status | AA on surface |

The automated contrast test (N008) is the evidence; the values above are targets.

## Elevation
Two levels: panel border (1 px), popover shadow (single soft shadow).

## Layout
12-column fluid grid; sidebar 240 px; detail pane min 420 px; max content 1280 px.

## Components
| Component | Variants | States | Source |
|---|---|---|---|
| Button | primary, secondary, ghost, danger | hover, focus-visible, disabled, loading | internal on accessible primitives |
| InsightChip | objection, competitor, coaching | default, selected | internal |
| QueueRow | — | new, accepted, dismissed, focused | internal |
| AudioSnippet | 30 s, full | loading, playing, error | internal (native audio) |
| TranscriptSegment | rep, prospect | default, highlighted | internal |
| Dialog, Menu, Listbox | — | — | accessible primitives library |
| Toast | info, success, error | announced | internal |

## States
Focus-visible ring 2 px `accent` with 2 px offset; loading via skeletons; disabled at 40% opacity plus `aria-disabled`.

## Motion
120–200 ms ease-out for panels and toasts; none under reduced motion.

## Accessibility
Keyboard shortcuts documented and remappable-free (no single-key shortcuts while typing in inputs); targets ≥ 24 px (WCAG 2.2 target size) with dense mode still ≥ 24 px.

## Theme
Light default, dark supported, following the system with a manual override in user settings.

## Icons
Lucide (ISC licence; verify at adoption) at 16/20 px, stroke 1.75.

## Token examples
```css
:root { --bg:#F8F9FB; --surface:#FFFFFF; --text:#14171F; --text-muted:#5B6475; --accent:#4338CA;
        --objection:#B45309; --competitor:#0E7490; --coaching:#6D28D9; --radius-control:6px; --radius-card:10px; }
```
