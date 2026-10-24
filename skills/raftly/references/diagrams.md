# Product diagrams (DIAGRAMS.md)

DIAGRAMS.md is a final blueprint deliverable: five Mermaid diagrams that let anyone see the product in
five minutes. Draw them **after** PRODUCT, DESIGN, ARCHITECTURE and DATA_MODEL exist, and only from what
those documents and the ADRs say. A diagram that contradicts a recorded decision is a defect.

Template: `templates/docs/DIAGRAMS.md`. Checked by `raftly validate` and the Blueprint Completion Gate.

## The five diagrams

| # | Section | Mermaid type | Shows | Source documents |
|---|---|---|---|---|
| 1 | System architecture | `flowchart LR` (or `C4Container`) | parts, where each runs, external services, trust boundaries | ARCHITECTURE.md, ADRs |
| 2 | User flow | `flowchart TD` (or `journey`) | the primary journey, decision points, the main error branch | PRODUCT.md, features |
| 3 | Screen map and navigation | `flowchart LR` (or `stateDiagram-v2`) | every V1 screen and the transitions between them | DESIGN.md |
| 4 | Data model | `erDiagram` (client-only: `stateDiagram-v2` or `classDiagram`) | entities, keys, relationships, tenant/owner keys | DATA_MODEL.md |
| 5 | Critical path sequence | `sequenceDiagram` | the most important request end to end, including the failure path | ARCHITECTURE.md, features |

## Rules

- **Readable first.** 5-15 boxes per diagram. Split or simplify rather than cram. Label arrows with the
  verb or protocol (`HTTPS`, `reads`, `webhook`).
- **True to the decisions.** Name the chosen technology only when an ADR chose it, and cite the ADR in
  the section text. Unknown or undecided parts are labelled `undecided`, never invented.
- **Proportionate.** A calculator's architecture is a client with a pure engine; don't draw servers,
  queues or databases it doesn't have. Use `Not applicable: <reason>` for a diagram that truly doesn't
  apply (no screens for a pure API), but at least one diagram must apply.
- **Architecture shows deployment.** Say where each part runs (device, CDN, cloud region) and mark the
  trust boundary. Mermaid lays out lines that cross `subgraph` boxes poorly, so with many connections
  prefer one plain `flowchart LR` and mark third parties with `classDef ext stroke-dasharray: 5 5`
  (`zoom["Zoom API"]:::ext`); keep `subgraph` for small diagrams.
- **The sequence includes failure.** Use `alt`/`else` for the main failure (timeout, validation error,
  payment declined) and show what the user sees.
- **The data model shows ownership.** Include primary keys, foreign keys and the tenant/owner key on
  every tenant-scoped table.
- **Valid Mermaid.** One diagram per block; first line is the diagram type. Avoid parentheses and
  quotes inside unquoted labels (`A[Save (draft)]` breaks; use `A["Save (draft)"]`). Never use Mermaid
  keywords as node ids (`call`, `click`, `class`, `style`, `end`, `graph`, `subgraph`): write
  `callDetail["Call"]`, not `call["Call"]`.

## Updating

When a decision changes (supersede, override, requirement change), update the affected diagrams in the
same turn and mark DIAGRAMS.md CURRENT with `raftly state doc DIAGRAMS.md CURRENT`.
