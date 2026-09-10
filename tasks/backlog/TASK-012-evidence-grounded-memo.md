# TASK-012 — Evidence-grounded credit memo
**Status:** COMPLETED (CRD-AC-001 / CRD-AC-014 memo tests; workbench UI not in scope)  
**Requirements:** `CRD-FR-006`, `CRD-SEC-003`, `CRD-DATA-014`, `CRD-NFR-005`  
**Acceptance focus:** `CRD-AC-001`, `CRD-AC-014`  
**Change request:** `CRD-CR-2026-011`  
**Guardrails:** Every material statement cites evidence or is labelled inference; memo is not the final credit decision; invented thresholds rejected

## Objective
Generate a structured credit memo with the twelve required sections. Provenance coverage is 100% for material facts. `CreditMemo` remains assistance, never `HumanDecision`.

## Verification
- `python -m unittest tests.test_crd_ac_001_014_credit_memo`
- Prior suites remain green
- `python scripts/sdd_validate.py`
- Evidence: `evidence/sdd/CRD-FR-006__CRD-AC-001-014__20260910.md`

## Out of scope
GS-01 / GS-14 workbench memo screens. Human recording of the final decision.
