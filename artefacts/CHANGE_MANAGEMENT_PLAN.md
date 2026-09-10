# Change Management Plan — SME Credit Underwriting Intelligence Workbench

**Compiled:** 2026-09-10  
**CRD IDs:** `CRD-BR-001`–`004`, `CRD-FR-007`, `CRD-FR-011`, `CRD-SEC-001`–`012`, HG-01–HG-08  
**Companions:** `artefacts/ADOPTION_STRATEGY.md`, `artefacts/TRAINING_PLAN.md`, `artefacts/SUPPORT_MODEL.md`, `artefacts/SUCCESS_METRICS.md`, `90_DAY_MODERNIZATION_ROADMAP.md`, `RELEASE_GATES.md`  
**Status:** Target enterprise change plan. **Production GO is BLOCKED** (0/12 screens; G-RB-01 undrilled). This plan does not authorize live lending or claim QT-05.

**Change thesis:** Move NexLend from fragmented nine-system underwriting and “add a credit chatbot” pressure to **architecture-first assistance**: trustworthy context, human credit authority, reconstructable traces. The LLM is not the architecture.

---

## 1. Change vision and what must not change

| Must change | Must not change |
|---|---|
| Where analysts reconcile evidence (workbench vs copy-paste) | Who holds final credit / adverse / exception / recourse |
| Visibility of stale, missing, conflict, policy version | ACTIVE catalog = `CREDIT-POLICY-3.2` until a dual-control CR |
| Memo drafting with provenance | Restricted attributes as runtime features |
| Learning via `GOVERNED_REVIEW` | `AI_ACCEPTED` as gold or policy |
| Honest layering: contract vs workbench vs production | Mixing 89.5 / 142 minutes with the <30-minute target |

Sponsor message: **faster TAT is failure if hard gates degrade.**

---

## 2. Stakeholder groups

| Group | Roles | Interest | Change risk if ignored |
|---|---|---|---|
| **Sponsors** | Credit Policy owner; Credit authority; independent reviewer | Policy fidelity, no AI credit, production sign-off | Silent GO; v2.9 rollback folklore |
| **Primary users** | `CREDIT_ANALYST` | Context, grounded memo, less lookup | Shadow chatbots; invented “revenue” |
| **Authority users** | `SENIOR_UNDERWRITER`, `CREDIT_AUTHORITY` | Engine role vs LOS assignment; exceptions vs missing data | Rubber-stamp AI; GS-02/07/13 bypass |
| **Channel** | `RELATIONSHIP_MANAGER` | Assigned-app status only | Expecting to approve in the workbench |
| **Risk / fairness** | `RISK_COMPLIANCE_EVAL` | Separate eval purpose | Restricted sample in runtime |
| **Control functions** | Security/privacy; Model risk/evals; Legal/compliance (`OPEN_DECISION`) | Isolation, injection, traces, no invented cutoff | Fail-open “to help adoption” |
| **Source owners** | Lending Ops, Credit Risk, Data Partnerships, Portfolio Risk | Adapters, freshness, not replaced by generated data | Fixture-as-live-book |
| **Delivery** | Engineering; Operations; Credit Operations (L1/L2) | Screens display gates; on-call | Support that disables filters |
| **Affected persons** | SME, sole trader, natural-person guarantor | Recourse is human | AI-issued decline narrative |
| **Exec / demo audience** | Leadership under “add AI” pressure | Turnaround story | Claiming workshop demo as production |

`AI_AGENT` is not a stakeholder to “onboard”; it is a bounded system actor.

---

## 3. Adoption barriers (summary)

Full treatment: `artefacts/ADOPTION_STRATEGY.md`.

| Barrier | Typical quote | Countermeasure |
|---|---|---|
| Chatbot expectation | “Just let it approve the easy ones.” | Training + Human Decision before memo UI; HG-01 |
| TAT pressure | “Show we hit 30 minutes using the fixture.” | Population labelling; SM-01 not claimed from 89.5/142 |
| Copy-paste habit | “I’ll still pull bank from the PDF.” | Evidence Reconciliation; GS-11/05 drills |
| Role confusion | “LOS says I’m senior, so I can authorize 5.2m.” | Engine role wins (GS-02) |
| Exception queue mix | “No bureau = exception.” | GS-06 vs GS-07 |
| Trust deficit | “AI will hide stale data.” | Stale stays visible; Failure Simulation |
| Over-trust | “The memo looks complete, ship it.” | HG-03; reject invented thresholds (GS-14) |
| Fairness misuse | “Give me a cutoff from the cohort chart.” | Eval mode only; no invented legal threshold |
| Support anti-pattern | “Turn off isolation for this VIP.” | IR standing orders; Sev 1 |
| No UI yet | “We trained on slides, then nothing.” | Do not run end-user rollout before G-UI-01 |

---

## 4. Rollout phases (aligned to release gates)

Do not skip to PROD because training is complete.

