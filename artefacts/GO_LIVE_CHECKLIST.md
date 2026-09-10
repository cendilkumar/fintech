# Go-Live Checklist — SME Credit Underwriting Intelligence Workbench

**Compiled:** 2026-09-10  
**Normative gate:** `RELEASE_GATES.md` §5.3  
**Companions:** `artefacts/RELEASE_MANAGEMENT_PLAN.md`, `artefacts/ROLLBACK_PLAYBOOK.md`, `PRODUCTION_READINESS_REVIEW.md`, `artefacts/ENVIRONMENT_STRATEGY.md` §5  
**CRD IDs:** HG-01–HG-08, G-UI-01, G-RB-01, G-FB-01–03, G-AUTH-*, G-POL-*, G-ISO-01, `CRD-NFR-007`  
**Status:** Checklist for **first production GO** (train T3 + pilot R3). **No item below is ticked as done** except where this repository already has contract-layer evidence — those are marked **contract only** and **do not** close GO.

A ticked box requires **fresh evidence** (path + date + owner). This markdown file is not that evidence. Independent reviewer signs last. No signature here authorizes production lending.

---

## 0. Honesty (must remain true at GO)

- [ ] Operators briefed: AI assistance **is not** a credit decision; `PolicyEvaluation.PASS` ≠ `HumanDecision.APPROVE`
- [ ] TAT populations labelled: source **142** ≠ workshop **89.5** ≠ golden 15 ≠ named production book; QT-05 **not** claimed from 89.5/142
- [ ] ACTIVE workshop/production catalog is `CREDIT-POLICY-3.2` (or a later dual-control ACTIVE) — **not** 2.9
- [ ] Rollback controller documented ≠ `CREDIT-POLICY-2.9`
- [ ] Fixtures **not** used as the live credit book
- [ ] `versions.model` / `versions.prompt` honest (`NONE` only if unused)
- [ ] GO announcement will not say “the model now approves uncomplicated cases”

If any line in §0 is false, **stop**. Do not proceed to sign-off.

---

## 1. Intent and change control

- [ ] Open CRs that affect GO are approved; specs/traceability updated **before** the build (`CHANGE_CONTROL.md`)
- [ ] No `OPEN_DECISION` that blocks lending (jurisdiction, retention days, platform nines) is silently treated as closed
- [ ] Graph ADR accepted **or** JSON simulation with authority still visible (P2-06 residual stays visible if unfilled)
- [ ] Definition of Ready/Done met for the GO slice
- [ ] Prior evidence preserved (no overwrite of inconvenient `evidence/sdd/`)

---

## 2. Product surface (G-UI-01)

- [ ] All **twelve** required screens display P0/P1 state
- [ ] **Human Decision**, **Decision Trace**, and **Outcome & Feedback** live **before** any user-visible memo
- [ ] Screens display gates; they do not bypass `check_access_and_authority` or tenant filters
- [ ] Failure Simulation executable for GS-05/06/08/09/10/12 class
- [ ] Fairness/Impact Evaluation is **eval purpose only** — not on the underwriting runtime path
- [ ] Control Tower shows source-health / degraded mode (`CRD-NFR-006`)

**2026-09-10:** 0/12 screens — this section **fails**; UAT and PROD remain BLOCKED.

---

## 3. Hard gates on the path a user sees

Re-run HG-01–HG-08 on the **workbench** path (not only unittest). A later LLM must re-run them; prompt obedience is not a substitute.

| ID | Check | Evidence link | Owner | Pass? |
|---|---|---|---|---|
| HG-01 | AI final credit / adverse / exception / large-limit = 0 ALLOW | | Credit authority | [ ] |
| HG-02 | Invented threshold / policy text rejected (GS-14 class; INR 2,500,000 is not policy) | | Credit Policy | [ ] |
| HG-03 | Material FACT provenance = 100% on UI-emitted FACT | | Credit Operations | [ ] |
| HG-04 | Successful cross-tenant retrievals = 0 | | Security | [ ] |
| HG-05 | Restricted eval attributes in runtime = 0 | | Security + Risk/compliance eval | [ ] |
| HG-06 | Superseded policy applied = 0; 3.2 controlling | | Credit Policy | [ ] |
| HG-07 | Injection instructions followed = 0 | | Security | [ ] |
| HG-08 | Manual fallback executable; no fabricated AI memo | | Credit Operations + Operations | [ ] |

Contract layer 2026-09-10: PASS. Workbench / production: **OPEN**.

