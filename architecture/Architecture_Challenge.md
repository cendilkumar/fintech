# Architecture Challenge

Design a production-target architecture for an **SME Credit Underwriting Intelligence Workbench** using the supplied evidence.

Your architecture must explicitly show:

1. Enterprise source layer and trust boundaries.
2. Semantic layer and ontology as separate but aligned concerns.
3. Entity resolution and canonical identity for organizations/natural persons.
4. Knowledge graph with fact-level provenance and temporal/version semantics.
5. Graph persistence/query approach.
6. Hybrid retrieval: structured + graph + vector + policy + memory.
7. Runtime context graph scoped by task, application, tenant, actor, time, source health and policy version.
8. AI/agent tool orchestration with deterministic boundaries.
9. Human credit authority and exception/adverse pathways.
10. Decision trace, evaluation/monitoring and governed feedback.

## Questions your design must answer

- How do you prevent bank inflow, tax turnover and statement revenue from becoming one ambiguous `revenue` field?
- How does the system know that three names refer to one organization—or that it cannot know with sufficient certainty?
- How is active policy selected while superseded versions remain searchable for audit?
- What happens when a key evidence source is stale or unavailable?
- How do you enforce tenant and restricted-attribute boundaries **before** retrieval/context assembly?
- Which controls are deterministic rather than prompt-based?
- What can the agent read, write and recommend?
- Which roles can make the actual credit decision?
- How is an adverse-factor pathway explained and traced without exposing hidden chain-of-thought?
- How do outcomes improve evaluation without becoming automatic training truth?
