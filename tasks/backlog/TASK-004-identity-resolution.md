# TASK-004 — Legal entity / applicant identity resolution
**Status:** COMPLETED (CRD-AC-004 contract tests; no adjudication UI)  
**Requirements:** `CRD-FR-003`, `CRD-DATA-006`  
**Acceptance focus:** `CRD-AC-004` (supporting `CRD-AC-003`)  
**Change request:** `CRD-CR-2026-003`  
**Guardrails:** do not silently merge uncertain identities; do not treat crosswalk candidates as MATCHED; do not collapse person and entity

## Objective
Resolve LOS / bureau / tax organization identity only when name and tax token agree. Emit MATCHED, AMBIGUOUS or UNRESOLVED. Keep sole-trader owners and guarantors in separate person clusters. Block unsafe downstream merge.

## Verification
- `python -m unittest tests.test_crd_ac_004_identity_resolution`
- Prior suites remain green
- `python scripts/sdd_validate.py`
- Evidence: `evidence/sdd/CRD-FR-003__CRD-AC-004__20260910.md`
