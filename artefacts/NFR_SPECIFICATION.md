# Non-Functional Requirements Specification — SME Credit Underwriting Intelligence Workbench

**Organization:** NexLend SME Finance (fictional)  
**Product:** SME Credit Underwriting Intelligence Workbench  
**Compiled:** 2026-09-10  
**CRD IDs:** `CRD-NFR-001`–`007`, `CRD-SEC-001`–`012`, `CRD-FR-008`–`011`, `CRD-BR-001`–`004`, `CRD-DATA-001`–`003`/`012`–`016`, HG-01–HG-08, QT-01–QT-05  
**Sources:** `specs/03_non_functional/NFR.md`, `specs/04_security_privacy/SECURITY_GOVERNANCE.md`, `artefacts/PRD.md`, `artefacts/PRODUCT_STRATEGY.md`, `artefacts/SUCCESS_METRICS.md`, `RELEASE_GATES.md`, `PRODUCTION_READINESS_REVIEW.md`, `evidence/01_enterprise_sources/source_inventory.csv`, `evidence/06_evaluations/acceptance_thresholds.yaml`  
**Companion catalog:** `artefacts/SLA_SLO_CATALOG.md`

This artefact **does not replace** `specs/03_non_functional/NFR.md`. If they disagree, the approved spec wins. It does **not** mark any `CRD-FR-*` or production SLO `VERIFIED`. It does **not** invent legal classifications, extra credit thresholds, or fairness cut-offs.

---

## 1. How these NFRs are graded

| Binding class | Meaning | May close production GO? |
|---|---|---|
| **BINDING** | Numeric or binary target already in approved policy, inventory, hard gates or quality targets | Only with fresh evidence at the required layer (contract / workbench / production) |
| **PROPOSED** | Production-estate design target. Not in original case evidence. Requires change-control + human sign-off before it is contractual | No, until accepted as a CR and evidenced |
| **OPEN** | Required control exists; duration/capacity/percentage is not named in the case | No, until a named value and owner exist |

**SLA** = promise to the underwriting organization (and, where stated, to the affected-person recourse path). Breach blocks the named promotion path.  
**SLO** = internal objective used to operate the service. Hard-control SLOs have **no error budget**.  
**Layer:** Contract (unittest / `evidence/sdd/`) ≠ Workbench (twelve screens) ≠ Production (live adapters). Workshop fixture TAT (89.5 / 218) and source-case TAT (142 / 648) are **not** these SLOs.

Current production-readiness residual (`PRODUCTION_READINESS_REVIEW.md` §4.8 / §4.11): no production platform SLO, no multi-AZ adapters, no rollback drill, no retention schedule, no DPIA. Those gaps stay visible.

---

## 2. Owners

Owners match `RELEASE_GATES.md` sign-off families and `source_inventory.csv` source owners. No extra lending authority is created.

| Owner | Scope |
|---|---|
| Credit Operations | TAT, traces, human override, case record durability |
| Credit Policy | Active policy version, rollback controller (never v2.9), invented-threshold ban |
| Credit Risk | Bureau freshness, tax reuse basis, restricted-eval exclusion |
| Data Partnerships | Bank consent, purpose, freshness, retention controls |
| Portfolio Risk | Exposure freshness |
| Lending Operations | LOS / document identity and workflow availability |
| Security / privacy | Tenant isolation, injection, IAM (production), purpose limitation |
| Risk / compliance eval | Separate `RISK_COMPLIANCE_EVAL` purpose; no legal fairness cutoff |
| Model risk / evals | QT-01, HG-02, learning-loop denylist, model/prompt versions |
| Operations | Observability, platform restore, G-RB-01 drill |
| Legal / compliance (qualified review) | Jurisdiction, retention **duration**, data-subject process — `OPEN_DECISION` |
| Engineering | Adapters, measurement pipelines, workbench instrumentation |

---

## 3. Performance

### NFR-PERF-01 — Uncomplicated-case turnaround

**Statement:** Uncomplicated-case end-to-end TAT MUST be under 30 minutes **without** degrading HG-01–HG-08 (`CRD-NFR-001`, `CRD-BR-001`, QT-05).

