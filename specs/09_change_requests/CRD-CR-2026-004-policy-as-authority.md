# CRD-CR-2026-004 — Policy-as-authority

**CR ID:** `CRD-CR-2026-004`  
**Requested by:** Prompt 05 / `CRD-AC-007`, `CRD-AC-012`, `CRD-AC-014`  
**Date:** 2026-09-10  
**Approval:** Workshop-approved by the Prompt 05 instruction.

## Problem / change

Active `CREDIT-POLICY-3.2` and superseded v2.9 share the document corpus. Policy engine results exist as fixtures, but nothing selects the effective bundle by version/date or rejects invented thresholds. Similarity search can treat v2.9 as controlling.

## Why current spec is insufficient

`CRD-TOOL-004` states the rule; there was no data contract for the catalog, abstention, or policy-fidelity scan. `POLICY-001` is YAML only.

## Affected requirement IDs

`CRD-FR-005`, `CRD-SEC-002`, `CRD-TOOL-004`, `CRD-AC-007`, `CRD-AC-012`, `CRD-AC-014`

## Affected hard guardrails

Active policy is deterministic and versioned; generative output cannot modify it. Do not invent thresholds not in the case.

## Data / source / authority impact

Policy Engine + `CREDIT-POLICY-3.2` remain authoritative. v2.9 is historical reference only. Numeric literals allowed from active policy text: INR 5,000,000 (limit authority) and 7 days (bank freshness). No v2.9 threshold is stated in the fixture and MUST NOT be invented.

## Proposed spec text

See `CRD-DATA-007` and tightened `CRD-TOOL-004`.

## Implementation task(s)

`tasks/backlog/TASK-005-policy-as-authority.md`

## Verification evidence

`evidence/sdd/CRD-FR-005__CRD-AC-007-012-014__20260910.md`
