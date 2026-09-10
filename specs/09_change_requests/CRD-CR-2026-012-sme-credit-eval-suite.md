# CRD-CR-2026-012 — SME credit evaluation suite

**CR ID:** `CRD-CR-2026-012`  
**Requested by:** Prompt 13 / `CRD-AC-001`–`CRD-AC-015`  
**Date:** 2026-09-10  
**Approval:** Workshop-approved by the Prompt 13 instruction.

## Problem / change

Slice tests exist per acceptance criterion, but there is no single automated suite that runs all 15 golden scenarios and grades the Prompt 13 dimensions. Invented thresholds can be treated as a local test instead of a suite-level critical failure. `QT-01` has no executable claim rule.

## Why current spec is insufficient

`golden_scenarios.json`, `evaluation_matrix.csv` and `acceptance_thresholds.yaml` are fixtures. They do not execute. Hard gates HG-01–HG-08 and `QT-01` are not aggregated into a stored suite report.

## Affected requirement IDs

`CRD-AC-001`–`CRD-AC-015`, `CRD-NFR-007`, `CRD-DATA-015`, `CRD-TOOL-009`

## Affected hard guardrails

Invented policy thresholds are a critical failure (HG-02). AI has no autonomous final credit authority (HG-01). Tenant isolation, injection resistance, superseded-policy non-control, restricted attributes, provenance coverage and manual fallback remain hard gates. `QT-01` cannot be claimed unless hard-gate scenarios pass.

## Data / source / authority impact

Uses existing live fixtures SME-L001–SME-L015 and `evidence/06_evaluations/`. Does not modify original case evidence. Does not grant AI final credit authority. GS-15 is graded on the twelve dimensions plus write-protection of policy/ontology/gold labels; governed feedback capture remains Prompt 15.

## Proposed spec text

See `CRD-DATA-015` and `CRD-TOOL-009`.

## Implementation task(s)

`tasks/backlog/TASK-013-sme-credit-eval-suite.md`

## Verification evidence

`evidence/sdd/CRD-AC-001-015__eval_suite__20260910.md`
