# TASK-011 — Credit degraded mode
**Status:** COMPLETED (CRD-AC-005 / CRD-AC-006 / CRD-AC-010 contract tests; workbench UI not in scope)  
**Requirements:** `CRD-FR-008`, `CRD-FR-006`, `CRD-NFR-004`, `CRD-SEC-010`, `CRD-DATA-013`, `FALLBACK-001`  
**Acceptance focus:** `CRD-AC-005`, `CRD-AC-006`, `CRD-AC-010`  
**Change request:** `CRD-CR-2026-010`  
**Guardrails:** Stale/missing evidence stays visible; never fabricate bureau/bank; manual underwriting remains executable during AI outage

## Objective
Classify degraded assistance into continue / needs-evidence / AI-unavailable / mandatory-abstention. SME-L005 stale bank remains not current. SME-L006 missing bureau stays null. SME-L010 continues manually. Structured/policy retrieval outage abstains rather than inventing facts.

## Verification
- `python -m unittest tests.test_crd_ac_005_006_010_degraded`
- Prior suites remain green
- `python scripts/sdd_validate.py`
- Evidence: `evidence/sdd/CRD-FR-008__CRD-AC-005-006-010__20260910.md`

## Out of scope
GS-05 / GS-06 / GS-10 workbench screens. Production adapter outage telemetry.
