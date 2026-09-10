# Business Metrics Catalog — SME Credit Underwriting Intelligence Workbench

**Compiled:** 2026-09-10  
**CRD IDs:** `CRD-BR-001`–`004`, `CRD-AC-001`–`016`, HG-01–HG-08, QT-01–QT-05, G-AUTH-*, G-FB-*, G-ISO-01  
**Companions:** `artefacts/VALUE_REALIZATION_FRAMEWORK.md`, `artefacts/EXECUTIVE_DASHBOARD_SPEC.md`, `artefacts/SUCCESS_METRICS.md`  
**Rule:** SM-*, HG-*, QT-* in `SUCCESS_METRICS.md` remain the product success model. This catalog adds **post-go-live business reporting IDs** (BM-*). A metric is closed only with fresh evidence from this repository on the **named layer**. Documentation is not evidence.

**Current claim:** All BM-* production values are **NOT MEASURED**. Contract HG/QT rows are **not** production BM values.

---

## 1. How to read a row

| Field | Meaning |
|---|---|
| **ID** | Stable catalog ID |
| **Maps to** | SM / HG / QT / gate / adoption hygiene |
| **Formula** | Observable counts or times — no hidden CoT |
| **Population** | Must be labelled on every report |
| **Target** | BINDING from specs, directional from source baseline, or OPEN |
| **Better** | Direction that is value — some zeros are success (isolation DENY) |
| **Layer now** | What 2026-09-10 evidence may say |

Populations (do not mix): source-case baseline **142 / 648 / 31.2% / 57% / 38 min / 8.4% / 13.7%**; workshop fixture **89.5 / 218**; golden **SME-L001–L015**; named **production book**.

---

## 2. Adoption KPIs

Adoption = designated roles complete assigned work **in** the workbench, leave defects visible, record `HumanDecision`, obey engine role, and do not write the catalog from AI accept (`ADOPTION_STRATEGY.md` §1).

| ID | Metric | Maps to | Formula | Target | Better | Owner | Layer now |
|---|---|---|---|---|---|---|---|
| **BM-A01** | Failure Lab coverage | Adoption hygiene | Users with memo/decision access who passed M5 labs (GS-08/09/10/14 + L004/L006) ÷ named cohort | 100% of UAT/PROD named cohort | ↑ to 100% | Credit Operations | Not started (G-UI-01) |
| **BM-A02** | In-workbench completion | Adoption definition | Cases with `HumanDecision` persisted in workbench ÷ assigned cases in the named book (exclude shadow tools) | Directional ↑ after GO; no % in case evidence (**PROPOSED** operating target) | ↑ | Credit Operations | NOT MEASURED |
| **BM-A03** | Gate-bypass tickets | Adoption hygiene | Tickets/requests to “just approve,” “turn off tenant filter,” or “use 2.9” | Trend → 0; each is coaching or Sev 1 | ↓ | L1 / Security | NOT MEASURED |
| **BM-A04** | Named-cohort active users | Enablement | Distinct IdP users in the signed role matrix who completed ≥1 gated path in period | 100% of **named** PROD cohort after hypercare (cohort list OPEN until UAT) | ↑ within named list — not “all staff” | Credit Operations | Cohort **OPEN** |
| **BM-A05** | Shadow-tool incidents | Anti-adoption | Detected completions outside workbench (unofficial GPT, blended-revenue spreadsheet) on in-scope applications | 0 material incidents in claim window | ↓ | Credit Operations + Security | NOT MEASURED |
| **BM-A06** | Catalog writes from `AI_ACCEPTED` | G-FB-01 | Count of policy / ontology / prompt / model / gold mutations sourced from accept/modify/reject | **0** (BINDING) | = 0 | Model risk | Contract PASS; PROD OPEN |
| **BM-A07** | RM decision attempts | Persona | `RELATIONSHIP_MANAGER` actions that would record memo, recommendation, or final credit | **0** ALLOW | = 0 | Credit Operations | Contract role matrix; UI OPEN |

**Not adoption KPIs:** memo count, chatbot sessions, workshop 15/15, fixture TAT 89.5.

---

## 3. Decision quality KPIs

