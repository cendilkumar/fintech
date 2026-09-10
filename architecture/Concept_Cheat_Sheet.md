# Concept Cheat Sheet — SME Credit Context-Aware AI

| Concept | In this case |
|---|---|
| Enterprise data | LOS applications, documents, bureau, bank, tax/GST, exposures, policy-engine results, case events, historical decisions and outcomes. |
| Semantic layer | Canonical meanings for Party, ApplicantRole, revenue-like measures, evidence status, policy result, decision, exception, freshness and TAT. |
| Ontology | Domain concepts and relationships such as Application-HAS_APPLICANT-Party, Application-HAS_EVIDENCE-EvidenceItem and PolicyEvaluation-USES_POLICY-PolicyVersion. |
| Knowledge graph | Connected application, party, evidence, financial observations, policy runs, human roles, decisions and provenance. |
| Graph platform | Persists/traverses identity, evidence, policy and decision relationships; supports multi-hop questions. |
| Structured retrieval | Exact current application, financial observations, exposure and source-health facts. |
| Vector retrieval | Relevant credit-memo standards, expert notes and historical narratives. |
| Policy retrieval | Active deterministic rules and authority; must be version/status aware. |
| Memory retrieval | Prior approved interaction/decision/outcome records when purpose and tenant permit. |
| Runtime context graph | The task-specific, actor/tenant/time-aware connected slice supplied to AI assistance. |
| AI/agent | Retrieves, reconciles, explains and drafts; it does not acquire final credit authority. |
| Governance gate | Tenant/IAM, permissible use, policy engine, human authority, adverse-outcome/recourse and audit controls. |
| Feedback | Outcome/override/evaluation evidence that enters governed learning, not silent policy/model self-modification. |

## Core warning

A vector search result that says "approved" is not a credit decision. A policy-engine `PASS` is not the same thing as an authorized human `APPROVE`. An OCR confidence score is not confidence in creditworthiness.
