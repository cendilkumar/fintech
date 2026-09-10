# Responsible AI Framework — SME Credit Underwriting Intelligence Workbench

**Organization:** NexLend SME Finance (fictional)  
**Compiled:** 2026-09-10  
**CRD IDs:** `CRD-SEC-001`–`012`, `CRD-FR-006`–`011`, `CRD-DATA-011`–`016`, `CRD-AC-003`, `CRD-AC-013`, `CRD-AC-015`, HG-01–HG-08  
**Sources:** `architecture/Decision_Guardrails.md`, `evidence/02_documents/fairness_and_impact_evaluation_policy.md`, `human_authority_and_recourse_policy.md`, `artefacts/GOVERNANCE_FRAMEWORK.md`  
**Companions:** `artefacts/AI_RISK_REGISTER.md`, `artefacts/AI_GOVERNANCE_PLAYBOOK.md`  
**Status:** Target Responsible AI (RAI) framework. **Does not** invent a legal fairness cutoff, sector-wide regulatory classification, or production GO. Segment diagnostics are **not** a compliance finding.

**North star:** AI may retrieve, reconcile, explain and draft. Humans and deterministic policy remain the authority for credit, adverse, exception and recourse. The LLM is not the architecture.

---

## 1. Scope and roles of AI

| AI may | AI must not |
|---|---|
| Extraction assistance, discrepancy explanation, retrieval planning, evidence summary, memo draft, next-evidence questions, business-language explanation of **engine** results | Approve, decline, condition, price, change a facility, authorize large limits, approve exceptions, issue adverse determinations, rewrite policy/ontology/prompts/models/gold, use restricted attributes as default decision features, fabricate missing bureau/bank/policy, follow document instructions |

Outputs are `Recommendation` / draft `CreditMemo` with `required_authority`. They are not `HumanDecision`. `PolicyEvaluation.PASS` is not `APPROVE`.

---

## 2. Fairness controls

From the ACTIVE fairness policy and `CRD-DATA-011` / `CRD-SEC-005` / `CRD-SEC-008`.

| Control | Requirement | Proof |
|---|---|---|
| **Party-kind split** | Distinguish legal-entity SMEs, sole-trader **business**, and natural-person owners/guarantors. Do not collapse into one “customer.” | GS-03 `ORG-003` ≠ `NP-003`; GS-13 guarantor ≠ borrower |
| **Purpose split** | Runtime `UNDERWRITING_RUNTIME` ≠ `RISK_COMPLIANCE_EVAL` | HG-05; Fairness screen is a separate mode (P2-02) |
| **Restricted attributes** | Protected/sensitive attributes and `restricted_fairness_eval_sample.csv` are `EVALUATION_ONLY_APPROVED_PURPOSE`. `decision_feature_eligible=CONDITIONAL` is not a default feature | GS-03, GS-15 inject deny |
| **No invented personal attributes** | Age, gender, religion, caste, ethnicity, marital status, disability, nationality must not be generated as factors | Person-claim scan; GS-13 |
| **No invented legal threshold** | Segment diagnostics do **not** define a legal fairness cutoff | Fairness policy |
| **Historical labels** | Prior approve/decline encode policy-era and selection effects; not objective creditworthiness gold | GS-15; SC-11 |
| **Adverse grounding** | Adverse factor = `factor_code` + `source_evidence_id` + source. Bureau band is not an invented personal reason | GS-13 `POL-ARREARS-02` on `EXP-013` |

Fairness **evaluation** is allowed only under approved purpose, access and governance. Fairness **enforcement in runtime** is: keep restricted attrs out, keep party kinds split, keep humans on adverse/recourse.

---

## 3. Bias monitoring

Monitor **process and evidence bias**, not an invented disparate-impact statistic.