| Field | Value |
|---|---|
| Binding | **BINDING** (target). Achievement is **NOT PROVEN**. |
| SLA | Uncomplicated applications complete intake-to-authorized-decision in **< 30 minutes** on a **named production population**, with hard gates still passing. |
| SLO | Median uncomplicated TAT < 30 min; hard-gate fail rate = 0 on the same population. |
| Measurement method | Decision-trace timestamps: application as-of / intake event → `HumanDecision` recorded. Population labelled (production ≠ workshop 89.5 ≠ source 142). |
| Validation approach | Production time-and-motion on named book. Workshop GS-01 is behavioral, not a TAT proof. Do not report 89.5 or 142 as this SLO. |
| Owner | Credit Operations (measurement); Engineering (instrumentation) |

### NFR-PERF-02 — Source freshness visibility

**Statement:** Material evidence MUST expose source-specific freshness; stale bank MUST NOT be presented as current (`CRD-NFR-006`, QT-03, `DATA-FRESHNESS-BANK`).

| Field | Value |
|---|---|
| Binding | **BINDING** |
| SLA | 100% of material evidence envelopes in an underwriting context show `freshness_state` and authority. Bank summaries **> 7 days** are `stale` and `presented_as_current=false`. Bureau expected **≤ 30 days** unless policy is stricter. Exposure expected **≤ 15 minutes**. |
| SLO | QT-03 = 100%. GS-05 class incidents: stale visible, not current. Engine `PASS` does not clear staleness. |
| Measurement method | Envelope fields on BANK/BUREAU/EXPOSURE/LOS facts; source-health flags; as-of vs `event_time`/`update_time`. |
| Validation approach | GS-05 contract + workbench Evidence Reconciliation. Inventory: `source_inventory.csv`. |
| Owner | Data Partnerships (bank); Credit Risk (bureau); Portfolio Risk (exposure); Engineering (envelopes) |

### NFR-PERF-03 — Retrieval-route correctness

**Statement:** Retrieval MUST classify structured / graph / semantic / policy / memory before adapters run; vector MUST NOT override policy (`CRD-FR-004`, QT-02).

| Field | Value |
|---|---|
| Binding | **BINDING** |
| SLA | ≥ 95% of underwriting retrieval plans use the correct family; 0 policy-controlling hops selected by similarity. |
| SLO | QT-02 ≥ 95% **and** HG-06 = 0 (superseded policy not applied). |
| Measurement method | Hop traces: family, tool id, need, `controlling` flag (`CRD-DATA-009`). |
| Validation approach | GS-02 / GS-05 / GS-11 / GS-12 routing tests; workbench Hybrid Retrieval inspector (G-UI-01). Production adapters **not claimed**. |
| Owner | Engineering; Credit Policy (controlling hop) |

### NFR-PERF-04 — Interactive context assembly (production estate)

**Statement:** Task-specific context assembly MUST NOT dump the repository and MUST leave headroom inside the 30-minute TAT (`CRD-FR-001`). Interactive latency is **not** named in the case.

| Field | Value |
|---|---|
| Binding | **PROPOSED** (latency number). Slice semantics are **BINDING**. |
| SLA | Analyst receives a task/actor/tenant/as-of slice, not a corpus dump. Proposed production UX: p95 context+policy-gate round-trip **≤ 10 seconds** excluding external bureau/bank provider time. |
| SLO | p95 ≤ 10 s (proposed); 100% of assemblies record inclusion/exclusion reasons. |
| Measurement method | Server-side span `assemble_runtime_context` + `retrieve_active_policy` + `check_access_and_authority`; exclude provider RTT. |
| Validation approach | Load test on named production-like fixtures after workbench exists. Candidate 10 s requires Operations/Engineering CR before it is contractual. |
| Owner | Engineering |

---

## 4. Availability

### NFR-AVAIL-01 — Manual underwriting during AI outage

**Statement:** Manual underwriting MUST remain available if AI/context assistance is unavailable (`CRD-NFR-004`, `CRD-SEC-010`, `FALLBACK-001`, HG-08).

