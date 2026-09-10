# PRD Generation Prompt — SME Credit Underwriting Intelligence Workbench

Use this only **after** Stages 1–8 are completed and reviewed.

## Prompt

You are converting an approved AI FDE architecture into a build-ready Product Requirements Document for a fictional multi-tenant SME-credit underwriting workbench.

### Source of truth
Use only:
- completed participant architecture templates;
- supplied case/evidence;
- accepted ADRs;
- evaluation thresholds and golden scenarios.

### Do not invent
Do not invent a missing permission, lending threshold, human authority, active policy rule, regulatory conclusion, source contract or model capability. Record unresolved items as `OPEN_DECISION` with owner and required evidence.

### Product boundary
The application provides evidence-aware underwriting assistance. AI may retrieve, reconcile, explain and draft. It must not receive autonomous final credit authority or change active policy.

### Required PRD sections
1. Product context, users, goals, non-goals.
2. User roles, tenant boundaries and decision authority.
3. Primary, exception, adverse, failure and manual workflows.
4. Functional requirements with `FR-###` identifiers.
5. Semantic layer requirements.
6. Ontology/KG/entity-resolution requirements.
7. Source/data/provenance/freshness requirements.
8. Hybrid retrieval requirements.
9. Runtime context-graph requirements.
10. AI/agent/tool requirements.
11. Deterministic policy and human-control requirements.
12. Decision trace/audit/feedback requirements.
13. Security/privacy/permissible-use/fairness-impact requirements.
14. Non-functional requirements.
15. UI/screen requirements.
16. Evaluation requirements mapped to GS-01 ... GS-15.
17. Architecture/interfaces and workshop-vs-production mapping.
18. Given/When/Then acceptance criteria.
19. Traceability matrix: evidence → architecture decision → PRD requirement → app component → scenario/test.
20. Open decisions/excluded capabilities.

### Mandatory constraints
- active policy is version-aware and deterministic;
- policy PASS is not final human APPROVE;
- cross-tenant access is denied before retrieval/context assembly;
- restricted fairness attributes are not runtime decision features by default;
- missing/stale/conflicting evidence is visible;
- prompt injection in documents is untrusted content;
- adverse/exception pathways preserve human authority and recourse;
- decision trace stores concise rationale/evidence, not hidden chain-of-thought;
- feedback does not auto-modify policy/model/ontology.

Return a complete implementation-grade PRD, not a product-marketing summary.
