# TASK-014 — Reconstructable underwriting trace
**Status:** COMPLETED (AT-16 / AT-17 contract tests; workbench trace UI not in scope)  
**Requirements:** `CRD-FR-009`, `CRD-SEC-011`, `CRD-DATA-003`, `CRD-TOOL-008`  
**Acceptance focus:** AT-16, AT-17 on GS-01, GS-07, GS-13  
**Change request:** `CRD-CR-2026-013`  
**Guardrails:** No hidden chain-of-thought; generated explanation is not policy evidence; recommendation is not HumanDecision

## Objective
Write a reconstructable underwriting trace with evidence sources, versions, consent/purpose, retrieval route, financial calculations, policy version, exceptions, generated recommendation, required authority, human action and final outcome.

## Verification
- `python -m unittest tests.test_crd_fr_009_at16_at17_trace`
- Prior suites remain green
- `python scripts/sdd_validate.py`
- Evidence: `evidence/sdd/CRD-FR-009__AT-16-17__20260910.md`

## Out of scope
Workbench Decision Trace screen. Governed feedback write-path (Prompt 15).
