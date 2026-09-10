# Template 11 — Outcome, Feedback and Learning Loop

## Feedback types

| Feedback type | Example | Authority | Can update operational truth automatically? | Review required? |
|---|---|---|---|---|
| Event feedback | | | | |
| Human accept/reject/modify | | | | |
| Operational outcome | | | | |
| Evaluation/adjudication | | | | |

## Learning destinations

For each destination below, define evidence threshold, owner, review gate, versioning and rollback:

- historical decision memory;
- golden/evaluation sets;
- semantic definitions;
- ontology/KG schema;
- KG facts;
- retrieval policy/index;
- model/prompt configuration;
- policy bundle;
- operational workflow.

## Anti-patterns to prevent

- accepted recommendation automatically becomes ground truth;
- rejected recommendation automatically becomes a negative label;
- model output writes directly into authoritative lending/decision sources;
- feedback updates policy without approval;
- history loses the original evidence/version after correction.
