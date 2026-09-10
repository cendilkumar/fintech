# CRD-CR-2026-006 — Hybrid credit retrieval routing

**CR ID:** `CRD-CR-2026-006`  
**Requested by:** Prompt 07 / `CRD-AC-002`, `CRD-AC-005`, `CRD-AC-011`, `CRD-AC-012`  
**Date:** 2026-09-10  
**Approval:** Workshop-approved by the Prompt 07 instruction.

## Problem / change

Structured envelopes, the context graph and versioned policy retrieval exist as separate modules. Nothing classifies an underwriting need onto a retrieval family or records the selected sources. Vector/document similarity can still be treated as a policy authority path.

## Why current spec is insufficient

`CRD-FR-004` and `CRD-TOOL-001`–`004` name the families; there is no routing table, fusion rule or hop-trace contract.

## Affected requirement IDs

`CRD-FR-004`, `CRD-TOOL-001`, `CRD-TOOL-002`, `CRD-TOOL-003`, `CRD-TOOL-004`, `CRD-AC-002`, `CRD-AC-005`, `CRD-AC-011`, `CRD-AC-012`

## Affected hard guardrails

Active policy is deterministic and versioned; generative output and similarity cannot modify it. Tenant isolation before retrieval. Historical memos are not current policy.

## Data / source / authority impact

Numeric/current facts stay on structured sources. Relationships stay on the context graph. Narratives stay untrusted semantic/memory hits. Authoritative rules stay on `retrieve_active_policy` + Policy Engine.

## Proposed spec text

See `CRD-DATA-009` and tightened `CRD-TOOL-001` / `CRD-TOOL-003`.

## Implementation task(s)

`tasks/backlog/TASK-007-hybrid-retrieval.md`

## Verification evidence

`evidence/sdd/CRD-FR-004__CRD-AC-002-005-011-012__20260910.md`
