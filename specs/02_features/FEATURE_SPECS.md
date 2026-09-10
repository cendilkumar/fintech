# Feature Specifications

## F0 — Semantic Foundation
Implements `CRD-FR-002` (type semantics) and `CRD-DATA-004`.
- Exposes the approved party kinds, roles, measures, policy/decision objects and forbidden equivalences in `specs/05_data_contracts/DOMAIN_MODEL.md`.
- Rejects construction or mapping that collapses LegalEntity/NaturalPerson, bank inflow/tax turnover, BureauRecord/Exposure, or Recommendation/HumanDecision.
- Applicant and Guarantor remain roles; `PolicyEvaluation.PASS` is not `HumanDecision.APPROVE`.
- Inspectable via `CRD-AC-016`; scenario proof remains `CRD-AC-003`, `CRD-AC-004`, `CRD-AC-011`.

## F1 — Evidence & Context Explorer
Implements `CRD-FR-001` through `CRD-FR-004`.
- Assembles `CRD-DATA-001` envelopes for LOS, bank, bureau, tax/GST and exposure facts.
- Builds a task/actor/tenant/as-of context graph (`CRD-DATA-008`) connecting Applicant, Entity, Application, Facility, Guarantor, Exposure, BureauRecord, BankEvidence, TaxEvidence, Policy, Exception, Decision and Evidence.
- Shows included evidence, excluded evidence and reason for exclusion (`CRD-AC-001`).
- Exposes source, freshness, version, authority, consent/purpose and unresolved conflict. Stale bank remains visible and not current (`CRD-AC-005`).
- Does not average or silently choose among contradictory financial measures (`CRD-AC-011`).
- Keeps application / organization / natural person / guarantor / evidence identity resolution inspectable (`CRD-DATA-006`, `CRD-AC-004`).
- Does not treat `identifier_crosswalk.canonical_candidate` as a resolved match.
- Historical credit memos are not current policy or objective truth.
- Routes retrieval by need (`CRD-DATA-009`): structured for numeric/current facts; graph for ownership/guarantor/exposure; semantic for narrative/history; policy-version for authoritative rules. Selected sources are traced. Vector similarity cannot override policy (`CRD-AC-012`).

## F2 — Bounded AI Workbench
Implements `CRD-FR-005` through `CRD-FR-008` and `CRD-FR-011`.
- AI may analyze, summarize, compare and recommend only within approved tool/control boundaries.
- Deterministic gates execute outside free-form model generation.
- Active policy is retrieved by version/date (`CRD-TOOL-004`); superseded v2.9 cannot control (`CRD-AC-012`).
- Generated thresholds not in CREDIT-POLICY-3.2 are rejected (`CRD-AC-014`).
- True policy exceptions use the engine route and required senior role (`CRD-AC-007`).
- Deterministic authority gate (`CRD-DATA-010`): AI may assist/refer; it cannot approve, decline, condition, price, change a facility, authorize large limits, approve exceptions or issue adverse determinations (`CRD-FR-007`, `CRD-FR-011`). Every recommendation names the engine-required human role (`CRD-AC-002`).
- Sole-trader / guarantor processing keeps entity ≠ person, purpose limits, restricted-attribute exclusion, human oversight and grounded adverse factors (`CRD-DATA-011`, `CRD-AC-003`, `CRD-AC-013`).
- Tenant isolation and injection resistance are deterministic (`CRD-DATA-012`, `CRD-AC-008`, `CRD-AC-009`): filters run before retrieval; documents/memos are DATA; prompt text cannot override.
- Insufficient material evidence or missing active policy produces a degraded/conditional response or abstention (`CRD-DATA-013`, `CRD-AC-005`, `CRD-AC-006`, `CRD-AC-010`). The four modes stay distinct. Missing bureau/bank facts are never invented.
- Evidence-grounded credit memo assistance (`CRD-DATA-014`, `CRD-AC-001`, `CRD-AC-014`): required sections; every material statement cites evidence or is labelled inference; the memo is never the final credit decision.

## F3 — Decision Trace & Evaluation
Implements `CRD-FR-009` and `CRD-FR-010`.
- Captures observable evidence, context, routes, tools, controls, versions, result and authorized human/technical action (`CRD-DATA-003`, `CRD-TOOL-008`, AT-16, AT-17).
- Generated explanation cannot replace active-policy or Policy Engine evidence.
- Hidden chain-of-thought is not a trace field.
- Feedback enters governed evaluation/change control rather than automatic truth rewriting (`CRD-DATA-016`, `CRD-AC-015`, `FEEDBACK-001`). `AI_ACCEPTED` does not mutate `CREDIT-POLICY-3.2`.

## F4 — Failure Lab
Uses the existing 15 golden scenarios as executable/inspectable acceptance evidence, including normal, stale, identity-conflict, unauthorized-action, prompt-injection, outage, superseded-policy, clock/temporal and reconnect/replay conditions.
- Automated suite (`CRD-DATA-015`, `CRD-TOOL-009`, `CRD-AC-001`–`CRD-AC-015`): grades numerical fidelity, evidence grounding, identity resolution, policy version, authority, adverse-factor grounding, tenant isolation, injection resistance, conflict preservation, abstention, outage handling and hallucinated thresholds. Invented thresholds are a critical failure. `QT-01` cannot be claimed unless hard-gate scenarios pass.
