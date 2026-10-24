---
id: ADR-007
title: "Build the keypad and display internally; no UI component library"
owner_role: design-systems
date: 2026-10-24
status: ACCEPTED
decision_type: AUTO
impact: low
reversibility: high
type1: false
confidence: 90
affects: []
supersedes: []
superseded_by: null
evidence: []
category: design
---
# ADR-007 — Build the keypad and display internally; no UI component library

- **Owner role:** design-systems
- **Decision type:** AUTO · **Impact:** low · **Reversibility:** high · **Confidence:** 90/100

## Context
The UI consists of a keypad grid, a two-line display, a history drawer and a few icons.

## Options considered
| Option | Benefit | Cost |
|---|---|---|
| Internal components on React Native primitives | exact control of a11y, haptics and tokens; zero dependency weight | a few hundred lines |
| A cross-platform component library | prebuilt buttons and sheets | bundle weight, theming friction, little real benefit for a keypad |

## Decision
Build internally on React Native primitives (Pressable, Text, View, a modal or bottom-sheet built in-house).

## Rationale
Spec §9: "For a trivial component, building internally can be the senior decision." A keypad is a grid of buttons.

## Supporting evidence
Not applicable (engineering judgment, low impact).

## Rejected alternatives
Component libraries (recorded as REJECTED in dependencies.yaml).

## Consequences
Accessibility props (roles, labels, hints) are our responsibility. They are part of F002's DoD.

## Revisit trigger
Not applicable (low impact, reversible).

## Affected requirements / features
F002, F003, F005
