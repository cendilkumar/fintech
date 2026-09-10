# TASK-006 — Runtime credit context graph
**Status:** COMPLETED (CRD-AC-001 / 005 / 011 contract tests; workbench UI not in scope)  
**Requirements:** `CRD-FR-001`, `CRD-DATA-002`, `CRD-DATA-008`, `CRD-TOOL-002`  
**Acceptance focus:** `CRD-AC-001`, `CRD-AC-005`, `CRD-AC-011`  
**Change request:** `CRD-CR-2026-005`  
**Guardrails:** no repository dump; stale/conflict stay visible; historical memos are not policy or truth; restricted eval attributes stay out of runtime context

## Objective
Assemble a task/actor/tenant/as-of graph connecting Applicant, Entity, Application, Facility, Guarantor, Exposure, BureauRecord, BankEvidence, TaxEvidence, Policy, Exception, Decision and Evidence. Record include/exclude reasons. Do not treat historical memos as current policy.

## Verification
- `python -m unittest tests.test_crd_ac_001_005_011_context_graph`
- Prior suites remain green
- `python scripts/sdd_validate.py`
- Evidence: `evidence/sdd/CRD-FR-001__CRD-AC-001-005-011__20260910.md`

## Out of scope
Hybrid retrieval (Prompt 07), memo UI, workbench screens, full AC-008 security suite.
