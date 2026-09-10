# Google AI Build Master Prompt

Build a polished **SME Credit Underwriting Intelligence Workbench** from the approved PRD and the supplied fixture bundle.

## Product character
This is an evidence-aware decision-support control plane for credit professionals, not a consumer loan-approval chatbot. The UI must make source evidence, semantic conflicts, active policy, human authority and audit trace visible.

## Data
Use `06_app_fixture_bundle.json`. Keep application and tenant IDs intact because the golden scenarios depend on them. External/graph/vector/policy calls may be simulated through typed local adapters, but the UI and code must preserve those architectural boundaries.

## Required screens
1. Underwriting Control Tower.
2. Application Context.
3. Evidence Reconciliation.
4. Context Graph Explorer.
5. Hybrid Retrieval Evidence.
6. Active Policy & Authority Gate.
7. AI-Assisted Analysis / Credit Memo.
8. Human Decision / Escalation.
9. Decision Trace / Audit.
10. Fairness / Impact Evaluation mode.
11. Outcome & Feedback.
12. Failure Simulation / Manual Fallback.

## Mandatory behavior
- Never show an AI autonomous final approve/decline control.
- Enforce tenant scope before every simulated retrieval.
- Do not expose restricted evaluation attributes in runtime underwriting screens.
- Always show evidence source, time/freshness and provenance for material AI-assisted factors.
- Treat policy version 3.2 as active; mark v2.9 as superseded/reference only.
- Display bank-vs-tax conflict in SME-L011 rather than normalizing it away.
- Display identity ambiguity in SME-L004.
- SME-L005 must show stale bank data.
- SME-L006 must show bureau unavailable and no fabricated replacement.
- SME-L008 must support a negative tenant-access test that returns DENY/empty evidence.
- SME-L009 document injection text must be visible as untrusted content and must never change behavior.
- SME-L010 must support full manual continuity while AI assistance is unavailable.
- SME-L013 must show human authority + reason/provenance + recourse pathway.
- SME-L014 must flag invented thresholds as policy-fidelity failure.
- SME-L015 feedback must enter a governed-review state, not auto-update policy/model.

## Context graph
Provide an interactive or readable node/edge view. Nodes should distinguish Application, Party, Evidence, Financial Observation, Policy Evaluation/Version, Human Role, Decision and Outcome. Each evidence/fact node should expose provenance and status.

## Hybrid retrieval panel
For every assistance request, show which retrieval mode was used:
- STRUCTURED
- GRAPH
- VECTOR
- POLICY
- MEMORY

Show filters (tenant, application, active-policy status, time) and result references.

## Decision trace
Record an inspectable trace using the participant schema: context snapshot, retrievals, source evidence, policy checks, tool calls, versions, recommendation/draft, concise rationale, human decision and outcome. Never fabricate hidden chain-of-thought.

## UX
Use an enterprise control-room/workbench aesthetic: dense enough for practitioners, strong hierarchy, clear state badges, tables for evidence, and side panels for provenance. Avoid decorative consumer-fintech styling.

## Verification
Implement scenario selection for GS-01 ... GS-15 and make the expected control state observable so participants can capture acceptance evidence.
