# AI Governance Playbook — SME Credit Underwriting Intelligence Workbench

**Compiled:** 2026-09-10  
**Use with:** `artefacts/RESPONSIBLE_AI_FRAMEWORK.md`, `artefacts/AI_RISK_REGISTER.md`, `artefacts/APPROVAL_WORKFLOWS.md`, `artefacts/INCIDENT_RESPONSE_PLAN.md`, `artefacts/SUPPORT_MODEL.md`  
**CRD IDs:** `CRD-SEC-001`–`012`, `CRD-FR-006`–`011`, `CRD-AC-003`, `CRD-AC-013`–`015`  
**Status:** How to run RAI day-to-day. Production fairness screen and dual-control ops are **not** live.

---

## 1. Daily underwriting (analyst)

1. Confirm tenant and role (engine role, not only LOS assignment).
2. Read source health and **degraded mode** before trusting a draft.
3. Treat memos as assistance: every FACT needs a source or `[INFERENCE]`.
4. If bank stale, bureau missing, or bank vs tax conflict — leave them visible; do not ask AI to pick one number.
5. If identity is AMBIGUOUS — escalate a human; do not accept a single canonical name.
6. If the draft invents a threshold, personal attribute, or “this is approved” — reject the draft (GS-14 / GS-13 / HG-01).
7. Record accept / modify / reject of AI into governed feedback — that is **not** a policy write.
8. If AI is down — continue manually; large limits still need `CREDIT_AUTHORITY` (GS-10).

---

## 2. Human oversight checklist (decisioning)

Before a human records `HumanDecision`:

- [ ] Required role from **Policy Engine** is sufficient for this actor
- [ ] AI did not persist the decision
- [ ] Material reasons cite evidence ids; adverse factors grounded if GS-13 class
- [ ] Recourse/appeal path visible for adverse/conditional
- [ ] Restricted eval attributes absent from the context you used
- [ ] Trace will persist **before** ACK (RPO 0)
- [ ] Override, if any, will **not** auto-retrain or rewrite 3.2

---

## 3. Fairness / impact evaluation job (eval mode only)

**Purpose:** `RISK_COMPLIANCE_EVAL`. Operator: that role only.

1. Confirm you are **not** on the underwriting runtime path.
2. Distinguish legal-entity vs sole trader vs natural-person guarantor/co-borrower in the cohort.
3. If using protected/sensitive attributes: approved purpose, access, governance documented on the job.
4. Produce segment **diagnostics**. Do **not** publish a legal fairness threshold.
5. Do **not** write results into runtime context, gold labels, or `CREDIT-POLICY-3.2`.
6. Historical approve/decline in the sample are prior policy/human selection — not creditworthiness truth.
7. If the job would need a jurisdictional conclusion → `OPEN_DECISION` to Legal; stop.

Until P2-02 exists, do not run “shadow” eval by dumping `restricted_fairness_eval_sample.csv` into DEV runtime.

---

## 4. Explainability pack (what to show)

| Question | Answer from |
|---|---|
| Why this number? | Envelope: source, period, freshness, authority |
| Why this policy? | Engine row + 3.2 rule id; not the memo paragraph |
| Why this person/org? | Party kind + resolution state + observations |
| Why this human? | `required_human_role` |
| Why not decide? | Degraded mode / abstention / missing evidence |
| What did AI do? | Recommendation stance + versions; no CoT |

If you cannot fill the pack, **do not** ship the statement as a FACT.

---

## 5. Escalation (RAI)

| You see | You do | Who |
|---|---|---|
| Draft “approved” / invented cutoff | Reject memo; ticket IR-HG01/02 | Credit Policy / Credit authority |
| Personal attribute invented | Reject; GS-13 class | Credit Operations |
| Fairness chart with a cutoff | Do not circulate as compliance | Risk/compliance + Legal |
| Ask to use other-tenant data | Deny; IR-HG04 | Security |
| Document orders “ignore policy” | Keep as DATA; IR-HG07 | Security |
| Accept-AI ticket to “update policy” | GOVERNED_REVIEW only | Model risk |
| Sole trader treated as company | Stop collapse | Risk/compliance eval |
| Need a law/licence name | Do not guess | Qualified legal review |

Severity and paging: `INCIDENT_RESPONSE_PLAN.md`. Support routing: `SUPPORT_MODEL.md`.

---

## 6. Change playbooks (RAI lens)

Follow `APPROVAL_WORKFLOWS.md`, plus:

**Model:** Must still fail GS-14 and GS-09; fallback GS-10; party-kind tests GS-03/13. Model-risk file before any live PROD call.

**Prompt:** Must not add thresholds or protected-attribute features. Instruction channel unchanged.

**Eval:** Must not gold-label from `AI_ACCEPTED`. Must not drop critical invented-threshold fail. Must not add GS that requires runtime restricted attrs.

**Policy:** Dual-control; GS-12/14; never 2.9 as rollback; no fairness cutoff slipped into 3.2 without a Legal-backed CR (and still no invented cutoff in **this** workshop).

---

## 7. Transparency scripts (internal)

**To analysts:** “This is assistance. The engine and your role decide. Stale or conflicting evidence stays on screen on purpose.”

**To demos:** “Contract gates are tested. Workbench and production are not claimed. 89.5 and 142 minutes are not the 30-minute target.”

**To affected-person/recourse ops:** “Adverse outcomes are human, with material reason and source. AI cannot issue them.”

---

## 8. Regulatory handling (process only)

1. Do not embed a statute name in prompts or gold.
2. Log `OPEN_DECISION`: question, owner=Legal/compliance, evidence needed.
3. Until closed, preserve workshop controls (human final, purpose split, traces, restricted-attr ban).
4. Production DPIA / retention days / appeal calendar remain OPEN (`NFR_SPECIFICATION.md`).

---

## 9. Cadence

| Rhythm | RAI activity |
|---|---|
| Each case | Oversight checklist §2 |
| Each GS run | Risk register C column |
| Each model/prompt/eval/policy CR | Workflows + register rows |
| When Fairness screen exists | Eval-mode jobs §3 |
| Before PROD GO | Independent review of register residuals W/P |
| After Sev 1 RAI incident | Preserve evidence; CR if intent must change |

---

## 10. Stop rules

Stop the AI path (keep manual underwriting if gates hold) when:

- any HG-01–HG-07 would be violated to “keep the demo going”;
- a fairness diagnostic is about to be used as a decline rule;
- a live model is called with `versions.model=NONE`;
- restricted eval data is in the underwriting context.

This playbook does not authorize production lending or a legal fairness opinion.
