# CRD-CR-2026-010 — Credit degraded mode

**CR ID:** `CRD-CR-2026-010`  
**Requested by:** Prompt 11 / `CRD-AC-005`, `CRD-AC-006`, `CRD-AC-010`  
**Date:** 2026-09-10  
**Approval:** Workshop-approved by the Prompt 11 instruction.

## Problem / change

Stale bank, missing bureau and AI-outage flags exist on fixtures and on the context graph, but nothing classifies underwriting assistance into continue / needs-evidence / AI-unavailable / mandatory-abstention. Generated text can still treat a 12-day bank feed as current or invent a bureau score. AI outage has no explicit manual-continuity path.

## Why current spec is insufficient

`STALE-001` and `FALLBACK-001` are YAML. `CRD-FR-008` / `CRD-SEC-010` state the outcomes. There is no data contract for the four degraded modes or for refusing fabricated bureau/bank facts.

## Affected requirement IDs

`CRD-FR-008`, `CRD-FR-006`, `CRD-NFR-004`, `CRD-SEC-010`, `CRD-AC-005`, `CRD-AC-006`, `CRD-AC-010`

## Affected hard guardrails

Stale, missing and conflicting evidence remains visible. Manual underwriting remains available during AI outage. Do not fabricate missing bureau/bank evidence. HG-08 = true.

## Data / source / authority impact

SME-L005: bank `freshness_days=12`, health `BANK_DATA=STALE`, engine `PASS` + `DATA-FRESHNESS-BANK` (7-day rule). SME-L006: no `BUR-006`, health `CREDIT_BUREAU=UNAVAILABLE`, engine `INSUFFICIENT_EVIDENCE` / `DATA-BUREAU-REQ`. SME-L010: `AI_ASSIST=UNAVAILABLE`, engine `REQUIRES_CREDIT_AUTHORITY` / `AUTH-LIMIT-01`, limit `5,200,000`. Retrieval-family outage is a workshop override (no live GS row).

## Proposed spec text

See `CRD-DATA-013`.

## Implementation task(s)

`tasks/backlog/TASK-011-credit-degraded-mode.md`

## Verification evidence

`evidence/sdd/CRD-FR-008__CRD-AC-005-006-010__20260910.md`
