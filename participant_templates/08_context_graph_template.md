# Template 08 — Runtime Context Graph

**Normative source:** `specs/05_data_contracts/DATA_CONTRACTS.md` (`CRD-DATA-002`, `CRD-DATA-008`). This worksheet is a readable extract, not a second authority.

## Context request contract

```json
{
  "task": "UNDERWRITE_APPLICATION",
  "application_id": "SME-L00x",
  "actor_role": "CREDIT_ANALYST",
  "actor_tenant": "TENANT-ALPHA",
  "as_of_time": "2026-09-15T10:00:00+05:30",
  "intent": "underwrite",
  "requested_action": "assemble_context",
  "context_budget": "target_application_only"
}
```

## Context node/section contract

For every included fact: value, entity, source, event time, freshness, authority, tenant, conflict state, provenance, `presented_as_current`.

Node kinds: Applicant, Entity, Application, Facility, Guarantor, Exposure, BureauRecord, BankEvidence, TaxEvidence, Policy, Exception, Decision, Evidence.

## Inclusion rules

Target application only. Actor tenant must match. Active `CREDIT-POLICY-3.2` + engine result. Material LOS/bank/bureau/tax/exposure/documents. Stale and conflicting facts stay in-graph with flags.

## Exclusion rules

| Code | What |
|---|---|
| `OTHER_APPLICATION` | Other live SME-L00x |
| `CROSS_TENANT` | TENANT-BETA (e.g. SME-L008) |
| `HISTORICAL_MEMO_NOT_POLICY` | `historical_case_narratives.jsonl`, `historical_decisions.jsonl` |
| `SUPERSEDED_POLICY` | CREDIT-POLICY-2.9 |
| `RESTRICTED_ATTRIBUTE` | `restricted_fairness_eval_sample.csv` |
| `IRRELEVANT_TO_TASK` | Source-case history dump |

## Scenario-specific context

### GS-01
SME-L001: MATCHED `ORG-001`, policy PASS, Decision PENDING (not APPROVE). Include/exclude reasons recorded.

### GS-02
Large limit uses engine `CREDIT_AUTHORITY`; not assembled as a second application dump.

### GS-05
SME-L005: BankEvidence `freshness_state=stale`, `presented_as_current=false`. Policy PASS does not clear stale. Exception `FRESHNESS`.

### GS-10
AI outage is source-health, not a missing policy node.

### GS-11
SME-L011: BankEvidence `CONFLICTS_WITH` TaxEvidence; both values remain; no blend.

### GS-13
Guarantor `NP-013` is a role PLAYED_BY a NaturalPerson Entity, not the borrower LegalEntity.

### GS-15
Historical outcomes stay excluded; they are not current HumanDecision.

## Update / invalidation

Rebuild when application id, actor tenant/role, as-of time, source health, identity state, policy version or material evidence envelopes change.
