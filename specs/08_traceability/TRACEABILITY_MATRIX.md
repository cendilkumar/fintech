# Traceability Matrix
    | Requirement | Business | Primary AC | Relevant AC numbers | Domain source | Seed task | Status |
|---|---|---|---|---|---|---|
| CRD-FR-001 | CRD-BR-002 | CRD-AC-001 | 001,002,003,005,011 | architecture/Decision_Guardrails.md; specs/05_data_contracts/DATA_CONTRACTS.md | tasks/backlog/TASK-006-runtime-context-graph.md | IN_PROGRESS |
| CRD-FR-002 | CRD-BR-002 | CRD-AC-011 | 003,004,005,011,013,016 | architecture/Decision_Guardrails.md; specs/05_data_contracts/DOMAIN_MODEL.md; specs/05_data_contracts/DATA_CONTRACTS.md | tasks/backlog/TASK-003-evidence-contract.md | IN_PROGRESS |
| CRD-FR-003 | CRD-BR-002 | CRD-AC-004 | 003,004 | architecture/Decision_Guardrails.md; specs/05_data_contracts/DATA_CONTRACTS.md | tasks/backlog/TASK-004-identity-resolution.md | IN_PROGRESS |
| CRD-FR-004 | CRD-BR-002 | CRD-AC-012 | 002,005,011,012 | architecture/Decision_Guardrails.md; specs/05_data_contracts/DATA_CONTRACTS.md | tasks/backlog/TASK-007-hybrid-retrieval.md | IN_PROGRESS |
| CRD-FR-005 | CRD-BR-003 | CRD-AC-012 | 003,006,007,008,009,012,013,014 | architecture/Decision_Guardrails.md; specs/05_data_contracts/DATA_CONTRACTS.md | tasks/backlog/TASK-010-injection-tenant-isolation.md | IN_PROGRESS |
| CRD-FR-006 | CRD-BR-003 | CRD-AC-001 | 001,002,005,010,011,014 | architecture/Decision_Guardrails.md; specs/05_data_contracts/DATA_CONTRACTS.md | tasks/backlog/TASK-012-evidence-grounded-memo.md | IN_PROGRESS |
| CRD-FR-007 | CRD-BR-003 | CRD-AC-002 | 002,003,006,007,008,013 | architecture/Decision_Guardrails.md; specs/05_data_contracts/DATA_CONTRACTS.md | tasks/backlog/TASK-008-credit-authority-gate.md | IN_PROGRESS |
| CRD-FR-008 | CRD-BR-003 | CRD-AC-005 | 005,006,010,014,015 | architecture/Decision_Guardrails.md; specs/05_data_contracts/DATA_CONTRACTS.md | tasks/backlog/TASK-011-credit-degraded-mode.md | IN_PROGRESS |
| CRD-FR-009 | CRD-BR-004 | CRD-AC-001 | 001,007,013,015 | architecture/Decision_Guardrails.md; specs/05_data_contracts/DATA_CONTRACTS.md | tasks/backlog/TASK-014-underwriting-trace.md | IN_PROGRESS |
| CRD-FR-010 | CRD-BR-004 | CRD-AC-015 | 015 | architecture/Decision_Guardrails.md; specs/05_data_contracts/DATA_CONTRACTS.md | tasks/backlog/TASK-015-governed-feedback.md | IN_PROGRESS |
| CRD-FR-011 | CRD-BR-003 | CRD-AC-007 | 002,003,006,007,008,013,014 | architecture/Decision_Guardrails.md; specs/05_data_contracts/DATA_CONTRACTS.md | tasks/backlog/TASK-008-credit-authority-gate.md | IN_PROGRESS |

    ## Status values
    `OPEN` → not yet demonstrated; `IN_PROGRESS` → implementation/evidence underway; `VERIFIED` → fresh evidence exists; `BLOCKED` → unresolved dependency or decision.

    Do not mark a row `VERIFIED` from documentation alone.