| Field | Value |
|---|---|
| Binding | **BINDING** |
| SLA | Credit decisioning does not depend on AI availability. During AI outage, policy, source health and required human role remain visible; the case is not blocked. |
| SLO | 100% of AI-outage incidents keep manual path executable (HG-08 = true). Fabricated assistance memos = 0. |
| Measurement method | Health flag `AI_ASSIST=UNAVAILABLE`; `assess_degraded_mode` = `AI_ASSISTANCE_UNAVAILABLE`; `emit_ai_assistance` = DENY; `manual_underwriting_view` executable. |
| Validation approach | GS-10 / AT-10 on contract **and** Failure Simulation / Human Decision screens. |
| Owner | Credit Operations; Operations (health signal); Engineering |

This is the **credit-path availability** SLO. It is not a platform “nines” claim. A platform monthly % for the UI is **OPEN** until Operations names it (see NFR-AVAIL-03).

### NFR-AVAIL-02 — Structured / policy outage abstention

**Statement:** If structured or policy retrieval is out, the system MUST abstain rather than invent bank, bureau or policy facts (`CRD-DATA-013` `MANDATORY_ABSTENTION`).

| Field | Value |
|---|---|
| Binding | **BINDING** |
| SLA | No recommendation that requires invented bank/bureau/policy is emitted when those retrievals are down. Manual underwriting on surviving LOS/policy evidence remains executable. |
| SLO | 100% of structured/policy-out incidents → `MANDATORY_ABSTENTION`; invented facts = 0. |
| Measurement method | Degraded-mode enum; null bureau/bank envelopes; policy retrieval `PolicyUnavailable`. |
| Validation approach | Workshop retrieval-family outage override; GS-06 missing bureau; do not conflate with GS-07 exception. |
| Owner | Engineering; Credit Policy |

### NFR-AVAIL-03 — Workbench / adapter platform availability

**Statement:** Production workbench availability is **not** in case evidence. Production GO is blocked until Operations names and drills it (`PRODUCTION_READINESS_REVIEW.md` §4.8).

| Field | Value |
|---|---|
| Binding | **OPEN** (percentage). Observability of health is **BINDING** (`CRD-NFR-006`). |
| SLA | Until named: “source health, degraded mode and tool failures are visible.” Candidate for internal beta (not case evidence): Control Tower + Human Decision **99.5%** monthly excluding agreed maintenance, **excluding** AI generation. |
| SLO | Candidate 99.5% (PROPOSED). Error budget does **not** apply to HG-*. |
| Measurement method | Synthetic probes on Human Decision and Control Tower; exclude AI token latency. |
| Validation approach | Named SLO in a CR + 30 days of probes before production GO. Workshop TENANT-ALPHA/BETA is not a production AZ design. |
| Owner | Operations |

---

## 5. Reliability

### NFR-REL-01 — Golden-scenario behavior

**Statement:** Golden-scenario pass rate MUST be ≥ 95% **and** all hard-gate scenarios passing (QT-01, `CRD-NFR-007`).

| Field | Value |
|---|---|
| Binding | **BINDING** |
| SLA | GS-01–GS-15 behaviors in `CRD-AC-001`–`015` hold on the claimed layer. |
| SLO | QT-01 ≥ 95% with HG-01–HG-08 passing. Invented threshold = **critical** fail. |
| Measurement method | `run_golden_evaluation_suite` / Prompt 13 dimensions; persist report under `evidence/sdd/`. |
| Validation approach | Contract 2026-09-10: 15/15 MET **at contract only**. Workbench QT-01 not claimed. Production QT-01 not claimed. Re-run on UI path before workbench claim. |
| Owner | Model risk / evals |

### NFR-REL-02 — Four degraded modes stay distinct

**Statement:** Assistance MUST emit exactly one primary mode from `DECISION_CAN_CONTINUE` / `REQUIRES_ADDITIONAL_EVIDENCE` / `AI_ASSISTANCE_UNAVAILABLE` / `MANDATORY_ABSTENTION` (`CRD-FR-008`, `CRD-DATA-013`).

| Field | Value |
|---|---|
| Binding | **BINDING** |
| SLA | Missing bureau is not a policy exception; stale bank is not “current”; AI outage is not case-blocked. |
| SLO | 100% of GS-05/06/07/10 classifications match the table in `CRD-DATA-013`. |
| Measurement method | `assess_degraded_mode` primary mode + exception class. |
| Validation approach | GS-05 vs GS-06 vs GS-07 vs GS-10 tests; Failure Simulation screen. |
| Owner | Credit Operations; Engineering |