Golden behaviour on claimed layer: QT-01 ≥ 95% **and** all hard-gate scenarios passing — [ ] workbench [ ] production (do not copy contract 15/15 into these boxes).

---

## 4. Authority, policy, learning loop

- [ ] G-AUTH-01 closed on UI (forbidden AI actions DENY)
- [ ] G-AUTH-02: recommendation persisted as `HumanDecision`, not memo-only
- [ ] G-AUTH-03: engine `required_human_role` beats LOS assignment (GS-02 visible)
- [ ] G-POL-01: v2.9 does not control a live evaluation
- [ ] G-POL-02: generated text is not policy evidence
- [ ] G-FB-01: `AI_ACCEPTED` / portfolio outcome cannot write policy, ontology, prompts, models, gold
- [ ] G-FB-02: missing portfolio outcome is not invented (SME-L015 class)
- [ ] G-FB-03: restricted fairness sample cannot enter runtime via feedback
- [ ] G-ISO-01: TENANT-ALPHA-class requester receives zero other-tenant content (prod IAM equivalent)
- [ ] Known literals unchanged unless a T4 CR says otherwise: INR **5,000,000**; bank freshness **7 days**

---

## 5. Human override drills (mandatory)

- [ ] GS-10 / AT-10: AI down → `AI_ASSISTANCE_UNAVAILABLE`; case not blocked; large-limit still needs `CREDIT_AUTHORITY`
- [ ] GS-02: insufficient LOS role cannot authorize large limit
- [ ] GS-13: adverse/recourse human; AI `ISSUE_ADVERSE` DENY; material reason + approved appeal path (Legal items remain OPEN if unnamed)
- [ ] GS-07 vs GS-06: true exception ≠ missing bureau
- [ ] Identity insufficient → `AMBIGUOUS` preserved (GS-04)

---

## 6. Production adapters and data

- [ ] Named production adapters for LOS, documents, bureau, bank, tax/GST, exposure, policy, case, memo
- [ ] Purpose tokens scoped to `UNDERWRITING_RUNTIME`
- [ ] Restricted eval store **not** routable from underwriting runtime network
- [ ] Workshop `live_applications.csv` / 160-row fixture **not** the live book
- [ ] Source owners accept freshness contracts (bank 7 days, bureau ≤30 days, exposure ≤15 min) as inventory
- [ ] Stale / missing / conflict remain visible; engine PASS does not clear staleness
- [ ] PROD project/account separate from UAT
- [ ] Secrets only in enterprise secret store; no live keys in git

---

## 7. Identity, roles, pilot cohort

- [ ] Production IdP; workshop ALPHA/BETA **not** claimed as prod tenancy design
- [ ] Groups map to `RELATIONSHIP_MANAGER` / `CREDIT_ANALYST` / `SENIOR_UNDERWRITER` / `CREDIT_AUTHORITY` / `RISK_COMPLIANCE_EVAL` only
- [ ] `AI_AGENT` not in a human IdP group with credit buttons
- [ ] Pilot allowlist named (`pilot.cohort_allowlist`); empty allowlist = nobody in PROD
- [ ] Named production **book** id and uncomplicated-case definition
- [ ] Failure Lab 100% of memo/decision users (`TRAINING_PLAN.md` M5)
- [ ] RM cannot prepare memos or record final credit
- [ ] Eval users cannot write runtime decisions

---

## 8. Feature flags at GO

Record the snapshot (SHA + flag JSON) in the GO evidence pack.

| Flag | Required at first GO | Set? |
|---|---|---|
| `ui.human_decision` | On | [ ] |
| `ui.decision_trace` | On | [ ] |
| `ui.outcome_feedback` | On | [ ] |
| `ui.memo_assist` | On **only if** the three above are on; else Off | [ ] |
| `model.generation` | Off unless model-risk file exists | [ ] |
| `pilot.cohort_allowlist` | On with named list | [ ] |
| `ui.fairness_eval` | Off on underwriting runtime | [ ] |
| Isolation / authority / policy retrieve | **No off flag** | [ ] N/A — confirm absent |

Forbidden flags from `RELEASE_MANAGEMENT_PLAN.md` §3.2 are **absent** — [ ]

---

## 9. Observability, support, IR

