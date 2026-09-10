# Template 09 — AI / Agent Execution and Controls

## 1. Agent objective

State the bounded underwriting-support job.

## 2. State machine / workflow

Define states such as request validation, policy pre-check, retrieval planning, evidence retrieval, context assembly, recommendation, policy post-check, human review, action handoff and trace finalization if justified by your design.

## 3. Tool registry

| Tool | Purpose | Inputs | Outputs | Read/Write | Permission check | Failure behavior |
|---|---|---|---|---|---|---|
| | | | | | | |

## 4. Deterministic controls

| Control | Enforcement point | Input | Decision | Agent behavior on deny |
|---|---|---|---|---|
| | | | | |

## 5. Human gates

Map recommendation/decision type → required role → approval/reject/modify/escalate behavior.

## 6. Uncertainty / abstention

Define when the agent must abstain versus produce a degraded recommendation.

## 7. Prompt-injection / untrusted-content rule

Define how retrieved/user-provided operational text is separated from system/policy instructions.

## 8. AI outage

Define the manual continuity experience.
