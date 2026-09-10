# TASK-003 — Multi-source material evidence contract
**Status:** COMPLETED (CRD-AC-011 contract tests; workbench UI not in scope)  
**Requirements:** `CRD-FR-002`, `CRD-DATA-001`, `CRD-DATA-004`  
**Acceptance focus:** `CRD-AC-011`  
**Change request:** `CRD-CR-2026-002`  
**Guardrails:** do not average conflicting facts; do not invent missing source values; do not alter fixtures

## Objective
Wrap LOS, bank, bureau, tax/GST and exposure facts in provenance-bearing envelopes and surface SME-L011 bank-inflow vs tax-turnover disagreement without blending.

## Verification
- `python -m unittest tests.test_crd_ac_011_evidence_contract`
- Prior semantic tests remain green: `python -m unittest tests.test_canonical_domain_model`
- `python scripts/sdd_validate.py`
- Evidence: `evidence/sdd/CRD-FR-002__CRD-AC-011__20260910.md`

## Out of scope
Entity-resolution workflow, policy-as-authority engine, credit memo, workbench screens.