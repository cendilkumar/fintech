# CRD-CR-2026-003 — Explicit identity resolution states

**CR ID:** `CRD-CR-2026-003`  
**Requested by:** Prompt 04 / `CRD-FR-003` / `CRD-AC-004`  
**Date:** 2026-09-10  
**Approval:** Workshop-approved by the Prompt 04 instruction.

## Problem / change

`identifier_crosswalk.csv` prints one `canonical_candidate` (including `ORG-004`) against disagreeing LOS/bureau/tax observations. Evidence assembly currently used the LOS party id as `entity_ref` for every application, which silently treats SME-L004 as a single resolved entity.

## Why current spec is insufficient

`CRD-FR-003` and DOMAIN_MODEL §5.1 name MATCHED / AMBIGUOUS / UNRESOLVED but there was no data contract for when each applies, or for blocking downstream merge.

## Affected requirement IDs

`CRD-FR-003`, `CRD-AC-004`, `CRD-AC-003`, `CRD-DATA-004`

## Affected acceptance / golden scenarios

Primary: `CRD-AC-004` / GS-04. Supporting: `CRD-AC-003` (sole trader), GS-13 guarantor party split, GS-06 missing bureau.

## Affected hard guardrails

Preserve identity ambiguity when resolution evidence is insufficient. Do not invent matches. Do not alter fixtures.

## Data / source / authority impact

`canonical_candidate` is a hypothesis only. LOS remains workflow identity, not bureau/tax identity authority.

## Proposed spec text

See `CRD-DATA-006` in `DATA_CONTRACTS.md`.

## Implementation task(s)

`tasks/backlog/TASK-004-identity-resolution.md`

## Verification evidence

`evidence/sdd/CRD-FR-003__CRD-AC-004__20260910.md`
