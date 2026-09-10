# TASK-013 — SME credit evaluation suite
**Status:** COMPLETED (CRD-AC-001–015 contract-layer suite; workbench UI not in scope)  
**Requirements:** `CRD-AC-001`–`CRD-AC-015`, `CRD-DATA-015`, `CRD-TOOL-009`, `CRD-NFR-007`  
**Acceptance focus:** all 15 golden scenarios; invented thresholds are a critical failure  
**Change request:** `CRD-CR-2026-012`  
**Guardrails:** Do not invent facts or extra credit thresholds; memo is not the final decision; `QT-01` only at the contract layer when hard gates pass

## Objective
Run one automated suite over GS-01–GS-15 that grades numerical fidelity, grounding, identity, policy version, authority, adverse-factor grounding, tenant isolation, injection resistance, conflict preservation, abstention, outage handling and hallucinated thresholds.

## Verification
- `python -m unittest tests.test_crd_ac_001_015_eval_suite`
- `python scripts/run_eval_suite.py`
- Prior suites remain green
- `python scripts/sdd_validate.py`
- Evidence: `evidence/sdd/CRD-AC-001-015__eval_suite__20260910.md` and `.json`

## Out of scope
Workbench GS screens. Reconstructable traces (Prompt 14). Governed feedback write-path (Prompt 15). Production `QT-01`.