### NFR-REL-03 — No fabricated missing facts

**Statement:** Unavailable bureau or bank values MUST NOT be invented (`CRD-TOOL-001`, `CRD-AC-006`).

| Field | Value |
|---|---|
| Binding | **BINDING** |
| SLA | Explicit null/unavailable envelope; no generated score band or cashflow. |
| SLO | Fabricated bureau/bank fact count = 0. |
| Measurement method | Envelope `value` null + `freshness_state=unavailable`; memo scan for invented bureau/bank claims. |
| Validation approach | GS-06; degraded-mode scan. |
| Owner | Credit Risk (bureau); Data Partnerships (bank); Engineering |

---

## 6. Scalability

### NFR-SCALE-01 — Tenant isolation at any tenant count

**Statement:** Tenant isolation is a pre-retrieval code filter and MUST hold as tenant volume grows (`CRD-NFR-002`, `CRD-SEC-004`, HG-04).

| Field | Value |
|---|---|
| Binding | **BINDING** (zero leaks). Concurrent-user capacity is **OPEN**. |
| SLA | 0 successful cross-tenant retrievals or displays on structured, graph, vector, memory, context, tool or UI paths. |
| SLO | HG-04 = 0; G-ISO-01 closed. Prompt text cannot widen scope. |
| Measurement method | `inspect_retrieval_layers` + output scan for foreign-tenant markers; production IAM denial logs when adapters exist. |
| Validation approach | GS-08 at contract and on every retrieval UI. Repeat under multi-tenant load once capacity is named. |
| Owner | Security / privacy; Engineering |

### NFR-SCALE-02 — Workshop and production capacity

**Statement:** Workshop verification uses 15 live applications and the 160-row fixture (`CRD-NFR-007`). Production concurrent underwriters and application volume are **not** in the case.

| Field | Value |
|---|---|
| Binding | **BINDING** (workshop corpus). Production capacity **OPEN**. |
| SLA | Workshop: deterministic GS-01–GS-15 on SME-L001–L015. Production: Operations SHALL name concurrent-analyst and daily-application SLOs before GO. |
| SLO | Workshop: 15/15 scenarios reproducible. Production candidate: **OPEN**. |
| Measurement method | Eval suite runtime; later, queue depth / concurrent sessions. |
| Validation approach | `tests/test_crd_ac_001_015_eval_suite.py`. Do not use the 160-row TAT as capacity proof. |
| Owner | Engineering (workshop); Operations (production naming) |

---

## 7. Security

### NFR-SEC-01 — Tenant isolation before retrieval and display

**Statement:** `CRD-NFR-002`, `CRD-SEC-004`, `CRD-DATA-012`, `DATA-TENANT`.

| Field | Value |
|---|---|
| Binding | **BINDING** |
| SLA | TENANT-ALPHA actor receives **zero** TENANT-BETA application content. |
| SLO | HG-04 = 0; G-ISO-01 closed. |
| Measurement method | Pre-adapter tenant predicate; empty content on DENY; display scan. |
| Validation approach | GS-08 / AT-08 on all five retrieval families + UI. Production IAM/pentest **NOT PROVEN**. |
| Owner | Security / privacy |

### NFR-SEC-02 — Prompt injection / untrusted content

**Statement:** Untrusted uploaded or retrieved text cannot override instructions or policy (`CRD-SEC-007`, HG-07).

| Field | Value |
|---|---|
| Binding | **BINDING** |
| SLA | Applicant documents and historical memos are DATA. Embedded instructions are not followed. Policy version, engine result and required role unchanged. |
| SLO | HG-07 = 0; `FOLLOW_DOCUMENT_INSTRUCTION` = DENY. |
| Measurement method | Document trust class `UNTRUSTED_CONTENT`; injection-control evidence on envelope; policy hash unchanged. |
| Validation approach | GS-09 / `DOC-009-FIN`; AT-09. Filters are code, not model obedience. |
| Owner | Security / privacy; Credit Policy |

### NFR-SEC-03 — No autonomous AI credit authority

**Statement:** `CRD-SEC-001`, `CRD-FR-011`, HG-01, `CREDIT-AUTH-001`.