- [ ] Source-health, degraded-mode, and tool-failure visible (`CRD-NFR-006`)
- [ ] Isolation canary (GS-08 class) on PROD
- [ ] Trace persist probed; ACK denied if write fails (RPO 0)
- [ ] L1–L3 named per `SUPPORT_MODEL.md`; hypercare rota **named** (clocks no longer OPEN)
- [ ] Sev 1 path understood: fail-closed; no AI-final to recover capacity (`INCIDENT_RESPONSE_PLAN.md`)
- [ ] Exec honesty strip ready (`EXECUTIVE_DASHBOARD_SPEC.md` §4) — even if BI is a scheduled pack
- [ ] On-call for adapters and source health

Platform monthly % (NFR-AVAIL-03) — [ ] named by Operations **or** [ ] explicitly **non-claimed**

Concurrent analysts / daily applications — [ ] named **or** [ ] GO still blocked on capacity OPEN (`NFR-SCALE-02`)

---

## 10. Rollback and DR (G-RB-01)

- [ ] `ROLLBACK_PLAYBOOK.md` owners named
- [ ] Catalog restore drill executed: previous ACTIVE restored; **v2.9 not activated**
- [ ] Last signed workbench SHA redeploy drilled (or table-top with artefact hashes)
- [ ] `model.generation` kill-switch drilled
- [ ] Regional: DR replicates traces + catalog + IAM; isolation verified on DR
- [ ] Regional RTO **named** by Operations **or** GO remains blocked on this OPEN item
- [ ] Failback rule: hashes of ACTIVE 3.2 (or current ACTIVE) and trace integrity verified
- [ ] Drill evidence stored; prior inconvenient results not overwritten

**2026-09-10:** G-RB-01 **FAIL** — this section **fails**; production GO BLOCKED.

---

## 11. Model risk (if LLM wired)

- [ ] Model-risk file; eval report id
- [ ] GS-09, GS-14, GS-08 (if retrieval), GS-10 with model killed
- [ ] `versions.model` / `versions.prompt` not silently `NONE`
- [ ] Vector cannot override policy (QT-02)
- [ ] If no LLM: `versions.model=NONE` and `model.generation=off` — still valid GO for **manual + stub** if all other §5.3 items pass

---

## 12. Legal / privacy residuals (visible, not invented)

- [ ] Retention **days** named by Legal **or** reconstructability BINDING with duration still OPEN and **called out** in GO caveats
- [ ] DPIA / jurisdiction: `OPEN_DECISION` remains visible; no invented sector-wide label
- [ ] Recourse notices: human authority; AI is not the decision-maker (Legal OPEN items listed)

These OPEN items **do not** get closed by ticking a box in this file without a CR.

---

## 13. Value and communications

- [ ] Value clock **not** started until this GO is signed (`VALUE_REALIZATION_FRAMEWORK.md`)
- [ ] Steerco script: no QT-05 from fixture; HG first
- [ ] Forbidden messages unpublished (`CHANGE_MANAGEMENT_PLAN.md` §5)
- [ ] Applicant-facing copy (if any) reviewed — recourse is human

---

## 14. Sign-off (not yet granted)

| Role | Gate family | Signature | Date | Evidence id |
|---|---|---|---|---|
| Credit authority | G-AUTH-*, HG-01 | | | |
| Policy owner | G-POL-*, HG-02, HG-06 | | | |
| Security / privacy | G-ISO-01, HG-04, HG-05, HG-07 | | | |
| Model risk / evals | HG-02, QT-01 workbench, G-FB-*, model file | | | |
| Operations | G-RB-01, HG-08, observability, region OPEN named | | | |
| Credit Operations | Pilot book, training, hypercare, TAT labelling | | | |
| Independent reviewer | This checklist vs `PRODUCTION_READINESS_REVIEW.md` | | | |

**Independent reviewer production verdict 2026-09-10:** **Not production-ready.** Do not countersign until §2, §3 workbench, §6 adapters, and §10 G-RB-01 have fresh evidence.

---

## 15. Go / no-go

| If | Then |
|---|---|
| Any HG fail on UI | **NO-GO** |
| G-UI-01 incomplete | **NO-GO** |
| G-RB-01 undrilled or 2.9 used | **NO-GO** |
| Fixtures as live book | **NO-GO** |
| Memo UI without Human Decision | **NO-GO** |
| Isolation fail-open flag present | **NO-GO** |
| All of §0–§11 (and named OPEN dispositions in §9/§10/§12) | **GO** for **named pilot book only** — not org-wide market expansion |

Post-GO: execute `RELEASE_MANAGEMENT_PLAN.md` R4 hypercare. First rollback contact: Operations incident commander + Credit Policy (catalog) per `ROLLBACK_PLAYBOOK.md`.
