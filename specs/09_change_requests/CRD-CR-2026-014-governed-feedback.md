# CRD-CR-2026-014 — Governed feedback write-path

**CR ID:** `CRD-CR-2026-014`  
**Requested by:** Prompt 15 / `CRD-AC-015`  
**Date:** 2026-09-10  
**Approval:** Workshop-approved by the Prompt 15 instruction.

## Problem / change

GS-15 is POST_DECISION / OUTCOME_MONITORING, and historical interactions include `AI_ACCEPTED`. Nothing captures that feedback into a governed queue, so an accept event can be treated as a silent policy, prompt, model or gold-label write.

## Why current spec is insufficient

`FEEDBACK-001` and `CRD-FR-010` state the ban. The eval suite only probes an ungoverned write. There is no capture API, review state, or destination denylist.

## Affected requirement IDs

`CRD-FR-010`, `CRD-SEC-012`, `CRD-AC-015`, `CRD-DATA-016`, `CRD-TOOL-010`

## Affected hard guardrails

Feedback cannot silently rewrite policy, ontology, semantic definitions, prompts, models or gold labels. Restricted eval attributes stay out of runtime context. AI has no final credit authority.

## Data / source / authority impact

SME-L015: `Redwood Mobility Pvt Ltd`, limit `3900000`, engine `PASS` / `CREDIT-POLICY-3.2` / `CREDIT_ANALYST`, assigned `PORTFOLIO_ANALYST`, stage `OUTCOME_MONITORING`. No portfolio-outcome row exists for SME-L015; none will be invented. Restricted fairness sample remains evaluation-only.

## Proposed spec text

See `CRD-DATA-016` and `CRD-TOOL-010`.

## Implementation task(s)

`tasks/backlog/TASK-015-governed-feedback.md`

## Verification evidence

`evidence/sdd/CRD-FR-010__CRD-AC-015__20260910.md`
