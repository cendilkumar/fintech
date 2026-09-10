# TASK-010 — Injection and cross-tenant isolation
**Status:** COMPLETED (CRD-AC-008 / CRD-AC-009 security tests; workbench UI not in scope)  
**Requirements:** `CRD-FR-005`, `CRD-NFR-002`, `CRD-SEC-004`, `CRD-SEC-007`, `CRD-DATA-012`, `CRD-TOOL-006`  
**Acceptance focus:** `CRD-AC-008`, `CRD-AC-009`  
**Change request:** `CRD-CR-2026-009`  
**Guardrails:** Tenant isolation before retrieval/display; documents and historical memos are DATA; prompt text cannot override filters

## Objective
Enforce `DATA-TENANT` on structured, search, graph, context, memory, tool and output layers. Treat applicant documents and historical memos as untrusted DATA (`DATA-DOC-INSTRUCTION`). Prove isolation is deterministic and not prompt-dependent.

## Verification
- `python -m unittest tests.test_crd_ac_008_009_adversarial`
- Prior suites remain green
- `python scripts/sdd_validate.py`
- Evidence: `evidence/sdd/CRD-SEC-004-007__CRD-AC-008-009__20260910.md`

## Out of scope
GS-08 / GS-09 workbench screens. Production vector/graph adapters.
