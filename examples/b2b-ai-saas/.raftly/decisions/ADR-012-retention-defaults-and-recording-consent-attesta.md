---
id: ADR-012
title: Retention defaults and recording-consent attestation
owner_role: privacy
date: 2026-10-24
status: ACCEPTED
decision_type: RECOMMEND
impact: medium
reversibility: medium
type1: false
confidence: 70
affects:
  - REQ-010
  - REQ-011
supersedes: []
superseded_by: null
evidence: []
category: privacy
revisit_trigger: Legal review recommends different defaults or a new jurisdiction is targeted
---
# ADR-012 — Retention defaults and recording-consent attestation

- **Owner role:** privacy
- **Decision type:** RECOMMEND · **Impact:** medium · **Reversibility:** medium · **Confidence:** 70/100

## Context
Recordings include prospects who are not SalesLens users. Consent requirements differ by jurisdiction (some require all-party consent). Customers are the controllers of their recordings; SalesLens acts as their processor (to be confirmed by legal review).

## Options considered
| Topic | Chosen default | Alternative |
|---|---|---|
| Audio retention | 12 months, configurable 30 days – 36 months | indefinite (rejected: minimisation) |
| Transcripts and insights | kept until the call or org is deleted; configurable | same as audio |
| Consent | uploader attests per upload or per Zoom connection; an org-level consent policy text is shown at attestation | no attestation (rejected: R-001) |
| Deletion | call deletion removes audio, transcript, insights and derived eval samples within 30 days (backups roll off per the backup policy) | soft delete only |

## Decision
Adopt the defaults above. Show the attestation text in the upload flow and on Zoom connection; store attestation records (who, when, policy version).

## Rationale
Minimisation and controller support without blocking the core flow. Legal review confirms or adjusts the defaults before launch.

## Supporting evidence
privacy-compliance.md; **requires professional legal review** (G-COMPLIANCE-READINESS, G-LEGAL-DOCS).

## Rejected alternatives
See the table.

## Consequences
- Retention and deletion jobs are part of F009 and must be verified by tests and a restore/deletion drill.
- DPA template and subprocessor list required before paid launch.

## Revisit trigger
Legal review recommends different defaults or a new jurisdiction is targeted.

## Affected requirements / features
REQ-010, REQ-011 · F002, F009
