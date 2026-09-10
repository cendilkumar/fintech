# Product Requirements Document — SME Credit Underwriting Intelligence Workbench

**Organization:** NexLend SME Finance (fictional)  
**Product:** SME Credit Underwriting Intelligence Workbench  
**Requirement prefix:** `CRD`  
**Status:** Derived artefact compiled 2026-09-10 from approved specifications. Not a production GO.  
**Normative sources:** `specs/` (especially `specs/00_product/PRD.md`), `architecture/Decision_Guardrails.md`, `specs/08_traceability/TRACEABILITY_MATRIX.md`, `evidence/sdd/`, `PRODUCTION_READINESS_REVIEW.md`, `RELEASE_GATES.md`  
**This file does not replace the SDD pack.** If this artefact and an approved spec disagree, the approved spec wins. This file does not mark any `CRD-FR-*` row `VERIFIED`.

**CRD IDs compiled:** `CRD-BR-001`–`004`, `CRD-FR-001`–`011`, `CRD-AC-001`–`016`, `CRD-NFR-001`–`007`, `CRD-SEC-001`–`012`, `CRD-DATA-001`–`016`, `CRD-TOOL-001`–`010`.

---

## 1. Product vision

NexLend finances SMEs through working-capital, invoice-finance and term-loan products. Underwriting today is mature but fragmented: a single application can require an analyst to reconcile LOS, applicant documents, bureau, bank, tax/GST, exposure, deterministic policy, prior case notes and authority rules.

The product vision is **not** a credit chatbot. It is:

> Construct a trustworthy, semantically consistent, policy-aware context for an underwriter — and prove what evidence, policy version, tools and human authority produced each outcome.

**Core storyline:** Data → Meaning → Relationships → Retrieval → Context → Reasoning → Controlled Decision Support → Feedback.  
**Core principle:** The LLM is not the architecture. AI may retrieve, reconcile, explain and draft. It has no autonomous final credit, adverse, exception or recourse authority (`CRD-FR-011`, `CRD-SEC-001`).

Companions: `artefacts/PRODUCT_STRATEGY.md`, `artefacts/SUCCESS_METRICS.md`.

---

## 2. Product context

### 2.1 Problem

Source-case operating baseline (`evidence/01_enterprise_sources/source_case_baseline.json`):

| Measure | Value | May be used as |
|---|---|---|
| Median uncomplicated-case TAT | 142 minutes | Operating baseline only |
| P90 TAT | 648 minutes | Operating baseline only |
| Document rework | 31.2% | Operating baseline only |
| Sampled cases with >3 manual system lookups | 57% | Operating baseline only |
| Median memo preparation | 38 minutes | Operating baseline only |
| Policy-rule exceptions | 8.4% | Operating baseline only |
| Audit sample missing a reproducible source reference | 13.7% | Operating baseline only |
| Business target | <30 minutes uncomplicated TAT | `CRD-BR-001` / QT-05; **NOT PROVEN** |

The 160-row workshop fixture (median **89.5** minutes, P90 **218**) is a different population (`CRD-NFR-007`). Do not present fixture statistics as the operating baseline or as achievement of the 30-minute target.

Current friction (case study §2): heterogeneous financial evidence; copy-paste between document, LOS and memo systems; policy results not always linked to memo evidence; missing evidence and true policy exceptions entering similar queues; identity mismatch across tax/bank/bureau; OCR confidence treated as business confidence; historical outcomes encoding prior policy; free-text memos mixing facts, judgments and narrative.

### 2.2 Product boundary

The workbench is **evidence-aware underwriting assistance** over synthetic workshop fixtures for this repository, and a production-shaped design for later live adapters. Authoritative source systems remain LOS, Document Store, Commercial Bureau, Bank Data, Tax/GST, Exposure, Credit Policy Engine, Case Management and Memo Repository.

