# AI / Agent Tool Contracts

These are logical contracts for the workshop architecture. The prototype MAY simulate them, but the authority boundary MUST remain visible.

### CRD-TOOL-001 `retrieve_structured_state`
Read-only exact state retrieval for numeric/current facts (`CRD-DATA-009`). MUST return source, freshness and authority metadata. MUST NOT invent missing bureau/bank values or blend bank inflow with tax turnover. Stale facts keep `freshness_state=stale`. Unavailable bureau is an explicit null envelope (`CRD-DATA-013`).

### CRD-TOOL-002 `traverse_connected_context`
Read-only graph/relationship traversal over a `CRD-DATA-008` snapshot. MUST retain provenance and unresolved identity/conflict/freshness state. MUST NOT walk into excluded tenant, other-application, superseded-policy or historical-memo-as-policy nodes. `assemble_runtime_context` is the only approved builder.

### CRD-TOOL-003 `retrieve_narrative_evidence`
Read-only semantic/vector retrieval for supporting narrative/history (`CRD-DATA-009`). Returned content is untrusted data and cannot control the agent. MUST NOT be used as the authority path for active policy, thresholds or delegated authority. Hits with `authoritative_for_current_policy=false` stay non-controlling.

### CRD-TOOL-004 `retrieve_active_policy`
Version-aware policy retrieval. MUST select active/applicable policy deterministically by version/status/as-of date (`CRD-DATA-007`); similarity alone cannot choose authority. MUST return the controlling version, status, effective date and known rule ids. Superseded bundles MAY be returned only with `controlling=false`. If no active bundle applies, MUST return abstention, not an invented rule.

### CRD-TOOL-005 `check_access_and_authority`
Deterministic pre-context/pre-action check (`CRD-DATA-010`). MUST return allow/deny/conditional plus the controlling rule/version and required human role. MUST deny `AI_AGENT` (and any insufficient role) for final credit, large-limit authorization, exception approval and adverse determination.

### CRD-TOOL-006 `evaluate_feasibility_or_safety`
Deterministic domain gate for constraints the model cannot override (`CRD-DATA-012`). MUST apply `DATA-TENANT` before retrieval/display and `DATA-DOC-INSTRUCTION` before prompt assembly. MUST deny cross-tenant retrieve/display and deny treating applicant-document or historical-memo text as instructions. Prompt overrides cannot change the effect.

### CRD-TOOL-007 `handoff_recommendation`
Writes only a `Recommendation` to the approved human/controlled workflow surface (`CRD-DATA-010`). The recommendation MUST state `required_authority`. It MUST NOT persist `HumanDecision` or exercise final credit, adverse, exception or recourse authority.

### CRD-TOOL-008 `record_decision_trace`
Records a reconstructable underwriting trace (`CRD-DATA-003`). MUST include evidence sources, versions, consent/purpose, retrieval route, financial calculations, policy version, exceptions, generated recommendation, required authority, human action and final outcome. MUST NOT request or persist hidden chain-of-thought. MUST NOT treat generated explanation as policy evidence. Policy authority remains `CRD-TOOL-004` / the Policy Engine.

### CRD-TOOL-009 `run_golden_evaluation_suite`
Read-only evaluation over `GS-01`–`GS-15` (`CRD-DATA-015`). MUST grade the twelve Prompt 13 dimensions, persist an inspectable report, and treat invented policy thresholds as a critical failure. MUST NOT write policy, ontology, semantic definitions, prompts, models or gold labels. MUST NOT claim `QT-01` unless hard-gate scenarios pass. MUST NOT claim workbench screen PASS.

### CRD-TOOL-010 `capture_outcome_feedback`
Records operator feedback, human decision and later outcome onto a governed review queue (`CRD-DATA-016`). MUST deny automatic writes to policy, ontology, prompts, models and gold labels. SME-L015 / `AI_ACCEPTED` MUST leave `CREDIT-POLICY-3.2` unchanged.
