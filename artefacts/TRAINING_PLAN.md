# Training Plan — SME Credit Underwriting Intelligence Workbench

**Compiled:** 2026-09-10  
**Companions:** `artefacts/CHANGE_MANAGEMENT_PLAN.md`, `artefacts/ADOPTION_STRATEGY.md`, `artefacts/AI_GOVERNANCE_PLAYBOOK.md`, `google_ai_build/03_APP_SCREEN_REQUIREMENTS.md`  
**CRD IDs:** `CRD-AC-001`–`015`, HG-01–HG-08, `CRD-SEC-001`–`012`  
**Status:** Curricula and onboarding. **Hands-on labs require the workbench (G-UI-01).** Until then, only control-function briefings and contract walkthroughs.

Training lead is **named at UAT**; until then Credit Operations owns content with Engineering/Policy/Model risk as instructors.

---

## 1. Learning objectives (all credit roles)

After training, a participant can:

1. State that AI assistance is not a credit decision and `PASS` ≠ `APPROVE`.
2. Name ACTIVE policy `CREDIT-POLICY-3.2` and that v2.9 must not control.
3. Use engine `required_human_role`, not LOS assignment, for gates.
4. Keep bank inflow, tax turnover, and statement revenue distinct.
5. Leave stale, missing, and conflicting evidence visible.
6. Refuse document instructions and cross-tenant access.
7. Continue manually when AI is down without inventing a memo.
8. Send AI feedback to governed review, not to the catalog.
9. Label TAT populations (142 / 89.5 / golden 15 / <30 target).

Authority roles add: GS-02 / GS-07 / GS-13 actions. Eval role adds: purpose split and no legal cutoff.

---

## 2. Programme structure

| Module | Length (PROPOSED) | Audience | Mode |
|---|---|---|---|
| M0 Architecture first | 45 min | All stakeholders | Briefing (can run in Phase 0) |
| M1 Workbench tour | 60 min | Users of 12 screens | UAT demo — **blocked** |
| M2 Evidence and semantics | 60 min | Analysts, UW, authority | Lab L001/L005/L011 |
| M3 Policy and authority | 60 min | Analysts+ | Lab L002/L007/L012/L014 |
| M4 People, fairness, adverse | 60 min | Analysts+, eval | Lab L003/L013; eval clinic |
| M5 Failure Lab (mandatory) | 90 min | Anyone with memo or decision access | L008/L009/L010/L006/L004/L015 |
| M6 Human Decision and traces | 45 min | Analysts, UW, authority | Lab + AT-16 pack |
| M7 Support and IR | 30 min | L1/L2, Ops | Table-top |
| M8 Fairness eval mode | 45 min | `RISK_COMPLIANCE_EVAL` only | Separate purpose |

Proposed lengths are **not** case SLAs. Completion = assessment pass, not seat time.

---

## 3. Module outlines

### M0 — Architecture first (Phase 0 OK)

- Nine sources and who is authoritative.
- Storyline: data → meaning → graph → retrieval → context → gated AI → human → trace → governed feedback.
- Hard gates HG-01–HG-08 in plain language.
- Demo honesty script for execs.

### M1 — Workbench tour

Screens in order: Control Tower → Application Context → Evidence Reconciliation → Graph Explorer → Hybrid Retrieval (five families labelled) → Policy & Authority → Memo → Human Decision → Trace → (eval mode separate) → Outcome & Feedback → Failure Simulation.  
**Rule taught:** screens display gates; they are not the control plane.

### M2 — Evidence and semantics

- SC pairs: no generic revenue; OCR ≠ creditworthiness.
- L005 stale bank; L011 unblended conflict; L001 grounded memo (HG-03).

### M3 — Policy and authority

- 3.2 vs 2.9 (L012).
- Invented INR 2,500,000 is **not** policy (L014) — critical fail.
- L002 engine `CREDIT_AUTHORITY` vs LOS senior.
- L007 `SENIOR_UNDERWRITER` exception ≠ L006 missing bureau.

### M4 — People, fairness, adverse

- L003 business ≠ owner; restricted attrs out.
- L013 guarantor ≠ entity; AI cannot decline; reason on `EXP-013`.
- Segment diagnostics ≠ legal threshold.

### M5 — Failure Lab (gate to memo access)

