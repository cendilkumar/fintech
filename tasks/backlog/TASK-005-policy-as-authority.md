# TASK-005 — Policy-as-authority
**Status:** COMPLETED (CRD-AC-007 / 012 / 014 contract tests; workbench UI not in scope)  
**Requirements:** `CRD-FR-005`, `CRD-DATA-007`, `CRD-TOOL-004`  
**Acceptance focus:** `CRD-AC-007`, `CRD-AC-012`, `CRD-AC-014`  
**Change request:** `CRD-CR-2026-004`  
**Guardrails:** active policy is deterministic and versioned; generative output cannot invent thresholds, exception criteria, delegated authority or adverse rationale; do not apply v2.9; abstain when policy is unavailable

## Objective
Select CREDIT-POLICY-3.2 by version/status/as-of date. Treat Policy Engine rows as authoritative. Reject invented numeric thresholds. Keep v2.9 historical-only. Route SME-L007 from the engine exception result, not as missing data.

## Verification
- `python -m unittest tests.test_crd_ac_007_012_014_policy`
- Prior suites remain green
- `python scripts/sdd_validate.py`
- Evidence: `evidence/sdd/CRD-FR-005__CRD-AC-007-012-014__20260910.md`

## Out of scope
Credit-authority UI lock (Prompt 08), memo composition UI, workbench screens.
