# System Requirements — SME Credit Underwriting Intelligence Workbench

    ## Normative functional requirements
    ### CRD-FR-001
The system **MUST** construct task-specific runtime context from authorized, relevant evidence rather than indiscriminately dumping repository data.

The connected slice, inclusion/exclusion reasons and historical-memo non-authority are defined by `CRD-DATA-002` and `CRD-DATA-008`.
### CRD-FR-002
The system **MUST** preserve source-specific semantics, provenance, freshness, version and unresolved conflict in every material fact used by the AI path.

Canonical types and forbidden equivalences are defined by `CRD-DATA-004` and `specs/05_data_contracts/DOMAIN_MODEL.md`. Bank inflow, tax declared turnover and statement revenue remain distinct measures. Legal entity, sole-trader business and natural person remain distinct party kinds. A recommendation is not a human credit decision.
### CRD-FR-003
The system **MUST** resolve canonical identities only when evidence supports resolution; preserve ambiguity and conflicting observations when it does not.

Resolution states, suffix-only name equivalence and the unsafe-merge ban are defined by `CRD-DATA-006`.
### CRD-FR-004
The system **MUST** route retrieval by need across structured, graph, semantic/vector, policy/version-aware and controlled-memory retrieval.

Routing families, fusion and hop traces are defined by `CRD-DATA-009`. Vector similarity cannot override `CRD-TOOL-004`.
### CRD-FR-005
The system **MUST** apply deterministic access, policy, authority and hard-safety controls before any high-impact recommendation or action handoff.

Active policy selection and invented-threshold rejection are defined by `CRD-DATA-007` and `CRD-TOOL-004`. Affected-person, restricted-attribute and adverse-evidence rules are defined by `CRD-DATA-011`. Tenant isolation and untrusted-document handling are defined by `CRD-DATA-012` and `CRD-TOOL-006`.
### CRD-FR-006
The system **MUST** generate evidence-grounded analysis/recommendations with concise rationale, uncertainty/degraded-state disclosure and no fabricated missing facts.

Required memo sections, provenance coverage and the ban on treating a memo as the final decision are defined by `CRD-DATA-014`.
### CRD-FR-007
The system **MUST** require the domain-authorized human or deterministic authority for controlled decisions; AI output alone is never sufficient authority.

The action catalog, required-role sufficiency and recommendation authority field are defined by `CRD-DATA-010`.
### CRD-FR-008
The system **MUST** maintain graceful degraded operation when AI, graph, vector or external sources are stale/unavailable, with explicit abstention or conditional output when evidence is materially insufficient.

The four assistance modes and the ban on fabricated bureau/bank facts are defined by `CRD-DATA-013`.
### CRD-FR-009
The system **MUST** produce a reconstructable decision trace covering source evidence, retrieval route, context snapshot, controls, versions, recommendation, human action and outcome.

The envelope, the ban on hidden chain-of-thought and the ban on substituting generated text for policy evidence are defined by `CRD-DATA-003` and `CRD-TOOL-008`.
### CRD-FR-010
The system **MUST** use outcomes and feedback only through governed evaluation/change processes; do not silently rewrite policy, ontology, semantic definitions, prompts, models or gold labels.

The capture queue, write-protected destinations and `FEEDBACK-001` ban are defined by `CRD-DATA-016` and `CRD-TOOL-010`.

    ## Domain authority requirement
    ### CRD-FR-011
    The system **MUST NOT** allow AI output alone to exercise final credit decision, adverse/exception route and recourse authority; authority remains with underwriters and designated credit-authority roles and/or deterministic validated controls defined by the case.

`check_access_and_authority` and `handoff_recommendation` (`CRD-TOOL-005`, `CRD-TOOL-007`) are the deterministic controls. They cannot be replaced by prompt text.

    ## Source-of-truth rule
    When a generated interpretation conflicts with an authoritative source or active policy, the authoritative evidence/control wins and the conflict remains visible in the trace.
