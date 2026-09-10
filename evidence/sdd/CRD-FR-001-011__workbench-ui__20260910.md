# Acceptance Evidence
**Requirement ID(s):** CRD-FR-001–011, CRD-SEC-001–012, CRD-NFR-002/004/005, G-UI-01  
**Acceptance ID(s):** CRD-AC-001–015, AT-01–AT-18  
**Golden scenario(s):** GS-01–GS-15 on the workbench display plane (`src/credit_workbench`, `workbench/`). Contract-layer GS suite is unchanged.  
**Commit/diff reference:** one-shot workbench implementation over existing `credit_domain` gates  
**Command/check executed:**

```
python -m unittest tests.test_workbench_at01_at18 -v
python -m unittest tests.test_canonical_domain_model tests.test_crd_ac_001_015_eval_suite tests.test_crd_ac_008_009_adversarial -q
python scripts/sdd_validate.py
```

**Observed output:**
- 21 workbench tests OK (AT-01–AT-18, G-UI-01 screen order, five retrieval families, fairness eval-only)
- 24 prior contract tests OK
- SDD VALIDATION: PASS | files=32 | functional_requirements=11 | acceptance_criteria=16
- Twelve screens exist. Human Decision, Decision Trace and Outcome & Feedback precede Credit Memo in `SCREENS`. Memo assist is blocked unless those three flags are on. Isolation / authority / policy retrieve cannot be flagged off.
- GS-08 TENANT-ALPHA dossier for SME-L008 is `CROSS_TENANT` with empty content; applicant name is not displayed.
- GS-14 invented INR 2,500,000 probe is rejected as `PolicyFidelityError`.
- Feedback `AI_ACCEPTED` queues `GOVERNED_REVIEW`; POLICY_BUNDLE write is blocked.
- Trace includes AT-16 required fields; `versions.model=NONE`; no hidden CoT field on the trace object.

**Hard guardrail result:** PASS for HG display on the workbench service path. Gates remain in `credit_domain` (`check_access_and_authority`, `retrieve_active_policy`, tenant isolation). Fixtures were not modified.  
**Acceptance result:** PASS for AT-01–AT-18 on the workbench service/API path. Production GO is not claimed. `CRD-FR-*` remain IN_PROGRESS.  
**Evidence files:**
- `src/credit_workbench/`
- `workbench/index.html`, `workbench/app.js`, `workbench/styles.css`
- `scripts/run_workbench.py`
- `tests/test_workbench_at01_at18.py`
**Human/technical authority outcome (if applicable):** Screens display required human role and deny AI final credit. They do not become the control plane.  
**Known limitations:** No live LLM (`model.generation=off`, stub memo). Graph ADR still unfilled. Production adapters, durable audit store and G-RB-01 drill remain open. Workshop TAT is not the 30-minute business target.
