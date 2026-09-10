# CRD-CR-2026-007 — Credit authority gate

**CR ID:** `CRD-CR-2026-007`  
**Requested by:** Prompt 08 / `CRD-AC-002`, `CRD-AC-007`  
**Date:** 2026-09-10  
**Approval:** Workshop-approved by the Prompt 08 instruction.

## Problem / change

Policy evaluation already records `required_human_role`, but nothing blocks AI (or a lower LOS-assigned role) from treating a recommendation as a final approve, large-limit authorization, exception approval or adverse determination.

## Why current spec is insufficient

`CRD-FR-007` / `CRD-FR-011` and `CREDIT-AUTH-001` state the rule; `CRD-TOOL-005` / `CRD-TOOL-007` are stubs. There is no action catalog or role-sufficiency check.

## Affected requirement IDs

`CRD-FR-007`, `CRD-FR-011`, `CRD-TOOL-005`, `CRD-TOOL-007`, `CRD-AC-002`, `CRD-AC-007`, `CREDIT-AUTH-001`

## Affected hard guardrails

AI has no autonomous final credit authority. Adverse and exception routes preserve human authority. Required role is the engine role, not the LOS assignment, when they differ.

## Data / source / authority impact

Policy Engine `required_human_role` is controlling. Role matrix `AI_AGENT.final_credit_decision = NO`. SME-L002 requires `CREDIT_AUTHORITY`. SME-L007 requires `SENIOR_UNDERWRITER`.

## Proposed spec text

See `CRD-DATA-010` and tightened `CRD-TOOL-005` / `CRD-TOOL-007`.

## Implementation task(s)

`tasks/backlog/TASK-008-credit-authority-gate.md`

## Verification evidence

`evidence/sdd/CRD-FR-007-011__CRD-AC-002-007__20260910.md`
