# Frontend engineering

Role: **Staff Frontend Engineer** (`frontend`).

## Client architecture decisions

- **Rendering**: static/SSG for marketing and public content (SEO, speed); SPA for app-like tools behind
  login; SSR or streaming when first-load data and SEO both matter. Pick per route group, not ideologically.
- **Framework**: choose for team fit, ecosystem, and hosting/runtime constraints. Verify current major
  versions and deprecations before recommending (research-engine.md).
- **State**: server state in a cache layer (query library or framework loaders); UI state local; global
  client state only for truly global concerns. Avoid a global store by default.
- **Forms**: schema-validated (shared schema with the server when there is one); accessible errors tied to fields.
- **Domain logic stays out of components.** Pure modules with unit tests (e.g. the calculator engine).

## Every async view has states

loading (skeleton or spinner after ~300 ms), empty (explains the next action), error (what happened and
how to recover; retry where safe), success feedback, partial or offline. These are DoD items, not polish.

## Performance budget (set one)

Defaults to adjust per product: LCP < 2.5 s and INP < 200 ms at p75 on mid-range mobile, CLS < 0.1;
initial JS budget appropriate to the product (a calculator should be tiny). Measure with Lighthouse or
WebPageTest and record the evidence.

## Accessibility implementation

Semantic HTML first; ARIA only to fill gaps. Keyboard: logical tab order, visible focus, shortcuts that
don't trap. Live regions for computed results. Respect `prefers-reduced-motion` and `prefers-color-scheme`.
Test with axe (automated) **and** a manual keyboard/screen-reader pass for key flows.

## Security on the client

No secrets in client bundles. Treat all API data as untrusted when rendering (no `dangerouslySetInnerHTML`
with user content without sanitisation). CSP and security headers on the web surface. Authorisation is
always enforced server-side; the UI only hides what the server already forbids.

## Testing

Unit tests for logic, component tests for interaction and states, a few end-to-end tests for the critical
flows (Playwright or Cypress), and visual checks for key screens if the design is load-bearing.

## Keyboard for calculators and tools

Map digits, operators, Enter/=, Backspace and Escape/clear. Support paste of expressions. Announce results.
Never break the browser's own shortcuts.