| Field | Value |
|---|---|
| Binding | **BINDING** |
| SLA | AI cannot approve, decline, condition, price, change a facility, authorize large limits, approve exceptions or issue adverse determinations. |
| SLO | HG-01 = 0; G-AUTH-01 closed. |
| Measurement method | `check_access_and_authority` / `handoff_recommendation` allow/deny; `AI_AGENT` final = NO. |
| Validation approach | GS-02, GS-07, GS-13, GS-14. Re-run on Human Decision UI. |
| Owner | Credit authority (sign-off); Engineering (gate) |

### NFR-SEC-04 — Active policy not modified by generation

**Statement:** `CRD-SEC-002`, HG-02, HG-06.

| Field | Value |
|---|---|
| Binding | **BINDING** |
| SLA | Only `CREDIT-POLICY-3.2` controls. Generated thresholds not in 3.2 are rejected. v2.9 is historical only. |
| SLO | HG-02 = 0; HG-06 = 0; G-POL-01/02 closed. |
| Measurement method | `retrieve_active_policy` controlling flag; `scan_generated_policy_claims`; protected-artifact hashes. |
| Validation approach | GS-12, GS-14 (INR 2,500,000 probe). Critical fail on invented threshold. |
| Owner | Credit Policy |

---

## 8. Privacy

### NFR-PRIV-01 — Restricted evaluation attributes out of runtime

**Statement:** `CRD-NFR-003`, `CRD-SEC-005`, HG-05.

| Field | Value |
|---|---|
| Binding | **BINDING** |
| SLA | `restricted_fairness_eval_sample.csv` and other `EVALUATION_ONLY_APPROVED_PURPOSE` rows do not enter runtime decision context. Natural-person `decision_feature_eligible=CONDITIONAL` attributes are not default decision features. |
| SLO | HG-05 = 0; G-FB-03 closed. |
| Measurement method | Context exclusion reason `RESTRICTED_ATTRIBUTE`; feedback inject path raises. |
| Validation approach | GS-03, GS-15. Fairness screen is a **separate** purpose (`RISK_COMPLIANCE_EVAL`). No legal fairness threshold is defined here. |
| Owner | Risk / compliance eval; Security / privacy |

### NFR-PRIV-02 — Purpose limitation and consent on material facts

**Statement:** Permissible-use policy + `CRD-DATA-001` purpose/consent fields. Bank data is restricted (`source_inventory.csv` `RESTRICTED`).

| Field | Value |
|---|---|
| Binding | **BINDING** (fields and purpose split). Legal basis text is **OPEN** (qualified legal review). |
| SLA | Runtime purpose is `UNDERWRITING_RUNTIME` / `UNDERWRITING_VERIFIED`. Bureau requires verified permissible purpose. Tax reuse basis verified for the workflow. Evaluation purpose cannot ride the underwriting path. |
| SLO | 100% of material envelopes used by AI or gates carry `purpose` and `consent_status`. |
| Measurement method | Envelope audit; retrieval filter on purpose. |
| Validation approach | GS-03 purpose flags; AT-18 provenance. Production DPIA **NOT PROVEN**. |
| Owner | Data Partnerships (bank); Credit Risk (bureau/tax); Security / privacy |

### NFR-PRIV-03 — Affected-person minimization

**Statement:** Sole-trader and guarantor cases require explicit affected-person analysis; generated personal attributes are forbidden (`CRD-SEC-008`, `CRD-DATA-011`).

| Field | Value |
|---|---|
| Binding | **BINDING** |
| SLA | `SoleTraderBusiness` ≠ owner `NaturalPerson`; guarantor ≠ borrower entity. No invented age, gender, religion, caste, ethnicity, marital status, disability or nationality. |
| SLO | GS-03 / GS-13 pass; invented personal-attribute count = 0. |
| Measurement method | `analyze_person_impact`; `scan_generated_person_claims`. |
| Validation approach | `CRD-AC-003`, `CRD-AC-013`. Jurisdiction label remains `OPEN_DECISION`. |
| Owner | Credit Operations; Risk / compliance eval |

---

## 9. Data retention

Case evidence requires **controls**, not a duration. Production readiness lists “no retention schedule” as a residual. Durations below that are not in `CREDIT-POLICY-3.2` are **OPEN**.