Quality is grounding, authority, semantics, and reconstructability — **not** approval rate or model confidence.

| ID | Metric | Maps to | Formula | Target | Better | Owner | Layer now |
|---|---|---|---|---|---|---|---|
| **BM-Q01** | Autonomous AI final actions | HG-01, SM-03, G-AUTH-01 | Count of AI `APPROVE` / `DECLINE` / `AUTHORIZE_LARGE_LIMIT` / `APPROVE_EXCEPTION` / `ISSUE_ADVERSE` = ALLOW | **0** | = 0 | Credit authority / Engineering | Contract PASS; UI OPEN |
| **BM-Q02** | Invented policy / threshold | HG-02, GS-14 | Count of generated thresholds or policy text treated as catalog (workshop probe class: INR 2,500,000) | **0** (critical) | = 0 | Credit Policy | Contract PASS; UI OPEN |
| **BM-Q03** | Material FACT provenance | HG-03, SM-02, `CRD-BR-002` | Material FACT statements with reproducible source reference ÷ material FACT statements | **100%** on UI/PROD path | = 100% | Credit Operations | Contract PASS on generated FACT; UI **not claimed**. Baseline problem: **13.7%** missing in source audit sample |
| **BM-Q04** | Semantic non-collapse | `CRD-AC-016`, SM-02 | Bank inflow, tax/GST turnover, statement revenue remain distinct kinds; generic `revenue` blended facts | **0** blended generic revenue in decision context | = 0 | Credit Policy + Engineering | Contract tests; UI OPEN |
| **BM-Q05** | Decision ≠ memo | G-AUTH-02 | Recommendations persisted as `HumanDecision` (not memo-only) ÷ assistance-completed cases | **100%** of cases that leave assistance | = 100% | Credit Operations | Contract PASS; Human Decision UI OPEN |
| **BM-Q06** | Engine role vs LOS | G-AUTH-03, GS-02 | Large-limit / adverse / exception actions where actor ≥ engine `required_human_role` | **100%**; LOS assignment never overrides | = 100% | Credit authority | Contract PASS; UI OPEN |
| **BM-Q07** | Missing vs exception split | SM-08, GS-06/07 | L006-class (null bureau) kept as missing-evidence; L007-class requires `SENIOR_UNDERWRITER` | **0** collapses of L006 into exception-approve | = 0 collapse | Credit Policy | Contract PASS; UI OPEN |
| **BM-Q08** | Identity ambiguity preserved | GS-04, `CRD-AC-004` | Applications with insufficient resolution evidence left `AMBIGUOUS` (no silent merge) | **100%** of insufficient-evidence identity cases | Preserve AMBIGUOUS | Existing human authority | Contract PASS; UI OPEN |
| **BM-Q09** | Reconstructable trace | SM-04, AT-16/17 | Traces with evidence, context, tools, policy checks, versions, concise rationale, human action; **no** hidden CoT as evidence | **100%** of HumanDecision events | = 100% | Credit Operations / Model risk | Contract PASS; Trace UI OPEN |
| **BM-Q10** | Golden-behavior pass rate | QT-01 | GS-01–GS-15 pass rate **and** all hard-gate scenarios passing, on the **claimed layer** | ≥ 95% **and** HG scenarios pass | ↑ only with HG | Model risk | Contract **MET** 15/15. Workbench/PROD **not claimed** |
| **BM-Q11** | Assistance challenge rate | Quality of drafts | Human `MODIFY` / `REJECT` of AI draft where reject reason is invented fact, invented threshold, or ungrounded FACT | No target % in case (**OPEN**). **Do not** maximize accept rate | Grounded rejects are healthy | Credit Operations | NOT MEASURED |
| **BM-Q12** | Stale / conflict visibility | QT-03, QT-04, GS-05/11 | Material stale or adjudicated-conflict cases where defect remains visible (`presented_as_current=false`; unblended bank vs tax) | **100%** of those scenarios | Visible = success | Data Partnerships / Credit Risk | Contract PASS; UI OPEN |

**Forbidden quality KPIs:** approval %, “AI agree with human” %, confidence, fairness cutoff, NPL predicted from the memo.

---

## 4. Productivity metrics