| Monitor | What “bias” means here | Method | Owner |
|---|---|---|---|
| Selection / label bias | Historical outcomes used as truth | Ban auto-gold from `AI_ACCEPTED` or portfolio rows; missing outcomes not invented | Model risk |
| Semantic collapse | Bank inflow treated as tax turnover / “revenue” | `CRD-AC-016`; GS-11 unblended measures | Credit Risk |
| Identity merge bias | Different names forced to one entity | GS-04 AMBIGUOUS; `canonical_candidate` hypothesis only | Credit Operations |
| Exception mix-up | Missing bureau queued as policy exception | GS-06 vs GS-07 modes | Credit Operations |
| Person/entity collapse | Sole trader or guarantor treated as org-only | GS-03 / GS-13 | Risk / compliance eval |
| Restricted-attr leakage | Eval sample or CONDITIONAL attrs in runtime | HG-05 counters = 0 | Security + Risk/compliance |
| Authority substitution | LOS assignment or AI used instead of engine role | GS-02; HG-01 | Credit authority |
| Representation in eval | Legal-entity vs sole trader vs guarantor distinguished in **eval-only** jobs | Fairness policy; no cutoff invented | Risk / compliance eval |

**Cadence:** each model/prompt/eval CR (`APPROVAL_WORKFLOWS.md`); GS suite on the claimed layer; eval-mode screen when built. Production cohort monitoring remains **NOT PROVEN** and must not inject restricted attrs into underwriting.

---

## 4. Explainability requirements

Explainability is **observable reconstructability**, not hidden chain-of-thought (`CRD-SEC-011`, AT-16/17).

A material AI-assisted statement MUST be explainable as:

1. **Evidence** — `evidence_id` / source system / freshness / authority (HG-03 = 100% of FACT statements, or memo blocked).
2. **Policy** — controlling `CREDIT-POLICY-3.2` rule ids from the **engine**, not generated prose (AT-16: generated text ≠ policy evidence).
3. **Retrieval** — family, tool, `controlling` flag (vector never controlling for policy).
4. **Uncertainty** — stale, missing, conflict, abstention, degraded mode disclosed (`CRD-FR-006`, `CRD-FR-008`).
5. **Inference label** — `[INFERENCE]` when not a source fact.
6. **Human action** — role, decision, reason when a credit outcome exists.
7. **Versions** — model, prompt, ontology, policy (`NONE` if unused).

**Forbidden as explanation:** `chain_of_thought` / `cot` / `hidden_reasoning` fields; “the model is confident”; OCR confidence as creditworthiness (SC-10).

Applicant-facing adverse explanation follows recourse policy: **human** decision + material reason + source + approved appeal path. AI must not issue that determination.

---

## 5. Human oversight model

Oversight is **role-and-engine based**, not a courtesy review of whatever the model said.

| Layer | Who | What they oversee |
|---|---|---|
| Pre-action gate | Deterministic `CRD-TOOL-005/006/004` | Access, tenant, injection, ACTIVE policy, required role |
| Assistance | `CREDIT_ANALYST` (and limited RM) | May request AI; may modify/reject draft; cannot exceed engine role |
| Exception | `SENIOR_UNDERWRITER` | GS-07 class; AI cannot `APPROVE_EXCEPTION` |
| Large limit / adverse / formal override | `CREDIT_AUTHORITY` | GS-02 / GS-13; AI cannot authorize or `ISSUE_ADVERSE` |
| Identity ambiguity | Existing human authority | GS-04; no silent merge |
| Fairness eval | `RISK_COMPLIANCE_EVAL` | Separate purpose; no runtime decision |
| Learning loop | Model risk + Credit Policy | `GOVERNED_REVIEW`; no auto-retrain |
| High-impact control change | Named human ≠ sole implementer | `DEFINITION_OF_DONE.md` |
| AI outage | Credit Operations | Manual path; engine role still applies (GS-10) |

Human override is **recorded** and does **not** automatically retrain a model or rewrite policy.

Sufficiency: engine `required_human_role` beats LOS `assigned_role`. `AI_AGENT` is never sufficient for final credit.

---

## 6. Transparency controls

| Audience | What must be visible | Must not claim |
|---|---|---|
| Analyst | Provenance, freshness, conflicts, policy version, required role, degraded mode, that the memo is assistance | “Application is approved” from AI |
| Credit authority | Engine route, grounded adverse factors, recourse text | Personal invented reasons |
| Audit | AT-16 envelope; no CoT | Workshop TAT as QT-05 |
| Risk/compliance eval | That they are in eval mode; segment diagnostics ≠ legal threshold | Runtime use of restricted attrs |
| Applicant (adverse/conditional) | Human decision, material reason/source, appeal path | AI as the decision-maker |
| Demo / exec | Layer: contract vs workbench vs production | Production GO; 89.5 or 142 as the 30-minute target |