### NFR-RET-01 — Decision-trace reconstructability window

**Statement:** Traces MUST remain reconstructable for the recorded decision and approved recourse path (`CRD-FR-009`, `CRD-SEC-011`, AT-16). Hidden CoT MUST NOT be stored (AT-17).

| Field | Value |
|---|---|
| Binding | **BINDING** (must retain enough to reconstruct). **OPEN** (calendar years). |
| SLA | For every recorded `HumanDecision`, the trace envelope remains retrievable for the appeal/recourse process in `human_authority_and_recourse_policy.md`. Legal-hold MUST be supportable. Calendar retention is named by Legal before production GO. |
| SLO | Trace completeness vs AT-16 = 100% at record time; forbidden CoT keys = 0. Duration SLO = **OPEN**. |
| Measurement method | `record_decision_trace` / `validate_trace`; durable store existence (production **NOT PROVEN**). |
| Validation approach | AT-16/17 on GS-01/07/13; Decision Trace screen. Retention **days** require Legal CR — do not invent a statutory period here. |
| Owner | Credit Operations (completeness); Legal / compliance (duration); Engineering (store) |

### NFR-RET-02 — Segregated evaluation data

**Statement:** Restricted fairness-eval rows remain `EVALUATION_ONLY_APPROVED_PURPOSE` and MUST NOT land in runtime stores via feedback (`CRD-DATA-016`, G-FB-03).

| Field | Value |
|---|---|
| Binding | **BINDING** |
| SLA | Eval-only datasets are stored and accessed only under `RISK_COMPLIANCE_EVAL`. Feedback cannot copy them into underwriting context. |
| SLO | Runtime inject count = 0. |
| Measurement method | Path denylist; store ACLs when production stores exist. |
| Validation approach | GS-15 inject deny. |
| Owner | Risk / compliance eval; Engineering |

### NFR-RET-03 — Purpose-limited bank and bureau data

**Statement:** Bank transaction data: consent/legal basis, **minimization and retention controls apply** (`data_permissible_use_policy.md`). Bureau: purpose + freshness.

| Field | Value |
|---|---|
| Binding | **BINDING** (controls exist). Retention **days** **OPEN**. |
| SLA | Bank/bureau payloads used for underwriting are purpose-limited and minimized to the workflow. Retention calendar named by Legal/Data Partnerships before production GO. |
| SLO | 100% of BANK envelopes have consent/purpose; stale >7 days not presented as current. Duration **OPEN**. |
| Measurement method | Envelope consent/purpose; data-partner contract register (production). |
| Validation approach | GS-05 freshness; permissible-use policy review. Do not invent a bank retention day-count. |
| Owner | Data Partnerships; Legal / compliance |

---

## 10. Recovery objectives

### NFR-REC-01 — AI-outage recovery of the credit path

**Statement:** Credit path RTO for AI failure is **immediate fallback**, not restore-AI-first (`FALLBACK-001`, HG-08).

| Field | Value |
|---|---|
| Binding | **BINDING** |
| SLA | When AI assistance fails, manual underwriting continues without waiting for model restore. Policy/source/authority remain visible. |
| SLO | Credit-path RTO for AI outage = **0 additional wait** beyond detecting unavailability. AI restore RTO is a separate Operations objective (**OPEN**). |
| Measurement method | Time from `AI_ASSIST=UNAVAILABLE` to successful `manual_underwriting_view`. |
| Validation approach | GS-10 drill on workbench Failure Simulation. |
| Owner | Credit Operations; Operations |

### NFR-REC-02 — Policy / catalog rollback

**Statement:** G-RB-01. Feedback write-protection is prevention, not rollback. Superseded `CREDIT-POLICY-2.9` is **never** a production rollback controller.

| Field | Value |
|---|---|
| Binding | **BINDING** (never v2.9). Drill existence **OPEN** (blocks production). |
| SLA | Restore previous **ACTIVE** policy bundle (not 2.9). Ontology, prompts, models and gold labels restore only through governed change control. |
| SLO | Rollback drill recorded (G-RB-01) before production GO. Ungoverned write count = 0 (`FEEDBACK-001`). |
| Measurement method | Catalog version history; protected-artifact hashes; drill runbook timestamp. |
| Validation approach | Table-top + restore drill; GS-12 still holds after rollback. |
| Owner | Credit Policy; Operations |