Measure **after** HG green in the same window. Directional targets use the **source-case** baseline, not the 160-row fixture.

| ID | Metric | Maps to | Formula | Target | Better | Owner | Layer now |
|---|---|---|---|---|---|---|---|
| **BM-P01** | Uncomplicated TAT (median) | SM-01, QT-05, `CRD-BR-001`, NFR-PERF-01 | Intake / as-of → `HumanDecision` on **named uncomplicated production** population | **< 30 minutes** **and** HG fail = 0 | ↓ vs **source 142**, never claim 89.5 as this target | Credit Operations | **NOT PROVEN** |
| **BM-P02** | Uncomplicated TAT (P90) | Source baseline | Same clock, P90 | Directional ↓ vs source **648**; no P90 SLO in case (**OPEN** numeric SLO) | ↓ | Credit Operations | NOT PROVEN |
| **BM-P03** | Memo preparation time | SM-05 | Median minutes from memo-task start → grounded memo ready **with** HG-03 intact | Directional ↓ vs source **38** min; **not** if facts invented | ↓ without HG-02/03 fail | Credit Operations | NOT PROVEN |
| **BM-P04** | Multi-system lookup burden | SM-06 | % of sampled cases with >3 **manual** system lookups outside Control Tower / Evidence Reconciliation | Directional ↓ vs source **57%** | ↓ | Credit Operations | NOT PROVEN |
| **BM-P05** | Document rework | SM-07 | % of cases returned for document rework | Directional ↓ vs source **31.2%** | ↓ **without** hiding missing evidence | Lending Operations / Credit Operations | NOT PROVEN |
| **BM-P06** | Missing source-ref rate | SM-02 | % of decision packages missing a reproducible source reference | Directional ↓ vs source **13.7%**; UI path aims at HG-03 = 100% | ↓ | Credit Operations | Contract FACT PASS; package UI OPEN |
| **BM-P07** | Manual-path throughput | HG-08, GS-10 | Cases completed on documented manual fallback during AI outage **without** a fabricated AI memo | Completions > 0 when AI down; **no** extra wait vs credit-path RTO = 0 added wait | Finish without invention | Credit Operations | Contract PASS; UI OPEN |
| **BM-P08** | Exception incidence | SM-08 note | True policy-exception rate | Source **8.4%** is **baseline incidence**, not a minimize-by-bypass target | Split quality (BM-Q07) over raw ↓ | Credit Policy | Do not “optimize” |

TAT instrumentation: decision-trace timestamps (`NFR_SPECIFICATION.md` NFR-PERF-01). Workshop GS-01 is behavioral, not a TAT proof.

---

## 5. Financial outcomes

Case evidence does **not** include FTE fully loaded cost, expected-loss models, NPL, revenue, or ROI. Financial **methods** are specified; **currency targets are OPEN** until Finance raises a change request.

| ID | Metric | Formula / method | Binding | Better | Owner | Layer now |
|---|---|---|---|---|---|---|
| **BM-F01** | Analyst hours avoided (memo) | `(38 − measured median memo minutes) × uncomplicated volume / 60` on named book, **only if** BM-P03 valid and HG-03 = 100% | Hours BINDING method; **$ OPEN** | Hours ↓ | Credit Operations (hours); Finance ($ CR) | NOT MEASURED |
| **BM-F02** | Lookup / rework hours avoided | Directional from BM-P04 / BM-P05 vs 57% / 31.2% on a **time-and-motion sample** — do not invent minutes-per-lookup | Sample method **PROPOSED**; $ OPEN | Hours ↓ | Credit Operations; Finance | NOT MEASURED |
| **BM-F03** | Control-incident count (not $) | Sev 1 isolation / injection / invented-policy / AI-final events in period | Count BINDING; **do not** publish an expected-loss $ from this catalog | = 0 | Security / Model risk | NOT MEASURED in PROD |
| **BM-F04** | Currency conversion | `hours × named fully loaded rate` | **OPEN** — rate not in fixtures | n/a until CR | Finance | OPEN |
| **BM-F05** | Credit-book P&L / NPL / loss given default | **Out of product authority.** Historical portfolio labels ≠ gold (G-FB-02). Do not attribute book performance to LLM scores | Forbidden as workbench value unless a **separate** Credit Risk CR defines an independent study | n/a | Credit Risk / Portfolio Risk | Not a workbench KPI |
| **BM-F06** | Cases per FTE | Volume ÷ named analyst FTE on the production book | **PROPOSED** — not in case evidence | ↑ only with HG green | Credit Operations | OPEN |
| **BM-F07** | Appeal / recourse cost | Recourse remains human; calendar and cost **OPEN** (`NFR` appeal calendar OPEN) | Do not claim AI reduced appeals by issuing decline text | n/a | Credit Operations + Legal (`OPEN_DECISION`) | OPEN |

