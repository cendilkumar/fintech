# TASK-002 — Canonical SME credit domain model
**Status:** COMPLETED (CRD-AC-016 inspectable; CRD-FR-002 remains IN_PROGRESS)  
**Requirements:** `CRD-FR-002`, `CRD-BR-002`, `CRD-DATA-004`  
**Acceptance focus:** `CRD-AC-016` (model contract); `CRD-AC-003`, `CRD-AC-004`, `CRD-AC-011`  
**Change request:** `CRD-CR-2026-001`  
**Guardrails:** entity/person distinction; source-specific financial semantics; recommendation ≠ decision

## Objective
Make the approved type system inspectable and reject the four forbidden collapses before any retrieval or memo work.

## Verification
- `python -m unittest tests.test_canonical_domain_model`
- `python scripts/sdd_validate.py`
- `python scripts/sanity_check.py`
- Evidence: `evidence/sdd/CRD-FR-002__CRD-AC-016__20260910.md`

## Out of scope
Evidence envelope runtime (`CRD-DATA-001` producer), entity-resolution workflow, policy engine, workbench UI.
