---
id: ADR-004
title: Expo + React Native Web as the single cross-platform codebase
owner_role: mobile
date: 2026-10-24
status: ACCEPTED
decision_type: RECOMMEND
impact: high
reversibility: low
type1: true
confidence: 72
affects:
  - REQ-004
  - REQ-005
  - REQ-009
supersedes: []
superseded_by: null
evidence:
  - "https://docs.expo.dev/workflow/web/"
  - RESEARCH.md
category: platform
revisit_trigger: "A-002 invalidated: web performance budget missed or native feel unacceptable on test devices"
---
# ADR-004 — Expo + React Native Web as the single cross-platform codebase

- **Owner role:** mobile
- **Decision type:** RECOMMEND · **Impact:** high · **Reversibility:** low · **Confidence:** 72/100

## Context
Tally ships on iOS, Android and the web. The UI is small (one main screen plus a history drawer), so one
codebase is attractive if it feels native and the web build stays fast.

## Options considered
| Option | Pros | Cons | Fit |
|---|---|---|---|
| A. Expo (React Native) + React Native Web | one codebase for three surfaces; official web support; static web export; managed builds | web bundle heavier than plain web; RN upgrade cadence | **Recommended** |
| B. Flutter (mobile + web) | consistent rendering | web output less "web-native" (accessibility and SEO trade-offs need checking); Dart | Viable alternative |
| C. Native iOS + native Android + separate web | best platform feel | three UIs for a tiny product | Over-scoped |
| D. PWA only | simplest | weaker store presence and haptics; iOS PWA limits | Doesn't meet "mobile app" goal |

## Decision
Option A. The shared engine (ADR-002) is plain TypeScript, so it remains portable if this decision is revisited.

## Rationale
Expo documents first-class web support from the same codebase via react-native-web, with static rendering and
`npx expo export --platform web` for production builds (checked 2026-10-24). This keeps the UI layer single-sourced
for a product whose differentiation is semantics and polish.

## Supporting evidence
- Expo docs, "Develop websites with Expo" (checked 2026-10-24).
- Assumption A-002 (confidence 65) **must be validated in N003** on two physical devices plus a Lighthouse run.

## Rejected alternatives
B (viable; rejected for web accessibility/SEO uncertainty and team-language fit), C (cost), D (store goal).

## Consequences
- Web performance needs a budget and measurement (R-002).
- Haptics and clipboard come from Expo modules (recorded in dependencies.yaml).
- Store builds via Expo tooling; the web build deploys as static files to any static host.

## Revisit trigger
A-002 invalidated: the web performance budget is missed, or the native feel is unacceptable on test devices.

## Affected requirements / features
REQ-004, REQ-005, REQ-009 · F002, F005, F006