**Steerco line:** report **hours and incident counts** until Finance signs BM-F04. Never present a payback period from workshop PASS.

---

## 6. User engagement metrics

Engagement = following the **gated path**, not session length or chat turns.

| ID | Metric | Formula | Target | Better | Owner | Layer now |
|---|---|---|---|---|---|---|
| **BM-E01** | Named-cohort weekly active | Distinct named-cohort users with ≥1 authenticated workbench session in week | 100% of **required** roles in the signed PROD list during hypercare (**PROPOSED** %) | Within list, not vanity WAU | Credit Operations | NOT MEASURED |
| **BM-E02** | Gated-path completion | Sessions that include Control Tower → Evidence Reconciliation → (Policy & Authority as needed) → Memo → **Human Decision** → Trace ACK ÷ assistance sessions that emit a memo | **100%** of memo-emitting sessions include Human Decision + Trace | = 100% | Engineering / Credit Operations | UI OPEN (0/12) |
| **BM-E03** | Time-to-first Human Decision | Calendar time from access grant → first persisted `HumanDecision` (supervised UAT then PROD) | No numeric SLA in case (**OPEN**); used as enablement diagnostic | Shorter after training, not rushed gates | Training lead | NOT MEASURED |
| **BM-E04** | Failure Simulation use | Distinct users completing assigned Failure Lab / simulation in period | 100% of memo/decision cohort (BM-A01) | Assigned use; do not game volume | Training lead | NOT MEASURED |
| **BM-E05** | Governed feedback vs catalog | `GOVERNED_REVIEW` events ÷ (accept/modify/reject events); catalog mutations from those events | Review **100%** of material feedback; catalog mutations **0** | Review ↑; mutations = 0 | Model risk | Contract PASS; UI OPEN |
| **BM-E06** | Eval-mode containment | Fairness/Impact Evaluation sessions with purpose `RISK_COMPLIANCE_EVAL` and **zero** runtime decision writes | **100%** of eval sessions contained | Contained | Risk / compliance eval | Contract PASS; eval UI OPEN |
| **BM-E07** | How-to vs bypass ticket mix | After hypercare: how-to tickets ÷ (how-to + bypass) | Bypass → 0 (BM-A03); how-to may remain | Mix shift, not ticket starvation | L1 | NOT MEASURED |

**Not engagement:** tokens, chat turns, “AI used” clicks, RM logins as underwriting adoption.

---

## 7. Risk reduction metrics

Zero on isolation, injection, restricted attributes, superseded policy, and invented thresholds **is** the value. DENY is success.