`PolicyEvaluation.PASS` is not `HumanDecision.APPROVE`. A generated memo is not a credit decision. `AI_ACCEPTED` is not ground truth or a policy write.

---

## 3. Business objectives

| ID | Objective | Success is not |
|---|---|---|
| `CRD-BR-001` | Reduce uncomplicated-case turnaround to **under 30 minutes** without weakening policy, evidence traceability, tenant isolation, fairness/impact evaluation, human credit authority, recourse, fallback or auditability | Reporting 89.5 or 142 minutes as the product result |
| `CRD-BR-002` | Transform fragmented evidence into semantically consistent, provenance-bearing, task-specific context without fabricating certainty | Dumping the repository into a prompt |
| `CRD-BR-003` | Keep AI bounded by deterministic policy/access/safety controls and designated human credit-authority roles | Prompt-only “please don’t approve” |
| `CRD-BR-004` | Make every material recommendation or controlled workflow outcome reconstructable | Hidden chain-of-thought logs |

Hard domain-control gates pass **first**. Usefulness, latency, burden reduction and recommendation quality are judged only after those invariants (`specs/00_product/PRD.md` success model).

---

## 4. Customer value proposition

**For** NexLend credit analysts, senior underwriters and credit-authority officers  
**who** must underwrite SME facilities across nine fragmented systems without losing provenance or authority  
**the workbench** assembles a task-specific, policy-version-aware context, grounds AI draft assistance in evidence, and records a reconstructable trace  
**unlike** a generic credit chatbot or an unscoped document dump  
**because** tenant isolation, active `CREDIT-POLICY-3.2`, human gates and conflict/freshness visibility are deterministic controls — not model obedience.

Value the product may claim only after hard gates:

- fewer unlinked memo factors (baseline 13.7% missing source reference);
- fewer unnecessary multi-system lookups (baseline 57% of sampled cases >3 lookups);
- shorter memo preparation (baseline median 38 minutes) **without** inventing facts or policy;
- TAT improvement toward <30 minutes **only** on a named production population.

Workshop contract-layer evidence does not by itself prove those operating improvements.

---

## 5. User personas and authority

Personas are taken from `evidence/04_policy_authority/role_authorization_matrix.csv` and `CRD-DATA-010`. No additional lending permission is invented.

| Persona | Role ID | What they need | Authority |
|---|---|---|---|
| Relationship manager | `RELATIONSHIP_MANAGER` | Assigned-application visibility; limited AI assist | No memo, no recommendation record, no final credit, no policy override |
| Credit analyst | `CREDIT_ANALYST` | Reconcile evidence, draft memo, refer | Final credit only if policy allows (`LIMITED_IF_POLICY_ALLOWS`). Engine role controls, not LOS assignment |
| Senior underwriter | `SENIOR_UNDERWRITER` | Exception review, within-authority decisions | Final credit `YES_WITHIN_AUTHORITY`. Policy override only via documented authorized process. SME-L007 `APPROVE_EXCEPTION` requires this role |
| Credit authority | `CREDIT_AUTHORITY` | Large-limit authorization, adverse/recourse | Final credit `YES_WITHIN_AUTHORITY`. Formal exception process only. SME-L002 / SME-L013 require this engine role |
| Risk / compliance evaluator | `RISK_COMPLIANCE_EVAL` | Separate fairness/impact evaluation | De-identified or approved-purpose view. Restricted attributes allowed **only** for approved evaluation purpose. **No** runtime decision, memo, recommendation or final credit |
| AI agent (system actor) | `AI_AGENT` | Tool-scoped retrieve / draft / advise | `final_credit_decision=NO`, `override_policy=NO`. Allowed: `ASSIST`, `SUMMARIZE`, `REFER`, `DRAFT_RECOMMENDATION`. Forbidden: `APPROVE`, `DECLINE`, `CONDITION`, `PRICE`, `CHANGE_FACILITY`, `AUTHORIZE_LARGE_LIMIT`, `APPROVE_EXCEPTION`, `ISSUE_ADVERSE` |