### NFR-REC-03 — Decision-record RPO

**Statement:** A reconstructable recommendation cannot be acknowledged if the trace is lost (`CRD-FR-009`).

| Field | Value |
|---|---|
| Binding | **BINDING** (no silent loss). Platform backup RPO **OPEN**. |
| SLA | `HumanDecision` is not confirmed to the operator unless `record_decision_trace` has persisted the AT-16 envelope. |
| SLO | RPO for decision + trace = **0** (synchronous persist). Operational log RPO **OPEN** until Operations names it. |
| Measurement method | Write barrier: decision API returns success only after trace persist; chaos test of store failure. |
| Validation approach | AT-16; production durable store **NOT PROVEN**. |
| Owner | Credit Operations; Engineering; Operations (backups) |

---

## 11. Auditability

### NFR-AUD-01 — Reconstructable decision trace

**Statement:** `CRD-NFR-005`, `CRD-FR-009`, `CRD-SEC-011`, AT-16.

| Field | Value |
|---|---|
| Binding | **BINDING** |
| SLA | Every material recommendation or controlled outcome can be reconstructed: task, application, actor, tenant, context as-of, retrievals, source refs, freshness, authority, policy checks/versions, tools, versions, draft, concise rationale, uncertainty, human action, outcome. |
| SLO | AT-16 field completeness = 100% on recorded traces. Generated explanation is not policy evidence. |
| Measurement method | `validate_trace` required fields; sample GS-01/07/13. |
| Validation approach | Contract PASS 2026-09-10. Decision Trace **screen** OPEN. Durable audit store NOT PROVEN. |
| Owner | Credit Operations; Model risk / evals |

### NFR-AUD-02 — No hidden chain-of-thought

**Statement:** `CRD-SEC-011`, AT-17.

| Field | Value |
|---|---|
| Binding | **BINDING** |
| SLA | Traces and UI do not require or persist hidden model CoT (`chain_of_thought`, `cot`, `hidden_reasoning`). |
| SLO | Forbidden-key count = 0. |
| Measurement method | Serialization scan `FORBIDDEN_TRACE_KEYS`. |
| Validation approach | AT-17 tests. |
| Owner | Model risk / evals; Engineering |

### NFR-AUD-03 — Material-factor provenance coverage

**Statement:** HG-03 = 100% on generated FACT statements (`CRD-NFR-005`, `CRD-SEC-003`).

| Field | Value |
|---|---|
| Binding | **BINDING** |
| SLA | Every material AI-assisted FACT cites evidence_id / source-record ref, or the memo is blocked. Inferences labelled `[INFERENCE]`. |
| SLO | HG-03 = 100%. |
| Measurement method | Memo grounding coverage; AT-18. |
| Validation approach | GS-01 memo; GS-14 reject ungrounded/invented policy. UI not claimed. |
| Owner | Credit Operations; Engineering |

---

## 12. Compliance

This product does **not** assert a jurisdiction, licence, or fairness legal threshold. Compliance here means **adherence to approved workshop/production-shaped controls**. Sector-wide regulatory labels remain `OPEN_DECISION` for qualified legal/compliance review (`artefacts/PRD.md` §20).

### NFR-CMP-01 — Versioned active credit policy

**Statement:** `CRD-SEC-002`, HG-06, G-POL-01.

| Field | Value |
|---|---|
| Binding | **BINDING** |
| SLA | Controlling bundle is `CREDIT-POLICY-3.2`. Known literals remain INR **5,000,000** and **7-day** bank freshness. No invented thresholds. |
| SLO | HG-06 = 0; HG-02 = 0. |
| Measurement method | Policy retrieval `controlling`; fidelity scan. |
| Validation approach | GS-12, GS-14. |
| Owner | Credit Policy |

### NFR-CMP-02 — Fairness / impact evaluation purpose split

**Statement:** Fairness policy: segment diagnostics do **not** define a legal fairness threshold. Protected attributes require approved purpose (`CRD-SEC-005`, `CRD-SEC-008`).

