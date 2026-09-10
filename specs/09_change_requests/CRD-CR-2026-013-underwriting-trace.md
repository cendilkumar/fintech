# CRD-CR-2026-013 — Reconstructable underwriting trace

**CR ID:** `CRD-CR-2026-013`  
**Requested by:** Prompt 14 / `CRD-FR-009`, AT-16, AT-17  
**Date:** 2026-09-10  
**Approval:** Workshop-approved by the Prompt 14 instruction.

## Problem / change

Context, retrieval, policy, authority and memo contracts exist, but nothing writes a reconstructable underwriting trace. A generated rationale can look like policy. Hidden chain-of-thought could be treated as an audit field.

## Why current spec is insufficient

`CRD-DATA-003` and `CRD-TOOL-008` name the envelope. `participant_templates/10_decision_trace_template.json` is an example, not a writer. AT-16 / AT-17 have no executable inspection.

## Affected requirement IDs

`CRD-FR-009`, `CRD-SEC-011`, `CRD-DATA-003`, `CRD-TOOL-008`, `CRD-AC-001`, `CRD-AC-007`, `CRD-AC-013`

## Affected hard guardrails

Decision traces record evidence, checks, versions, concise rationale and human action — not hidden chain-of-thought. Generated output cannot modify or replace active policy. AI has no final credit authority. A recommendation is not a HumanDecision.

## Data / source / authority impact

GS-01 SME-L001: engine `PASS` / `CREDIT_ANALYST`; bank `9126438.87`; tax `9407915.21`. GS-07 SME-L007: `EXCEPTION_REVIEW` / `POL-EXC-07` / `SENIOR_UNDERWRITER`. GS-13 SME-L013: `ADVERSE_FACTORS_REVIEW` / `POL-ARREARS-02` / `CREDIT_AUTHORITY`. Policy evidence remains `CREDIT-POLICY-3.2` plus the Policy Engine row.

## Proposed spec text

See expanded `CRD-DATA-003` and `CRD-TOOL-008`.

## Implementation task(s)

`tasks/backlog/TASK-014-underwriting-trace.md`

## Verification evidence

`evidence/sdd/CRD-FR-009__AT-16-17__20260910.md`