**Sufficiency (engine-required role vs actor):**

| Required role | Sufficient actor |
|---|---|
| `CREDIT_ANALYST` | `CREDIT_ANALYST`, `SENIOR_UNDERWRITER`, `CREDIT_AUTHORITY` |
| `SENIOR_UNDERWRITER` | `SENIOR_UNDERWRITER`, `CREDIT_AUTHORITY` |
| `CREDIT_AUTHORITY` | `CREDIT_AUTHORITY` |

LOS `assigned_role` is not controlling when it differs from the Policy Engine `required_human_role` (SME-L002). Fixture role `PORTFOLIO_ANALYST` (SME-L015) is an assigned workflow label, not an extra authority in the matrix.

**Affected persons (not workbench operators):** legal-entity SMEs, sole-trader businesses, natural-person owners and guarantors. Sole-trader and guarantor cases require explicit affected-person and governance analysis (`CRD-SEC-008`). Jurisdiction/legal classification remains `OPEN_DECISION` for qualified legal/compliance review.

**Tenants:** workshop isolation is `TENANT-ALPHA` vs `TENANT-BETA`. A TENANT-ALPHA actor receives zero TENANT-BETA content (`CRD-AC-008`, `CRD-SEC-004`). Workshop tenancy is not a production IAM design.

---

## 6. Primary, exception, adverse, failure and manual workflows

Intended operating flow:

`application intake → consent/evidence collection → identity reconciliation → financial analysis → policy evaluation → memo preparation → authorized human decision → condition/recourse/outcome recording`

Intelligence path:

`request validation → access/purpose check → retrieval plan → evidence retrieval → context assembly → AI analysis/draft → deterministic policy checks → required human review → decision record → trace/evaluation`

| Workflow | Trigger | Required behavior | Proof scenario |
|---|---|---|---|
| Nominal legal-entity | SME-L001 | Task context from permitted evidence; active policy; grounded memo; human final | `CRD-AC-001` |
| Large-limit authority | SME-L002 | Engine `CREDIT_AUTHORITY`; AI cannot authorize | `CRD-AC-002` |
| Sole trader / person impact | SME-L003 | Business ≠ owner; restricted attrs excluded | `CRD-AC-003` |
| Identity mismatch | SME-L004 | AMBIGUOUS; no silent merge; escalate/adjudicate | `CRD-AC-004` |
| Stale bank | SME-L005 | Stale visible, not current; refresh or degrade | `CRD-AC-005` |
| Bureau unavailable | SME-L006 | Explicit missing; no invented score; not L007 | `CRD-AC-006` |
| True policy exception | SME-L007 | Engine `EXCEPTION_REVIEW` / `SENIOR_UNDERWRITER` | `CRD-AC-007` |
| Cross-tenant attack | SME-L008 | Zero TENANT-BETA content on every path | `CRD-AC-008` |
| Prompt injection | SME-L009 | Document text is DATA; not followed | `CRD-AC-009` |
| AI outage | SME-L010 | Manual underwriting continues; no fabricated assist | `CRD-AC-010` |
| Bank vs tax conflict | SME-L011 | Do not average; surface disagreement | `CRD-AC-011` |
| Superseded policy trap | SME-L012 | `CREDIT-POLICY-3.2` controls; v2.9 historical only | `CRD-AC-012` |
| Adverse + guarantor | SME-L013 | Human authority, grounded reason, recourse; AI no decline | `CRD-AC-013` |
| Invented threshold | SME-L014 | Reject generated threshold not in 3.2 | `CRD-AC-014` |
| Feedback boundary | SME-L015 | Capture to governed review; no auto policy/model rewrite | `CRD-AC-015` |

