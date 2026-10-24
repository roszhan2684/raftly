# Product Diagrams — Tally

These diagrams render as pictures on GitHub and in most Markdown viewers that support Mermaid. Each one is
drawn from a recorded decision; nothing here goes beyond ARCHITECTURE.md, DESIGN.md and the ADRs.

## 1. System architecture
A client-only app (ADR-001): one Expo + React Native Web codebase (ADR-004) runs on the phone or in the
browser. All maths happens in a pure TypeScript engine (ADR-002) with decimal.js (ADR-003). History stays on
the device. There are no runtime services; stores and the static web host only distribute the app.

```mermaid
flowchart LR
  user([User]) --> ui
  subgraph device["User's device: iOS, Android or browser"]
    ui["UI layer: keypad, display, history drawer"] -->|tokens| engine["Engine: tokenizer, parser, evaluator"]
    engine -->|EvalResult| ui
    engine --- dec[(decimal.js)]
    ui -->|onEvaluated| hist["History store"]
    hist --> storage[("On-device storage: AsyncStorage / localStorage")]
  end
  subgraph dist["Distribution only, no runtime calls"]
    stores["App Store / Google Play"]
    host["Static web host + service worker"]
  end
  stores -. install .-> device
  host -. load once, then offline .-> device
```

## 2. User flow
The three key flows from DESIGN.md: calculate, reuse a result from history, copy. Errors stay inline,
never in a dialog.

```mermaid
flowchart TD
  open([Open Tally]) --> type["Type or tap an expression"]
  type --> preview["Live preview shows the provisional result"]
  preview --> eq{"Press ="}
  eq -->|valid| result["Result shown large, saved to history"]
  eq -->|divide by zero / overflow| err["Inline message: Can't divide by zero"]
  err --> type
  result --> next{"Next?"}
  next -->|keep calculating| type
  next -->|copy| copied["Copied toast"]
  next -->|open history| history["History drawer"]
  history -->|tap an entry| insert["Result inserted into the expression"]
  insert --> type
```

## 3. Screen map and navigation
One screen plus a history surface (DESIGN.md, ADR-005). History is a bottom sheet on phones and a side
panel at 900 px and wider; the shortcuts dialog exists on the web only.

```mermaid
stateDiagram-v2
  [*] --> Main
  Main: SCR-main Calculator
  History: SCR-history History
  Shortcuts: Keyboard shortcuts (web)
  Main --> History: swipe up / history button / panel on wide screens
  History --> Main: tap an entry or Escape
  Main --> Shortcuts: press ?
  Shortcuts --> Main: Escape
  History --> History: confirm clear all (inline)
```

## 4. Data model
No server and no personal data (blueprint data section: NOT_APPLICABLE). The only data is the engine
state and up to 100 history entries on the device (F001, F003).

```mermaid
classDiagram
  class EngineState {
    tokens: Token[]
    lastOperation: op + operand
    lastResult: exact decimal string
  }
  class HistoryEntry {
    id: string
    expression: string
    resultExact: decimal string
    createdAt: timestamp
  }
  class HistoryStore {
    entries: max 100, newest first
    add(entry)
    clear()
  }
  EngineState ..> HistoryEntry : evaluate() creates
  HistoryStore "1" o-- "0..100" HistoryEntry
```

## 5. Critical path sequence
Pressing `=`: the most important path in the product. Exact maths, display-only rounding, and an inline
error instead of a crash (ARCHITECTURE.md failure behaviour, ADR-006).

```mermaid
sequenceDiagram
  actor U as User
  participant UI as UI layer
  participant E as Engine
  participant H as History store
  participant S as Device storage
  U->>UI: press =
  UI->>E: evaluate(tokens, state)
  E->>E: tokenize, parse with precedence, compute with decimal.js
  alt valid expression
    E-->>UI: EvalResult value, display
    UI-->>U: show result, announce it to screen readers
    UI->>H: add(expression, resultExact)
    H->>S: save
    alt storage unavailable
      S-->>H: error
      H-->>UI: session-only history
      UI-->>U: note: History won't be saved
    end
  else divide by zero or overflow
    E-->>UI: error value
    UI-->>U: inline message, next key starts fresh
  end
```
