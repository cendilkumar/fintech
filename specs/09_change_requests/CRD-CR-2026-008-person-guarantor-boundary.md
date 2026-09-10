# CRD-CR-2026-008 — Natural-person and guarantor boundary

**CR ID:** `CRD-CR-2026-008`  
**Requested by:** Prompt 09 / `CRD-AC-003`, `CRD-AC-013`  
**Date:** 2026-09-10  
**Approval:** Workshop-approved by the Prompt 09 instruction.

## Problem / change

Identity types already split sole-trader business from owner and keep guarantors off the organization cluster. Nothing assembles an affected-person view, binds adverse factors to source evidence, or rejects invented personal attributes.

## Why current spec is insufficient

`CRD-SEC-008` / `CRD-SEC-009` and `CRD-AC-003` / `CRD-AC-013` state the outcomes. There is no data contract for purpose, restricted-attribute exclusion, grounded adverse factors or recourse visibility.

## Affected requirement IDs

`CRD-FR-005`, `CRD-SEC-005`, `CRD-SEC-008`, `CRD-SEC-009`, `CRD-AC-003`, `CRD-AC-013`

## Affected hard guardrails

Sole-trader and natural-person-guarantor cases require explicit affected-person and governance analysis. Restricted evaluation attributes do not enter runtime decision context. Adverse routes preserve human authority, material-reason evidence and recourse. Do not invent personal attributes.

## Data / source / authority impact

SME-L003: `ORG-003` `SOLE_TRADER_BUSINESS` + `NP-003` `NATURAL_PERSON_OWNER` (`decision_feature_eligible=CONDITIONAL`). SME-L013: guarantor `NP-013`; engine `POL-ARREARS-02` / `AUTH-ADVERSE-01`; exposure past due `185000` on `EXP-013`. Recourse text is `human_authority_and_recourse_policy.md`. Fairness sample is evaluation-only.

## Proposed spec text

See `CRD-DATA-011`.

## Implementation task(s)

`tasks/backlog/TASK-009-person-guarantor-boundary.md`

## Verification evidence

`evidence/sdd/CRD-SEC-008__CRD-AC-003-013__20260910.md`