Degraded modes (`CRD-DATA-013`): `DECISION_CAN_CONTINUE`, `REQUIRES_ADDITIONAL_EVIDENCE`, `AI_ASSISTANCE_UNAVAILABLE`, `MANDATORY_ABSTENTION`. The four modes stay distinct. Missing bureau/bank facts are never invented.

---

## 7. Functional requirements

Normative text lives in `specs/01_system/SYSTEM_REQUIREMENTS.md`. Summary for build:

| ID | MUST | Primary AC | Contract 2026-09-10 | Workbench | Production |
|---|---|---|---|---|---|
| `CRD-FR-001` | Task-specific runtime context; no repository dump | `CRD-AC-001` | PASS | NOT IMPLEMENTED | NOT PROVEN |
| `CRD-FR-002` | Preserve source semantics, provenance, freshness, version, unresolved conflict | `CRD-AC-011` | PASS | NOT IMPLEMENTED | NOT PROVEN |
| `CRD-FR-003` | Resolve identity only with evidence; keep ambiguity | `CRD-AC-004` | PASS | NOT IMPLEMENTED | NOT PROVEN |
| `CRD-FR-004` | Route structured / graph / semantic / policy / memory; vector cannot override policy | `CRD-AC-012` | PASS | NOT IMPLEMENTED | NOT PROVEN |
| `CRD-FR-005` | Deterministic access, policy, authority, safety before high-impact handoff | `CRD-AC-012` | PASS | NOT IMPLEMENTED | NOT PROVEN |
| `CRD-FR-006` | Evidence-grounded analysis; disclose uncertainty; no fabricated facts | `CRD-AC-001` | PASS | NOT IMPLEMENTED | NOT PROVEN |
| `CRD-FR-007` | Human or deterministic authority for controlled decisions | `CRD-AC-002` | PASS | NOT IMPLEMENTED | NOT PROVEN |
| `CRD-FR-008` | Graceful degradation / abstention; manual path during AI outage | `CRD-AC-005` | PASS | NOT IMPLEMENTED | NOT PROVEN |
| `CRD-FR-009` | Reconstructable decision trace; no hidden CoT | `CRD-AC-001` | PASS | NOT IMPLEMENTED | NOT PROVEN |
| `CRD-FR-010` | Feedback only through governed change; no silent rewrite | `CRD-AC-015` | PASS | NOT IMPLEMENTED | NOT PROVEN |
| `CRD-FR-011` | AI MUST NOT exercise final credit, adverse, exception or recourse authority | `CRD-AC-007` | PASS | NOT IMPLEMENTED | NOT PROVEN |

When generated interpretation conflicts with an authoritative source or active policy, the authoritative evidence/control wins and the conflict remains visible.

---

## 8. Semantic, ontology and identity requirements

Canonical types and forbidden equivalences: `specs/05_data_contracts/DOMAIN_MODEL.md` (`CRD-DATA-004`, `CRD-AC-016`).

Must remain un-coercible: `LegalEntity` vs `NaturalPerson`; `Applicant`/`Guarantor` as roles; `BANK_INFLOWS_12M` vs `TAX_DECLARED_TURNOVER` vs `STATEMENT_RECOGNIZED_REVENUE`; `BureauRecord` vs `Exposure`; `Recommendation` vs `HumanDecision`; `PolicyEvaluation.PASS` vs `HumanDecision.APPROVE`; OCR/extraction confidence vs creditworthiness; missing-evidence exception vs policy exception.

Identity (`CRD-FR-003`, `CRD-DATA-006`): states `MATCHED` / `AMBIGUOUS` / `UNRESOLVED`. `identifier_crosswalk.canonical_candidate` is a hypothesis. Uncertain identity must not enter underwriting as a single entity. Original source observations remain after any later canonicalization.

Knowledge graph must connect applications, parties, evidence, financial observations, policy evaluations, policy versions, human roles, decisions and outcomes with provenance and time, and **must represent conflict** rather than overwrite inconvenient facts.

---

## 9. Source, data, provenance and freshness