| Lab case | Must demonstrate |
|---|---|
| L008 | Zero other-tenant content; DENY is correct |
| L009 | Injection remains DATA; policy unchanged |
| L010 | Manual path; no fake AI memo; limit still needs authority |
| L006 | Null bureau; no invented score |
| L004 | AMBIGUOUS; no silent merge |
| L015 | Accept AI → governed review; catalog hash unchanged |

Fail any row → no production or UAT memo privilege.

### M6 — Human Decision and traces

- Sufficiency table; forbidden AI actions.
- Trace pack: evidence, policy, retrieval, versions, rationale, human action; no CoT.
- ACK only after persist.

### M7 — Support and IR

- How-to vs Sev 1 (isolation, injection, invented policy, AI-final).
- Never fail-open; never v2.9.

### M8 — Eval mode

- Purpose `RISK_COMPLIANCE_EVAL`.
- Distinguishing SME / sole trader / guarantor.
- Historical labels ≠ gold.
- Escalate jurisdiction to Legal (`OPEN_DECISION`).

---

## 4. Onboarding path by persona

| Persona | Required modules | First supervised cases | Access granted after |
|---|---|---|---|
| `RELATIONSHIP_MANAGER` | M0, M1 (Control Tower only) | Assigned-app status | M0 |
| `CREDIT_ANALYST` | M0–M6 | L001, L005, L011 then L014 | M5 pass |
| `SENIOR_UNDERWRITER` | M0–M7 | + L006/L007 | M5 + M3 pass |
| `CREDIT_AUTHORITY` | M0–M7 | + L002, L013 | M5 + M3/M4 pass |
| `RISK_COMPLIANCE_EVAL` | M0, M4, M8 | Eval job dry-run — **not** underwriting | M8; no runtime decision |
| L1 support | M0–M2, M5, M7 | Ticket shadow | M5 pass |
| Engineering / Ops | M0, M5, M7 + runbooks | GS suite in TEST | Role-based IAM |
| Exec / sponsor | M0 only | — | n/a |

Identity adjudication (L004) is in M5 for all decisioning roles; no new job title.

---

## 5. Assessment

| Check | Pass |
|---|---|
| Knowledge | Short items: PASS≠APPROVE; 3.2 ACTIVE; three TAT populations; L006≠L007 |
| Lab | Instructor sign-off on Failure Lab table |
| Safety | Zero attempts to bypass tenant/injection in lab (attempt + **correct** DENY is pass; **success** at bypass is fail) |
| Authority | L002/L007/L013: correct required role; AI DENY |

Records: trainee, role, date, assessor, GS ids. Do not store hidden CoT “explanations” of the trainee.

---

## 6. Instructors and materials

| Topic | Instructor |
|---|---|
| Gates, GS labs | Engineering + Model risk |
| Policy 3.2 / exceptions | Credit Policy |
| Authority / adverse | Credit authority |
| Fairness eval | Risk / compliance eval |
| Recourse | Credit Operations (+ Legal if OPEN items) |
| Isolation / injection | Security |

Materials: this plan, `AI_GOVERNANCE_PLAYBOOK.md`, golden `live_applications.csv`, Failure Simulation screen (when built), role matrix. **Do not** train on live PROD PII in UAT labs.

---

## 7. Sustainment

| Trigger | Retrain |
|---|---|
| New model/prompt/policy CR | Delta: GS-09/14/12 as applicable |
| Sev 1 involving user behaviour | Targeted lab |
| Role change (e.g. analyst → senior) | M3/M7 gap |
| 12 months or first PROD GO | M5 refresh |

---

## 8. Training vs rollout

| If | Then |
|---|---|
| Screens not built | Deliver M0 + table-top M5 only; **no** usage KPI |
| UAT open | Full path for **named** cohort |
| PROD GO | All PROD users M5-current; hypercare per Adoption strategy |

Success of training is Failure Lab pass rate and **zero** HG regressions from trained users — not course completion percentage alone.

---

## 9. Readiness (2026-09-10)

- [x] Curricula mapped to GS-01–GS-15 and personas  
- [ ] Named training lead  
- [ ] Workbench labs (blocked on G-UI-01)  
- [ ] UAT cohort list and IAM groups  
- [ ] Assessment records store  

Do not certify users for production lending on Phase 0 briefings.
