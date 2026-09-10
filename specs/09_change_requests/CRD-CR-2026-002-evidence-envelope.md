# CRD-CR-2026-002 — Material evidence envelope is mandatory

**CR ID:** `CRD-CR-2026-002`  
**Requested by:** Prompt 03 / modernization backlog P0-03  
**Date:** 2026-09-10  
**Approval:** Workshop-approved by the Prompt 03 instruction to implement provenance-bearing facts and test `CRD-AC-011`.

## Problem / change

`CRD-DATA-001` used SHOULD for envelope fields while `CRD-FR-002` requires source-specific semantics, provenance, freshness and unresolved conflict on every material AI-path fact. Prompt 03 names required fields. Without a MUST contract, an assembler can drop consent, period, or conflict state.

## Why current spec is insufficient

Envelope fields were optional. No executable conflict object existed. SME-L011 bank inflow and tax turnover could still be averaged after the type model forbade a shared `revenue` kind.

## Affected requirement IDs

`CRD-FR-002`, `CRD-DATA-001`, `CRD-AC-011`

## Affected acceptance / golden scenarios

`CRD-AC-011` / GS-11. Supporting: `CRD-AC-005`, `CRD-AC-006`.

## Affected hard guardrails

Stale, missing and conflicting evidence remains visible. Do not invent domain facts or alter fixtures.

## Data / source / authority impact

Material facts from LOS, Bank, Bureau, Tax/GST and Exposure MUST carry the envelope. Bank and tax remain separately authoritative. No blended revenue measure is permitted.

## Privacy / security / safety impact

Consent and purpose stay on the envelope. Bank remains purpose-limited (`UNDERWRITING_RUNTIME`).

## Backward compatibility / migration

Additive. `CRD-DATA-004` types unchanged. Fixtures unchanged.

## Proposed spec text

See updated `CRD-DATA-001` in `DATA_CONTRACTS.md`.

## Implementation task(s)

`tasks/backlog/TASK-003-evidence-contract.md`

## Verification evidence

`evidence/sdd/CRD-FR-002__CRD-AC-011__20260910.md` plus `python -m unittest tests.test_crd_ac_011_evidence_contract`.