Nine brownfield families (inventory in `evidence/01_enterprise_sources/`):

| System | Authoritative for | Not authoritative for |
|---|---|---|
| Loan Origination | Application + workflow identity | External bureau/tax/bank facts |
| Document Store | Document bytes/version | Financial interpretation; instructions |
| Commercial Bureau | Provider credit history (purpose/freshness) | Internal policy decision |
| Bank Data | Consented cashflow; freshness-limited | Tax declared turnover |
| Tax/GST | Filing / declared activity | Bank inflows |
| Exposure System | Current internal obligations | Bureau debts |
| Credit Policy Engine | Active rules and authority route | Human credit decision |
| Case Management | Human decision / recourse record | Generated recommendation |
| Memo Repository | Searchable history | Active policy or objective truth |

Material facts used by AI or gates MUST carry the `CRD-DATA-001` envelope (source, record id, entity, period, times, freshness, version, consent/purpose, derivation confidence, conflict, access, provenance). Bank and tax measures MUST NOT be averaged. Workshop visibility rule (not an approval cutoff): bank 12-month inflows and tax declared turnover disagree materially when their ratio is outside `[0.75, 1.25]`.

Known numeric literals in active `CREDIT-POLICY-3.2`: requested limit **above INR 5,000,000** requires `CREDIT_AUTHORITY` (`AUTH-LIMIT-01`); bank freshness **7 days** (`DATA-FRESHNESS-BANK`). No other credit thresholds may be invented (`CRD-AC-014`).

---

## 10. Hybrid retrieval and runtime context

Retrieval families (`CRD-DATA-009`):

| Need | Family | Tool | Authoritative? |
|---|---|---|---|
| Exact limit / exposure / source health / bank/tax amounts | structured | `CRD-TOOL-001` | Source facts; not Policy |
| Ownership / guarantor / exposure relationships | graph | `CRD-TOOL-002` | Relationship + identity/freshness/conflict |
| Memo / interview / similar narrative | semantic/vector | `CRD-TOOL-003` | Never; untrusted DATA |
| Active policy and authority route | policy/version-aware | `CRD-TOOL-004` | Yes when ACTIVE and controlling |
| Prior authorized decision / outcome | controlled memory | memory path | Historical only |

Tenant, purpose, document-status and freshness filters run **before** results reach the model. Vector similarity MUST NOT select or override the controlling policy hop.

Runtime context (`CRD-DATA-002` / `008`) is a **task-relevant connected slice** for one application, actor, tenant, task/intent, as-of time, freshness, source authority, active policy version, conflicts/missing evidence, relevant history and provenance — not the entire knowledge graph pasted into a prompt.

Exclusion reason codes include: `OTHER_APPLICATION`, `CROSS_TENANT`, `HISTORICAL_MEMO_NOT_POLICY`, `SUPERSEDED_POLICY`, `RESTRICTED_ATTRIBUTE`, `IRRELEVANT_TO_TASK`.

---

## 11. AI / agent, policy and human-control requirements

AI may: document extraction assistance; evidence reconciliation and discrepancy explanation; retrieval planning; summarizing connected evidence; drafting a credit memo section; proposing questions or next evidence requests; explaining deterministic policy results in business language.

AI may not: approve/decline; change policy; use restricted attributes by default; fabricate missing evidence; issue adverse determinations; authorize large limits; approve exceptions.

Tools (`specs/06_api_contracts/TOOL_CONTRACTS.md`): `CRD-TOOL-001`–`010`. `check_access_and_authority` and `handoff_recommendation` are the deterministic controls; they cannot be replaced by prompt text.

Active policy is `CREDIT-POLICY-3.2` (effective 2026-07-01). Superseded `CREDIT-POLICY-2.9` may be shown only as historical reference and MUST NOT control. Unavailable policy → abstention, not an invented rule. Generated explanation is not policy evidence (AT-16).

---