### Slice verification notes
- `CRD-AC-016` (semantic non-collapse): executable tests PASS — `tests/test_canonical_domain_model.py`; evidence `evidence/sdd/CRD-FR-002__CRD-AC-016__20260910.md`.
- `CRD-AC-011` (bank vs tax conflict, evidence contract): executable tests PASS — `tests/test_crd_ac_011_evidence_contract.py`; evidence `evidence/sdd/CRD-FR-002__CRD-AC-011__20260910.md`. Workbench UI / full GS-11 screen path remains unimplemented.
- `CRD-AC-004` (identity resolution): executable tests PASS — `tests/test_crd_ac_004_identity_resolution.py`; evidence `evidence/sdd/CRD-FR-003__CRD-AC-004__20260910.md`. Workbench adjudication UI remains unimplemented.
- `CRD-AC-007` / `CRD-AC-012` / `CRD-AC-014` (policy-as-authority): executable tests PASS — `tests/test_crd_ac_007_012_014_policy.py`; evidence `evidence/sdd/CRD-FR-005__CRD-AC-007-012-014__20260910.md`. Workbench GS-07 / GS-12 / GS-14 screens remain unimplemented.
- `CRD-AC-001` / `CRD-AC-005` / `CRD-AC-011` (runtime context graph): executable tests PASS — `tests/test_crd_ac_001_005_011_context_graph.py`; evidence `evidence/sdd/CRD-FR-001__CRD-AC-001-005-011__20260910.md`. Workbench GS-01 / GS-05 / GS-11 screens remain unimplemented.
- `CRD-AC-002` / `CRD-AC-005` / `CRD-AC-011` / `CRD-AC-012` (hybrid retrieval routing): executable tests PASS — `tests/test_crd_ac_002_005_011_012_retrieval.py`; evidence `evidence/sdd/CRD-FR-004__CRD-AC-002-005-011-012__20260910.md`. Workbench retrieval UI remains unimplemented.
- `CRD-AC-001` / `CRD-AC-014` (evidence-grounded memo): executable tests PASS — `tests/test_crd_ac_001_014_credit_memo.py`; evidence `evidence/sdd/CRD-FR-006__CRD-AC-001-014__20260910.md`. Workbench GS-01 / GS-14 screens remain unimplemented.
- `CRD-FR-006` stays `IN_PROGRESS` because the workbench memo UI and human-authorized outcome recording are not complete.
- `CRD-FR-001` stays `IN_PROGRESS` because the human-authorized outcome path is not complete.
- `CRD-AC-002` / `CRD-AC-007` (credit authority gate): executable tests PASS — `tests/test_crd_ac_002_007_authority_gate.py`; evidence `evidence/sdd/CRD-FR-007-011__CRD-AC-002-007__20260910.md`. Human-decision UI remains unimplemented.
- `CRD-FR-004` stays `IN_PROGRESS` because production vector/graph adapters and the workbench route inspector are not complete.
- `CRD-AC-003` / `CRD-AC-013` (person/guarantor boundary): executable tests PASS — `tests/test_crd_ac_003_013_person_impact.py`; evidence `evidence/sdd/CRD-SEC-008__CRD-AC-003-013__20260910.md`. Workbench GS-03 / GS-13 screens remain unimplemented.
- `CRD-AC-008` / `CRD-AC-009` (injection and tenant isolation): executable tests PASS — `tests/test_crd_ac_008_009_adversarial.py`; evidence `evidence/sdd/CRD-SEC-004-007__CRD-AC-008-009__20260910.md`. Workbench GS-08 / GS-09 screens remain unimplemented.
- `CRD-AC-005` / `CRD-AC-006` / `CRD-AC-010` (degraded underwriting): executable tests PASS — `tests/test_crd_ac_005_006_010_degraded.py`; evidence `evidence/sdd/CRD-FR-008__CRD-AC-005-006-010__20260910.md`. Workbench GS-05 / GS-06 / GS-10 screens remain unimplemented.
- `CRD-FR-008` stays `IN_PROGRESS` because the workbench degraded-mode UI is not complete.
- `CRD-AC-001`–`CRD-AC-015` (golden-scenario evaluation suite): executable tests PASS — `tests/test_crd_ac_001_015_eval_suite.py`; evidence `evidence/sdd/CRD-AC-001-015__eval_suite__20260910.md`. Contract-layer `QT-01` is MET; workbench GS screens remain unimplemented.
- `CRD-FR-009` / AT-16 / AT-17 (reconstructable underwriting trace): executable tests PASS — `tests/test_crd_fr_009_at16_at17_trace.py`; evidence `evidence/sdd/CRD-FR-009__AT-16-17__20260910.md`. Workbench Decision Trace screen remains unimplemented.
- `CRD-FR-009` stays `IN_PROGRESS` because the workbench trace UI is not complete.
- `CRD-FR-010` / `CRD-AC-015` (governed feedback write-path): executable tests PASS — `tests/test_crd_ac_015_governed_feedback.py`; evidence `evidence/sdd/CRD-FR-010__CRD-AC-015__20260910.md`. Workbench Outcome & Feedback screen remains unimplemented.
- `CRD-FR-010` stays `IN_PROGRESS` because production change-control operations and the feedback UI are not complete.
- Independent production-readiness pack: `PRODUCTION_READINESS_REVIEW.md`, `RELEASE_GATES.md`, `90_DAY_MODERNIZATION_ROADMAP.md`. Production release remains BLOCKED. No `CRD-FR-*` row is VERIFIED.
- Workbench display plane (2026-09-10): twelve screens in `src/credit_workbench` + `workbench/`; AT-01–AT-18 executable in `tests/test_workbench_at01_at18.py`; evidence `evidence/sdd/CRD-FR-001-011__workbench-ui__20260910.md`. G-UI-01 workshop screens exist; Human Decision / Trace / Feedback precede memo. Production HG-on-UI sign-off and G-RB-01 remain open. `CRD-FR-*` stay IN_PROGRESS.
- `CRD-FR-007` and `CRD-FR-011` stay `IN_PROGRESS` because the adverse/recourse workbench path (`CRD-AC-013`) is not complete.
- `CRD-FR-002` and `CRD-FR-003` stay `IN_PROGRESS` because human adjudication workflow and the AI path are not complete.
- `CRD-FR-005` stays `IN_PROGRESS` because remaining workbench gates are not complete.
