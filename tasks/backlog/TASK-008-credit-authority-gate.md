# TASK-008 — Credit authority gate
**Status:** COMPLETED (CRD-AC-002 / CRD-AC-007 gate tests; workbench UI not in scope)  
**Requirements:** `CRD-FR-007`, `CRD-FR-011`, `CRD-DATA-010`, `CRD-TOOL-005`, `CRD-TOOL-007`  
**Acceptance focus:** `CRD-AC-002`, `CRD-AC-007`  
**Change request:** `CRD-CR-2026-007`  
**Guardrails:** AI has no final credit authority; engine role overrides LOS assignment; recommendations are not HumanDecisions

## Objective
Block AI (and insufficient human roles) from approve/decline/condition/price/change, large-limit authorization, exception approval and adverse determination. Every recommendation names the engine-required human role.

## Verification
- `python -m unittest tests.test_crd_ac_002_007_authority_gate`
- Prior suites remain green
- `python scripts/sdd_validate.py`
- Evidence: `evidence/sdd/CRD-FR-007-011__CRD-AC-002-007__20260910.md`

## Out of scope
Human-decision UI, recourse workflow, full CRD-AC-013 adverse screen.