## 12. Decision trace, evaluation and feedback

Trace (`CRD-DATA-003`, `CRD-FR-009`, AT-16/AT-17) MUST record: task, application, actor, tenant; context snapshot/as-of; structured/graph/vector/policy/memory retrievals; source refs, freshness, authority; policy checks and versions; tool calls; model/prompt/semantic/ontology/policy versions; recommendation/draft; concise observable rationale; uncertainty/abstention; human decision, role and reason; outcome and evaluation flags. MUST NOT log hidden chain-of-thought.

Feedback events are distinct (`CRD-FR-010`, `CRD-AC-015`, `FEEDBACK-001`): human accept/modify/reject of AI assistance; authorized credit decision; later portfolio outcome; evaluation/adjudication evidence; changes to semantics, ontology/KG, retrieval policy, prompts/models or credit policy. `AI_ACCEPTED` MUST NOT mutate `CREDIT-POLICY-3.2`, ontology, prompts, models or gold labels. Missing portfolio outcomes are not invented (SME-L015 has no outcome row).

---

## 13. Security, privacy and fairness-impact

Must not violate (`specs/04_security_privacy/SECURITY_GOVERNANCE.md`):

`CRD-SEC-001`–`012` — no autonomous AI credit; policy not modified by generation; material factors evidenced; tenant isolation before retrieval/display; restricted eval attributes out of runtime by default; stale/missing/conflict visible; untrusted text cannot override policy; sole-trader/guarantor governance; adverse/exception human + reason + recourse; manual path during AI outage; observable traces not hidden CoT; feedback cannot silently rewrite controls.

Fairness/impact evaluation is a **separate approved purpose** (`RISK_COMPLIANCE_EVAL`), not runtime feature injection. This PRD invents no legal fairness threshold and does not treat segment diagnostics as a compliance finding. Unresolved jurisdiction conclusions route to qualified legal/compliance review.

---

## 14. Non-functional requirements

Normative text: `specs/03_non_functional/NFR.md`. Intent (P0-01 notes grammar debt on `CRD-NFR-001`–`005`; do not invent new product intent while tightening wording):

| ID | Intent |
|---|---|
| `CRD-NFR-001` | Uncomplicated TAT <30 minutes is a business objective; workshop evidence must not claim production achievement unless measured |
| `CRD-NFR-002` | Tenant isolation is a code filter before retrieval and context assembly |
| `CRD-NFR-003` | Restricted-attribute boundaries are enforceable and auditable |
| `CRD-NFR-004` | Manual underwriting remains available if AI/context services are unavailable (`FALLBACK-001`, SME-L010) |
| `CRD-NFR-005` | Every material AI-assisted factor is traceable to evidence, policy/version and human action (HG-03 = 100% on generated FACT statements) |
| `CRD-NFR-006` | Source health, degraded mode, retrieval/tool failures and trace completeness are observable for workshop evaluation |
| `CRD-NFR-007` | Workshop verification uses supplied synthetic fixtures and deterministic scenarios; production claims require separate production evidence |

---

## 15. UX / screen requirements

Twelve required experiences (`google_ai_build/03_APP_SCREEN_REQUIREMENTS.md`, case study §14). Screens **display** P0/P1 state; they do not become the control plane.

| Screen | Must show | Feature |
|---|---|---|
| Underwriting Control Tower | Application, tenant, stage, status, source-health/exception | F1 |
| Application Context | Party roles, facility request, source summary, task context | F1 |
| Evidence Reconciliation | Separate bank/tax/bureau/document facts, freshness, conflicts, provenance | F1 |
| Context Graph Explorer | Connected nodes/edges with source/time/status | F1 |
| Hybrid Retrieval Evidence | Mode, query/tool, filters, evidence refs; five families labelled | F1 |
| Active Policy & Authority Gate | Policy version, triggered rules, required role, deny/escalation | F2 |
| AI-Assisted Analysis / Credit Memo | Evidence-grounded draft; uncertainty; missing evidence; not final decision | F2 |
| Human Decision / Escalation | Role-aware review/modify/reject/escalate/final action | F2 |
| Decision Trace / Audit | Context, sources, tools, policies, versions, concise rationale, human action | F3 |
| Fairness / Impact Evaluation | Evaluation-only cohort diagnostics; separated from runtime | F3 / P2-02 |
| Outcome & Feedback | Interaction feedback, later outcome, governed-learning status | F3 |
| Failure Simulation | Stale bank, no bureau, cross-tenant, injection, superseded policy, AI outage | F4 |

