# Quality engineering

Role: **Staff QA / Quality Engineer** (`qa`).

## Test strategy (goes in BUILD.md under `## Test strategy`)

Proportionate to the product and risk:

| Layer | What | Calculator | B2B SaaS |
|---|---|---|---|
| Unit | pure logic, domain rules | **heavy**: engine semantics, precision, edge cases (property-based tests are valuable) | domain rules, policies, parsers |
| Component | UI interaction and states | keypad, history, keyboard | forms, tables, review queue |
| Integration | real DB/services | n/a | repositories, tenant scoping, jobs, webhooks |
| Contract | public APIs / providers | n/a | API schemas, provider adapters |
| End-to-end | critical flows | evaluate → copy → history on web and mobile | sign-up → org → upload → insight → review |
| Evals | AI quality | n/a | golden dataset thresholds (ai.md) |
| Accessibility | automated + manual | axe + VoiceOver/TalkBack pass | axe + keyboard pass on key flows |
| Performance | budgets | bundle size, startup | p95 API latency, job throughput |

## Platform matrix

List supported browsers, OS versions and device classes; test the oldest supported, the current one, and
small and large screens. Record the results as evidence (`G-TEST-PLATFORMS`).

## Regression

Every fixed bug gets a test that fails without the fix. Critical paths have regression coverage
(G-TEST-REGRESSION). Flaky tests are defects: quarantine and fix them, don't ignore them.

## Feature verification procedure

1. Run the tests; capture the exact command and the outcome.
2. Walk every acceptance criterion; record manual verification where automation is not reasonable
   (`--kind manual`), saying what was checked and on which device.
3. Check the DoD (definition-of-done.md).
4. `raftly evidence record ...` for each piece of verification **that actually happened**.
5. Only then: VERIFIED, and later COMPLETE.

## Evidence honesty

A test that was not run is not evidence. A screenshot of a mock is not evidence of a working feature.
"Should work" is not verification. When something can't be verified in the current environment (e.g. no
iOS simulator), mark it UNVERIFIED and say what is needed.
