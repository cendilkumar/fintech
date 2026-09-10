# TASK-001 — Implement evidence-aware underwriting context assembly
**Status:** BACKLOG  
**Requirements:** `CRD-FR-001`, `CRD-FR-002`, `CRD-FR-003`, `CRD-FR-004`, `CRD-FR-005`, `CRD-FR-008`, `CRD-FR-009`  
**Acceptance focus:** `CRD-AC-004`, `CRD-AC-005`, `CRD-AC-010`, `CRD-AC-011`, `CRD-AC-013`, `CRD-AC-015`

## Objective
Build or refine the prototype path that assembles one SME application context without collapsing bank inflow, tax turnover and statement revenue, while enforcing tenant, freshness, policy and affected-person boundaries.

## Before implementation
- Run `/sdd-discover` with the requirement and AC IDs above.
- Identify current prototype/fixture path from `google_ai_build/` and scripts.
- Identify exact source authority/freshness rules in `evidence/`.
- Produce `/sdd-plan`; do not code around an ambiguous domain rule.

## Definition of implementation evidence
- targeted scenario outputs for the acceptance focus;
- context/decision trace showing included/excluded evidence and controls;
- `python scripts/sdd_validate.py` PASS;
- original `scripts/sanity_check.py` PASS;
- traceability row status updated only when verified.