As of 2026-09-10: **0/12 screens implemented.** G-UI-01 blocks workbench beta and production (`RELEASE_GATES.md`).

Required memo sections (`CRD-DATA-014`): applicant context; financial evidence; exposure; bureau; policy applicability; conflicts; risk factors; mitigants; exceptions; missing evidence; recommendation; required authority. Material statements cite evidence or are labelled `[INFERENCE]`.

---

## 16. Evaluation and acceptance

Golden scenarios `GS-01`–`GS-15` = `CRD-AC-001`–`015`. Semantic non-collapse `CRD-AC-016` is a model contract, not a 16th golden scenario.

App tests AT-01–AT-18: `google_ai_build/04_APP_ACCEPTANCE_TESTS.md`.

Hard gates and quality targets: `artefacts/SUCCESS_METRICS.md` and `evidence/06_evaluations/acceptance_thresholds.yaml`.

Contract-layer 2026-09-10: 15/15 PASS, HG-01–HG-08 PASS, QT-01 MET **at contract layer only**. Workbench and production QT-01 are **not claimed**. `evaluation_matrix.csv` QUALITY rows that require UI/tool screenshots remain **NOT PROVEN**.

---

## 17. Architecture and workshop-vs-production mapping

| Layer | Workshop (this repo) | Production (not proven) |
|---|---|---|
| Sources | Heterogeneous fixtures | Named live adapters for LOS, bureau, bank, tax, exposure, policy engine |
| Semantics | `DOMAIN_MODEL.md` + `src/credit_domain/model.py` | Deployed type service |
| Graph | In-memory JSON slice; ADR Template 06 unfilled | Accepted ADR (property graph / RDF / relational); six representative traversals |
| Retrieval | Fixture readers; lexical stand-in for vector | Production vector/graph adapters; vector still cannot override policy |
| Context | `assemble_runtime_context` | Same contract on live data |
| AI | Deterministic grounded memo stub; `versions.model=NONE` | Versioned model card, prompt inventory, gates remain outside generation |
| Gates | Python `CRD-TOOL-004`–`007` | Same gates on workbench path + IAM |
| Trace / feedback | Contract writers | Durable audit store, Outcome & Feedback UI, change-control ops |
| Tenancy | TENANT-ALPHA / TENANT-BETA fixtures | Production tenancy/IAM (not this fixture pair) |

Prototype MAY simulate the graph contract in JSON. Authority boundaries MUST remain visible. Workshop fixtures MUST NOT be proposed as live credit data.

---

## 18. Release scope

See `artefacts/PRODUCT_STRATEGY.md` and `RELEASE_GATES.md`.

| Path | Allowed when | Current |
|---|---|---|
| Workshop demonstration (contracts only) | HG-01–HG-08 green on unittest; operators told this is assistance, screens missing, TAT not the 30-minute target, 3.2 is the only active workshop policy | CONDITIONAL GO |
| Workbench beta (internal) | G-UI-01 screen evidence for GS-01–GS-15 (or explicit exception list that does not weaken HG-*); Human Decision, Decision Trace, Outcome & Feedback mandatory before user-visible memo | BLOCKED |
| Production release | Hard gates re-verified on workbench path; G-FB-* green; rollback drill; human override drilled; named production adapters; human sign-off of high-impact controls; QT-05 if reported uses a production population | BLOCKED |