Version and purpose metadata travel on envelopes and traces. Tenant isolation is visible as **denial**, not as leaked redaction of another tenant’s facts.

---

## 7. Escalation procedures

Detail in `AI_GOVERNANCE_PLAYBOOK.md` and `INCIDENT_RESPONSE_PLAN.md`. RAI-specific triggers:

| Trigger | Escalate to | Do not |
|---|---|---|
| Restricted attr in runtime / fairness sample leak | Security + Risk/compliance (HG-05, Sev 1) | Leave it in context “for the eval” |
| Invented personal attribute or ungrounded adverse | Credit authority + Credit Operations (GS-13) | Let AI decline |
| Segment report treated as legal finding | Risk/compliance + Legal (`OPEN_DECISION`) | Publish a cutoff |
| Historical label proposed as gold | Model risk (G-FB) | Auto-write gold |
| Sole trader/guarantor collapsed | Credit Operations + Risk/compliance | “Fix” by merging parties |
| User asks AI to approve / ignore policy | Security if document/injection; else L2 credit | Follow the request |
| Jurisdiction / licensing question | Qualified legal/compliance review | Guess in the PRD or model |

---

## 8. Regulatory obligations

This case **does not** assign a jurisdiction or licence. Obligations below are **workshop-binding controls** plus a **process** to involve qualified legal review. They are **not** a claim that NexLend is subject to a named statute.

| Obligation (workshop) | Binding control | Production legal overlay |
|---|---|---|
| No automated final credit without required human | HG-01, `CRD-FR-011` | Legal names applicable automated-decision rules — **OPEN** |
| Purpose limitation / minimization (bank, bureau, tax) | Envelopes; permissible-use policy | Legal basis / DPIA **NOT PROVEN** |
| Adverse reason + recourse | `CRD-SEC-009`; human + source + appeal path | Appeal **calendar** OPEN |
| Traceability of material factors | HG-03, AT-16 | Retention **days** OPEN (Legal) |
| Sensitive attributes not default features | HG-05 | Named protected-class list = Legal CR, not model invention |
| Fairness evaluation governance | Separate purpose; no invented cutoff | Legal threshold **forbidden to invent here** |
| Cross-tenant confidentiality | HG-04 | Production IAM ≠ workshop ALPHA/BETA |
| Model/prompt change control | Approval workflows; `FEEDBACK-001` | Model-risk file required if LLM goes live |

**Rule:** If a real deployment would need a regulatory classification, open `OPEN_DECISION` with Legal. Do not encode that classification in prompts or gold labels.

---

## 9. AI risk taxonomy

Full register: `artefacts/AI_RISK_REGISTER.md`. Taxonomy used there:

| Family | Harm |
|---|---|
| **R-AUTH** | AI or insufficient role exercises credit / adverse / exception / recourse |
| **R-POL** | Invented or superseded policy controls the outcome |
| **R-EVID** | Fabricated, blended, stale-as-current, or ungrounded facts |
| **R-ID** | Silent identity merge; person/entity collapse |
| **R-PRIV** | Restricted attributes or extra-tenant data in runtime |
| **R-INJ** | Untrusted text overrides instructions |
| **R-XAI** | Unreconstructable or CoT-as-audit explanation |
| **R-FB** | Feedback poisons policy/prompts/models/gold |
| **R-FAIR** | Eval used as runtime; invented legal cutoff; label bias |
| **R-OPS** | AI outage blocks credit path; fail-open during incident |

Likelihood/impact in the register are **workshop-informed** (golden scenarios designed to fail naive systems). They are not production actuarial estimates.

---

## 10. Fit with existing artefacts

| Need | Where it is operated |
|---|---|
| Change of model/prompt/eval/policy | `APPROVAL_WORKFLOWS.md` |
| Incident | `INCIDENT_RESPONSE_PLAN.md` |
| Day-2 ops | `OPERATIONS_RUNBOOK.md` |
| Release | `RELEASE_GATES.md` §5.3 still BLOCKED |

This framework does not staff fairness-eval production runs or close P2-02 (Fairness/Impact screen still unimplemented).
