# CRD-CR-2026-001 — Canonical SME credit domain model

**CR ID:** `CRD-CR-2026-001`  
**Requested by:** Prompt 02 / modernization backlog P0-02  
**Date:** 2026-09-10  
**Approval:** Workshop-approved by the Prompt 02 instruction to update specs before implementation.

## Problem / change

`CRD-FR-002` and `CRD-BR-002` require source-specific semantics, but the spec pack had no normative type system. Physical clues in `evidence/03_semantic_evidence/` are incomplete by design. Without approved types, implementation can collapse legal entity and individual, bank inflow and tax turnover, bureau facts and internal exposure, or recommendation and human decision.

## Why current spec is insufficient

- `DATA_CONTRACTS.md` defines envelopes, not canonical entities.
- `FEATURE_SPECS.md` F1 mentions identity inspectability but does not define types.
- `conflicting_terms.csv` records risks; it is not an approved ontology.
- No inspectable acceptance criterion existed for model-level non-collapse independent of a full workbench.

## Affected requirement IDs

`CRD-BR-002`, `CRD-FR-002`, `CRD-FR-003`, `CRD-FR-007`, `CRD-FR-011`, `CRD-SEC-001`, `CRD-SEC-008`

## Affected acceptance / golden scenarios

Primary: `CRD-AC-003` (GS-03), `CRD-AC-004` (GS-04), `CRD-AC-011` (GS-11).  
Supporting: `CRD-AC-002`, `CRD-AC-013`, `CRD-AC-014`.  
Added: `CRD-AC-016` (model-level semantic non-collapse; not a 16th golden scenario).

## Affected hard guardrails

Preserve application / organization / natural person / guarantor / evidence identity ambiguity. AI has no autonomous final credit authority. Active policy is not generative text.

## Data / source / authority impact

Introduces `CRD-DATA-004` and `specs/05_data_contracts/DOMAIN_MODEL.md`. Does not change source-system authority in `source_authority.yaml`. Does not invent production legal classifications.

## Privacy / security / safety impact

Makes Applicant and Guarantor roles, not party types, so sole-trader and guarantor cases cannot be treated as a single “customer.” Restricted attributes remain out of default decision features.

## Backward compatibility / migration

Additive spec. Original semantic-evidence files remain clues. Fixtures are not altered.

## Proposed spec text

See `specs/05_data_contracts/DOMAIN_MODEL.md`, `CRD-DATA-004` in `DATA_CONTRACTS.md`, Feature F0 in `FEATURE_SPECS.md`, and `CRD-AC-016`.

## Implementation task(s)

`tasks/backlog/TASK-002-semantic-model.md`

## Verification evidence

`evidence/sdd/CRD-FR-002__CRD-AC-016__20260910.md` plus `python -m unittest tests.test_canonical_domain_model`.