| ID | Metric | Maps to | Formula | Target | Better | Owner | Layer now |
|---|---|---|---|---|---|---|---|
| **BM-R01** | Cross-tenant retrieval success | HG-04, G-ISO-01, GS-08 | Successful other-tenant content in requester context | **0** | = 0 (DENY = pass) | Security | Contract PASS; UI OPEN |
| **BM-R02** | Injection followed | HG-07, GS-09 | Document/retrieved text treated as instruction or policy change | **0** | = 0 | Security | Contract PASS; UI OPEN |
| **BM-R03** | Restricted attrs in runtime | HG-05, GS-03/15 | Restricted evaluation attributes in runtime decision context | **0** by default | = 0 | Risk / compliance eval + Security | Contract PASS; UI OPEN |
| **BM-R04** | Superseded policy applied | HG-06, GS-12 | Evaluations controlled by `CREDIT-POLICY-2.9` or non-ACTIVE bundle | **0**; ACTIVE remains **3.2** until dual-control CR | = 0 | Credit Policy | Contract PASS; UI OPEN |
| **BM-R05** | Invented threshold (risk view) | HG-02 | Same as BM-Q02; on exec risk pack as **critical** | **0** | = 0 | Credit Policy | Contract PASS |
| **BM-R06** | Manual fallback available | HG-08, GS-10 | Fallback path true when AI unavailable; no fabricated memo | **true** | true | Operations / Credit Operations | Contract PASS; UI OPEN |
| **BM-R07** | Sev 1 control incidents | IR plan | Count of Sev 1 (hard-gate or credit-path down, fail-open attempt) | **0** in claim window | = 0 | Incident commander | NOT MEASURED (no PROD) |
| **BM-R08** | Audit source-ref defect rate | SM-02, 13.7% baseline | Independent audit sample missing reproducible source | Directional ↓ vs **13.7%**; UI goal 100% provenance | ↓ | Independent reviewer | NOT MEASURED on UI |
| **BM-R09** | Learning-loop denylist holds | G-FB-01–03 | Catalog/prompt/model/gold writes; invented portfolio outcomes; restricted sample via feedback | **0** each | = 0 | Model risk | Contract PASS |
| **BM-R10** | Rollback folklore | G-RB-01, DR | Production rollback drill exists; rollback target ≠ v2.9 | Drill **done**; never 2.9 | Drill PASS | Operations + Credit Policy | **OPEN — blocks GO** |
| **BM-R11** | Adverse / recourse human | GS-13, `CRD-SEC-008` | Adverse/conditional with human authority, material reason, approved appeal path; AI `ISSUE_ADVERSE` DENY | **100%** of adverse/conditional | Human holds | Credit authority | Contract PASS; UI OPEN |

Hard-control SLOs have **no error budget** (`NFR_SPECIFICATION.md`). Do not “spend” isolation failures to hit TAT.

---

## 8. Crosswalk to SM / HG / QT

| Success / gate | Business IDs |
|---|---|
| SM-01 / QT-05 | BM-P01 |
| SM-02 | BM-Q03, BM-P06, BM-R08 |
| SM-03 / HG-01 | BM-Q01 |
| SM-04 | BM-Q09 |
| SM-05 | BM-P03, BM-F01 |
| SM-06 | BM-P04, BM-F02 |
| SM-07 | BM-P05, BM-F02 |
| SM-08 | BM-Q07, BM-P08 |
| HG-02 | BM-Q02, BM-R05 |
| HG-03 | BM-Q03 |
| HG-04 | BM-R01 |
| HG-05 | BM-R03 |
| HG-06 | BM-R04 |
| HG-07 | BM-R02 |
| HG-08 | BM-R06, BM-P07 |
| QT-01 | BM-Q10 |
| QT-03 / QT-04 | BM-Q12 |
| G-FB-01 | BM-A06, BM-E05, BM-R09 |
| G-UI-01 | Blocks all UI-path BM-* claims |
| G-RB-01 | BM-R10; blocks GO and value clock |

---

## 9. Instrumentation (when screens exist)

| Signal | Source |
|---|---|
| Role, tenant, purpose | IAM + `check_access_and_authority` |
| Path and timestamps | Decision trace (intake → HumanDecision → ACK) |
| Provenance | Evidence envelopes on FACT statements |
| Policy version | `retrieve_active_policy` controlling flag |
| Retrieval families | Tool traces; vector never overrides policy |
| Feedback | Outcome & Feedback → `GOVERNED_REVIEW` only |
| Labs | Training records (trainee, role, date, GS ids) — no CoT of the trainee |
| Tickets | L1 taxonomy: how-to vs bypass vs Sev 1 |

Do not instrument hidden chain-of-thought. Do not put restricted eval attributes on the underwriting dashboard.

---

## 10. Catalog change control

New BM-* or a numeric target not in this case (e.g. BM-F04 rate, BM-P02 P90 SLO, BM-A02 %) requires a change request and does **not** close production GO by existing in this file. Do not alter `source_case_baseline.json` or workshop fixtures to make a chart look green.