---

## 19. Out-of-scope capabilities

- Granting AI autonomous authority over final credit decision, adverse/exception route or recourse.
- Inventing production/legal classifications, extra credit thresholds, or fairness cut-offs not in the case / `CREDIT-POLICY-3.2`.
- Claiming workshop fixture results (including 89.5-minute TAT) prove production business outcomes.
- Replacing authoritative source systems with generated data.
- Using superseded `CREDIT-POLICY-2.9` as a production rollback controller.
- Treating `AI_ACCEPTED`, historical declines, or later portfolio outcomes as current policy or gold labels.
- Restricted fairness-eval attributes as runtime decision features.
- Hidden chain-of-thought as a required trace field.
- Marking any `CRD-FR-*` `VERIFIED` from this artefact alone.

---

## 20. Risks, assumptions and open decisions

### Assumptions

- Synthetic fixtures and golden scenarios are the workshop source of truth (`CRD-NFR-007`).
- Active workshop policy remains `CREDIT-POLICY-3.2`; known literals remain INR 5,000,000 and 7-day bank freshness.
- Human reviewers sign high-impact authority changes (`DEFINITION_OF_DONE.md`).
- Specs change only through `CHANGE_CONTROL.md` / `CRD-CR-*`.

### Risks

| Risk | Why it matters | Mitigation already specified |
|---|---|---|
| Screen bypasses gates | UI becomes the control plane | Screens display P0/P1 state; `check_access_and_authority` remains code |
| Later LLM without gates | Invented thresholds, injection, silent merge | GS-14 / GS-09 / GS-04 remain hard; prompt obedience is not a substitute |
| Mixing TAT populations | False 30-minute claim | Three labelled populations in `RELEASE_GATES.md` |
| Feedback writes policy | Silent learning-loop capture | `FEEDBACK-001`, G-FB-01 |
| Graph ADR never accepted | Stage 4 deliverable unmet | P2-06; prototype may simulate but ADR still required |
| Identity adjudicator unspecified | AMBIGUOUS cases stall | Keep ambiguity visible; do not invent a new authority role |

### OPEN_DECISION (do not guess)

| Item | Owner needed | Required evidence |
|---|---|---|
| Jurisdiction / legal classification of sole-trader and guarantor processing | Legal / compliance | Analysis of purpose, actor, affected-person — not a PRD invention |
| Graph platform choice | Architecture | Filled Template 06 ADR vs six case-study traversals |
| Production adapter contracts | Engineering + source owners | Named LOS/bureau/bank/tax/exposure/policy adapters; fixtures not live data |
| Rollback runbook (G-RB-01) | Operations + policy owner | Drill that never applies v2.9 as controller |
| Fairness eval-mode operating procedure | Risk / compliance | `RISK_COMPLIANCE_EVAL` purpose run; no legal fairness cutoff invented |
| NFR-001–005 grammar tidy | Spec owner | Change request; no new product intent |
| Empty `hard_fail_if` for GS-01/03/04/10/15 | Eval owner | Fill arrays; ACs remain normative meanwhile |
| Identity match adjudicator UI | Credit operations | Human workflow; no silent merge |

---

## 21. Traceability

Full matrix: `specs/08_traceability/TRACEABILITY_MATRIX.md`. All `CRD-FR-*` rows are `IN_PROGRESS`. Do not mark `VERIFIED` from this document.

Chain the final review must be able to trace:

`source evidence → semantic/ontology decision → connected knowledge → retrieval → context → AI behavior → deterministic control → human action → trace → outcome/evaluation`

---

## 22. Future roadmap

Normative horizon: `90_DAY_MODERNIZATION_ROADMAP.md` (2026-09-10 → 2026-12-08). Summary in `artefacts/PRODUCT_STRATEGY.md`. Production GO at day 90 is **not** the default outcome.
