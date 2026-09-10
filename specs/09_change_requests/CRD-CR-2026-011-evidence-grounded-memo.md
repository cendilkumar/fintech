# CRD-CR-2026-011 — Evidence-grounded credit memo

**CR ID:** `CRD-CR-2026-011`  
**Requested by:** Prompt 12 / `CRD-AC-001`, `CRD-AC-014`  
**Date:** 2026-09-10  
**Approval:** Workshop-approved by the Prompt 12 instruction.

## Problem / change

Context, policy, authority and degraded-mode contracts exist, but nothing emits a structured credit memo. A narrative can look complete while inventing factors, omitting provenance, or presenting itself as the decision.

## Why current spec is insufficient

`credit_memo_standard.md` and `CRD-SEC-003` state provenance. `CreditMemo` is a type, not a generator. There is no required-section contract or HG-03 coverage check on generated text.

## Affected requirement IDs

`CRD-FR-006`, `CRD-SEC-003`, `CRD-AC-001`, `CRD-AC-014`, `CRD-NFR-005`

## Affected hard guardrails

Material AI-assisted factors require evidence and provenance. AI has no final credit authority. Generated thresholds not in CREDIT-POLICY-3.2 are rejected. A recommendation is not a HumanDecision.

## Data / source / authority impact

SME-L001: aligned Rivermint Foods, bank inflows `9126438.87`, tax `9407915.21`, exposure `584194.1`, bureau band A, engine `PASS` / `CREDIT_ANALYST`. SME-L014: limit `1950000`, engine `PASS`, invented-threshold trap. Memo standard: `evidence/02_documents/credit_memo_standard.md`.

## Proposed spec text

See `CRD-DATA-014`.

## Implementation task(s)

`tasks/backlog/TASK-012-evidence-grounded-memo.md`

## Verification evidence

`evidence/sdd/CRD-FR-006__CRD-AC-001-014__20260910.md`
