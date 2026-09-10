# CRD-CR-2026-005 — Runtime credit context graph

**CR ID:** `CRD-CR-2026-005`  
**Requested by:** Prompt 06 / `CRD-AC-001`, `CRD-AC-005`, `CRD-AC-011`  
**Date:** 2026-09-10  
**Approval:** Workshop-approved by the Prompt 06 instruction.

## Problem / change

Evidence envelopes, identity resolution and policy retrieval exist, but nothing assembles a task-specific connected slice. A repository dump would mix other applications, TENANT-BETA content, superseded policy, restricted eval attributes and historical memos into underwriting context.

## Why current spec is insufficient

`CRD-DATA-002` names the envelope fields; it does not define required node kinds, inclusion/exclusion reasons, or that historical memos are not `Policy` / objective truth. `CRD-TOOL-002` is a one-line stub.

## Affected requirement IDs

`CRD-FR-001`, `CRD-FR-004`, `CRD-DATA-002`, `CRD-TOOL-002`, `CRD-AC-001`, `CRD-AC-005`, `CRD-AC-011`

## Affected hard guardrails

Retrieve only authorized, relevant evidence. Stale, missing and conflicting evidence remains visible. Historical memos are not current policy. Restricted evaluation attributes do not enter runtime decision context by default. Tenant isolation before retrieval and display.

## Data / source / authority impact

Live application evidence + active `CREDIT-POLICY-3.2` + Policy Engine remain in-scope. `historical_case_narratives.jsonl` and `historical_decisions.jsonl` are historical only. `restricted_fairness_eval_sample.csv` is evaluation-only. v2.9 is not controlling.

## Proposed spec text

See expanded `CRD-DATA-002` and `CRD-DATA-008`.

## Implementation task(s)

`tasks/backlog/TASK-006-runtime-context-graph.md`

## Verification evidence

`evidence/sdd/CRD-FR-001__CRD-AC-001-005-011__20260910.md`
