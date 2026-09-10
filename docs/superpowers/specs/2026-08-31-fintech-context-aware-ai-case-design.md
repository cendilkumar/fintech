# Fintech SME Credit Context-Aware AI Case — Design Specification

## Goal
Rebuild the supplied SME credit case around the architecture sequence Enterprise Data → Semantics/Ontology → Connected Knowledge → Graph → Hybrid Retrieval → Runtime Context → AI/Agent → Governance → Evidence/Feedback, then productize through PRD and Google AI Build.

## Domain boundary
Preserve the original business target and the strongest governance constraints: approved credit policy, reproducible material factors, customer/tenant isolation, fairness/impact evaluation, human oversight, manual fallback and traceability.

## Architecture decisions
- Participants derive semantics/ontology/KG from evidence; the repo supplies clues, not a completed solution.
- Heterogeneous sources are required so graph/retrieval/context concepts are necessary rather than decorative.
- AI remains advisory; deterministic policy and human authority are explicit.
- Decision trace captures inspectable artifacts and concise rationale, not hidden chain-of-thought.
- Workshop app simulates production interfaces but preserves architectural boundaries.

## Success
The repo is self-contained, all 15 scenarios have deterministic expected behavior, the PRD/build prompts contain no mandatory Qwen dependency, and automated checks validate integrity and critical controls.