| Field | Value |
|---|---|
| Binding | **BINDING** (split). Legal threshold **forbidden to invent**. |
| SLA | Runtime underwriting ≠ `RISK_COMPLIANCE_EVAL`. Restricted attributes are evaluation-only unless a later CR says otherwise. |
| SLO | HG-05 = 0; Fairness screen absent from runtime feature flags. |
| Measurement method | Purpose on context request; eval-sample exclusion. |
| Validation approach | GS-03; P2-02 screen when built. Production eval-purpose run NOT PROVEN. |
| Owner | Risk / compliance eval |

### NFR-CMP-03 — Governed learning loop

**Statement:** `CRD-SEC-012`, `CRD-FR-010`, `CRD-AC-015`, `FEEDBACK-001`.

| Field | Value |
|---|---|
| Binding | **BINDING** |
| SLA | `AI_ACCEPTED` / modify / reject, human decisions and portfolio outcomes do not auto-write policy, ontology, prompts, models or gold labels. Missing outcomes are not invented. |
| SLO | G-FB-01–03 closed; ungoverned write count = 0. |
| Measurement method | `capture_outcome_feedback` destination `GOVERNED_REVIEW`; protected hashes. |
| Validation approach | GS-15. Outcome & Feedback UI OPEN. Production dual-control ops NOT PROVEN. |
| Owner | Model risk / evals; Credit Policy |

### NFR-CMP-04 — Human authority, adverse reason and recourse

**Statement:** `CRD-SEC-009`, `CRD-FR-011`, `human_authority_and_recourse_policy.md`.

| Field | Value |
|---|---|
| Binding | **BINDING** |
| SLA | Adverse/conditional outcomes preserve human decision, material reason/source and approved appeal path. AI has no adverse or recourse authority. |
| SLO | GS-13: AI `ISSUE_ADVERSE` / `DECLINE` = DENY; factor grounded on source evidence (`EXP-013` / `POL-ARREARS-02` in workshop). |
| Measurement method | Authority gate; adverse-factor triple (code, evidence_id, source). |
| Validation approach | `CRD-AC-013`. Recourse **calendar SLA** for appeals is **OPEN** (not in policy text). |
| Owner | Credit authority; Credit Operations |

### NFR-CMP-05 — Workshop vs production evidence boundary

**Statement:** `CRD-NFR-007`. Production claims require separate production evidence.

| Field | Value |
|---|---|
| Binding | **BINDING** |
| SLA | Fixture/eval PASS is not a production compliance attestation. Live credit data is not replaced by generated fixtures. |
| SLO | Every external compliance claim cites layer (contract / workbench / production) and population. |
| Measurement method | Release-gate table; readiness review residuals kept visible. |
| Validation approach | `RELEASE_GATES.md` §5.3 checklist before any production GO. |
| Owner | Independent reviewer; Operations |

---

## 13. Open decisions (do not guess)

| Item | Blocks | Required to close |
|---|---|---|
| Workbench/UI monthly availability % (NFR-AVAIL-03) | Production GO | Operations CR + probe evidence |
| Production concurrent-analyst / daily-volume (NFR-SCALE-02) | Production capacity plan | Operations naming |
| Trace/bank/bureau retention **days** (NFR-RET-*) | Production GO | Legal / Data Partnerships CR |
| Appeal/recourse calendar SLA (NFR-CMP-04) | Applicant-facing ops | Credit Operations + Legal |
| AI model restore RTO (distinct from credit-path RTO) | Model ops | Operations + model risk |
| Production IAM / pentest / DPIA | Production security/privacy GO | Security + Legal |
| Interactive p95 10 s candidate (NFR-PERF-04) | Contractual UX SLA | Engineering CR |
| Jurisdiction / licensing label | Legal marketing claims | Qualified legal review |

---

## 14. Current evidence (2026-09-10)

| Layer | Hard-control NFRs | Platform nines / RTO-RPO days / retention days |
|---|---|---|
| Contract | HG-01–HG-08 PASS; QT-01 MET at contract | Not applicable |
| Workbench | OPEN (0/12 screens) | OPEN |
| Production | BLOCKED | OPEN / NOT PROVEN |

Do not treat this specification as closure of `PRODUCTION_READINESS_REVIEW.md` residuals.
