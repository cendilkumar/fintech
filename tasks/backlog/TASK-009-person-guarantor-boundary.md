# TASK-009 — Natural-person and guarantor boundary
**Status:** COMPLETED (CRD-AC-003 / CRD-AC-013 contract tests; workbench UI not in scope)  
**Requirements:** `CRD-FR-005`, `CRD-SEC-005`, `CRD-SEC-008`, `CRD-SEC-009`, `CRD-DATA-011`  
**Acceptance focus:** `CRD-AC-003`, `CRD-AC-013`  
**Change request:** `CRD-CR-2026-008`  
**Guardrails:** SoleTraderBusiness ≠ NaturalPerson owner; Guarantor ≠ borrower entity; restricted eval attributes stay out of runtime; AI has no adverse or recourse authority; no invented personal attributes

## Objective
Assemble an affected-person analysis for sole-trader, owner and guarantor cases. Bind adverse factors only to source evidence. Reject generated personal attributes and unsupported adverse reasons.

## Verification
- `python -m unittest tests.test_crd_ac_003_013_person_impact`
- Prior suites remain green
- `python scripts/sdd_validate.py`
- Evidence: `evidence/sdd/CRD-SEC-008__CRD-AC-003-013__20260910.md`

## Out of scope
GS-03 / GS-13 workbench screens, recourse workflow UI, human-decision recording UI.