| Phase | Environment | Who | Change activity | Exit |
|---|---|---|---|---|
| **0 — Contract awareness** | TEST (now) | Delivery, Policy, Model risk | Brief: gates exist, screens do not | Operators know assistance ≠ decision |
| **1 — Workbench beta** | UAT | Designated analysts + authority | Onboarding + Failure Lab on SME-L001–L015 | G-UI-01; HG on **UI** path |
| **2 — Fairness + feedback** | UAT | + Risk/compliance eval | Eval-mode training; GS-15 | Restricted sample still out of runtime |
| **3 — Production-shaped** | Pre-prod adapters | Source owners + Ops | Adapter runbooks; no fixture book | Named adapters; G-RB-01 drill |
| **4 — Production** | PROD | Signed roles only | Hypercare; SM-01 only on named population | `RELEASE_GATES.md` §5.3 |

Phases 1–4 are **blocked** on current repo state (0/12 screens). Phase 0 may proceed.

Horizon mapping: days 1–30 ≈ phase 1 enablement **once screens exist**; 31–60 ≈ phase 2; 61–90 ≈ phase 3, **not** default GO.

---

## 5. Communication plan

| Audience | Message | Channel | Cadence | Owner |
|---|---|---|---|---|
| All credit staff | Architecture first; AI drafts; humans decide; engine role; stale/conflict stay visible | Town hall + one-pager | Phase gate | Credit Operations |
| Analysts | How to use Control Tower → memo → Human Decision; GS failure modes | Training (`TRAINING_PLAN.md`) | Before UAT access | Credit Operations + Engineering |
| Senior UW / Credit authority | You are not optional; AI cannot cover GS-02/07/13 | Role clinic | Before UAT | Credit Policy + Credit authority |
| RM | Status only; no decision | Short brief | Phase 1 | Credit Operations |
| Risk/compliance eval | Separate purpose; no cutoff invention | Eval clinic | Phase 2 | Risk / compliance eval |
| Security / model risk | Isolation, injection, learning-loop denylist | Control briefing | Each promote | Security; Model risk |
| Exec | Layer honesty; TAT populations; GO blocked until §5.3 | Steerco | 30/60/90 checkpoints | Independent reviewer + sponsors |
| Source owners | Workbench consumes you; does not replace you | Adapter working group | Phase 3 | Operations |
| Applicants (when PROD) | Recourse is human; AI is not the decision-maker | Recourse notices (Legal OPEN) | At adverse/conditional | Credit Operations + Legal |

**Forbidden communications:** “The model now approves uncomplicated cases.” “We achieved 30 minutes on the 160-row file.” “v2.9 is the rollback.” “Ignore the injection warning.”

**Checkpoint questions in every steerco** (roadmap): bypassed gates? generated text as policy? feedback wrote 3.2/prompts/models/gold? HG re-run on UI? TAT population labelled?

---

## 6. User onboarding (process)

Detail: `TRAINING_PLAN.md`. Change-management sequence:

1. **Access:** IdP group = actual role matrix (not “everyone is analyst”).
2. **Prerequisite:** Phase training complete + Failure Lab (GS-08/09/10/14 minimum for any memo access).
3. **First cases:** SME-L001 (happy) then L005/L011 (stale/conflict) — not L002/L013 until authority clinic done.
4. **Buddy:** Credit Operations L2 on first Human Decision.
5. **Hypercare:** L1 staffed per `SUPPORT_MODEL.md` (clocks OPEN until named).
6. **Offboarding:** Remove role; do not leave `CREDIT_AUTHORITY` in UAT after beta.

No onboarding onto PROD until §5.3 and named production adapters.

---

## 7. Training, success, support transition

| Topic | Where specified |
|---|---|
| Curricula by persona | `artefacts/TRAINING_PLAN.md` |
| Barriers, enablement, adoption KPIs | `artefacts/ADOPTION_STRATEGY.md` |
| SM-01–SM-08, HG, QT | `artefacts/SUCCESS_METRICS.md` — value metrics **after** hard gates |
| L1→L3 and hypercare | `artefacts/SUPPORT_MODEL.md`; transition in Adoption §6 |

---

## 8. Sponsorship and RACI (change)

| Activity | A | R | C | I |
|---|---|---|---|---|
| Change narrative | Credit Policy | Credit Operations | Credit authority | Exec |
| UAT user list | Credit Operations | Credit Operations | Security (IAM) | Engineering |
| Training delivery | Credit Operations | Training lead (named at UAT) | Engineering, Policy, Model risk | Users |
| Hard-gate communication | Independent reviewer | Model risk | Security, Policy | All users |
| Production GO message | Independent reviewer | Sponsors | All sign-off families | Org |
| Support hypercare | Operations | L1 Credit Operations | Engineering | Users |

---

## 9. Resistance and reinforcement

| Behaviour to stop | Reinforcement |
|---|---|
| Asking support to approve | Ticket refused; engine role |
| Pasting injection text as instruction | Security Sev 1; GS-09 drill |
| Averaging bank/tax | GS-11 in training; memo reject |
| Reporting fixture TAT as QT-05 | Steerco correction |
| Using AI accept to change policy | G-FB-01; GOVERNED_REVIEW only |

Positive: time saved on **grounded** memos (SM-05) only after HG-03 holds on the UI path.

---

## 10. Readiness of this plan (2026-09-10)

- [x] Stakeholder map from role matrix + inventory owners  
- [ ] Named training lead and UAT cohort  
- [ ] G-UI-01 (onboarding blocked)  
- [ ] Comms artefacts beyond this file  
- [ ] Production hypercare rota (OPEN)

Do not start org-wide rollout in Phase 0 beyond control-function awareness.
