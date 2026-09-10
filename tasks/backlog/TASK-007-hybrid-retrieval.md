# TASK-007 — Hybrid credit retrieval routing
**Status:** COMPLETED (CRD-AC-002 / 005 / 011 / 012 routing tests; workbench UI not in scope)  
**Requirements:** `CRD-FR-004`, `CRD-DATA-009`, `CRD-TOOL-001`–`004`  
**Acceptance focus:** `CRD-AC-002`, `CRD-AC-005`, `CRD-AC-011`, `CRD-AC-012`  
**Change request:** `CRD-CR-2026-006`  
**Guardrails:** vector similarity cannot override policy; do not blend bank/tax; do not invent missing facts; tenant filter before retrieval

## Objective
Route underwriting needs to structured, graph, semantic and policy-version adapters. Trace selected sources. Keep semantic/memory hops non-controlling.

## Verification
- `python -m unittest tests.test_crd_ac_002_005_011_012_retrieval`
- Prior suites remain green
- `python scripts/sdd_validate.py`
- Evidence: `evidence/sdd/CRD-FR-004__CRD-AC-002-005-011-012__20260910.md`

## Out of scope
Workbench retrieval UI, production vector index, full AC-008 security suite.
