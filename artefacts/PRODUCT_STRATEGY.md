# Product Strategy — SME Credit Underwriting Intelligence Workbench

**Organization:** NexLend SME Finance (fictional)  
**Product:** SME Credit Underwriting Intelligence Workbench  
**Compiled:** 2026-09-10 from approved specs, production-readiness review and 90-day roadmap  
**Companions:** `artefacts/PRD.md`, `artefacts/SUCCESS_METRICS.md`  
**This artefact does not authorize production lending use and does not mark any `CRD-FR-*` row `VERIFIED`.**

**CRD IDs:** `CRD-BR-001`–`004`, `CRD-FR-001`–`011`, `CRD-SEC-001`–`012`, `CRD-NFR-001`–`007`.

---

## 1. Product vision

NexLend’s underwriting estate is fragmented across nine brownfield systems. The organization is under pressure to “add AI” and cut turnaround. The strategy is to **build architecture first**: a semantically consistent, policy-aware, provenance-bearing context for human underwriters, with reconstructable proof of what produced each outcome.

> The LLM is not the architecture.

AI is an analysis and recommendation component. Underwriters and designated credit-authority roles, plus deterministic validated controls, remain the domain authority for final credit, adverse/exception route and recourse (`CRD-FR-011`).

**North-star question:** Can NexLend construct trustworthy context for an underwriter — and prove evidence, policy version, tools and human authority for each outcome?

---

## 2. Business objectives

| Priority | Objective | ID | Constraint |
|---|---|---|---|
| 1 | Hard-control integrity | `CRD-BR-003`, `CRD-SEC-*`, HG-01–HG-08 | Faster TAT is failure if policy, privacy, fairness, evidence or authority degrades |
| 2 | Trustworthy context | `CRD-BR-002` | No fabricated certainty; conflicts stay visible |
| 3 | Reconstructability | `CRD-BR-004` | Observable traces, not hidden CoT |
| 4 | Uncomplicated TAT <30 minutes | `CRD-BR-001` / QT-05 | Only after hard gates; only on a named production population |

Source-case baseline (142-minute median, 648 P90, 31.2% document rework, 57% >3 lookups, 38-minute median memo, 8.4% exceptions, 13.7% missing source refs) describes the **operating problem**. It is not a product KPI already achieved.

---

## 3. Customer value proposition

| Audience | Job to be done | Value if hard gates hold | What we refuse to sell |
|---|---|---|---|
| Credit analyst | Reconcile heterogeneous evidence and draft a memo | Provenance-bearing context; grounded draft; conflicts/stale/missing visible | A chatbot that “just approves” |
| Senior underwriter | Distinguish missing data from true policy exceptions | Engine route + required role preserved | Collapsing L006 and L007 into one queue |
| Credit authority | Authorize large limits and adverse/recourse | Engine role, not LOS assignment; AI cannot bypass | Delegated AI credit |
| Risk / compliance | Evaluate impact without poisoning runtime | Separate `RISK_COMPLIANCE_EVAL` purpose | Restricted attributes as decision features |
| Audit / model risk | Reconstruct a recommendation | Trace of evidence, retrievals, policy version, human action | Chain-of-thought as audit evidence |
| Applicant / affected person | Recourse when adverse or conditional | Human authority + material reason + approved appeal path | AI-issued decline |

**Differentiation:** five retrieval families with tenant/purpose/freshness filters before the model; policy version as authority; identity ambiguity preserved; learning loop that cannot silently rewrite policy.

---

## 4. User personas

From `evidence/04_policy_authority/role_authorization_matrix.csv`. No extra persona is granted lending power.

### 4.1 Relationship manager (`RELATIONSHIP_MANAGER`)

Sees assigned applications; limited AI assist. Cannot prepare memos, record recommendations, take final credit action, or override policy. Value: status and source-health visibility without leaking other-tenant or restricted-eval data.

### 4.2 Credit analyst (`CREDIT_ANALYST`)

Primary daily user of Control Tower, Application Context, Evidence Reconciliation, memo draft and refer. Final credit only when the **engine** allows. Needs identity ambiguity, bank/tax non-collapse, and stale flags in the same view they draft from.

### 4.3 Senior underwriter (`SENIOR_UNDERWRITER`)

Exception and within-authority decisions. SME-L007 true policy exception routes here. Policy override only through a documented authorized process — never via generated text.

### 4.4 Credit authority (`CREDIT_AUTHORITY`)

Large-limit (INR > 5,000,000 / `AUTH-LIMIT-01`) and adverse/recourse (SME-L013 / `AUTH-ADVERSE-01`). Engine required role beats LOS assignment (SME-L002). AI `AUTHORIZE_LARGE_LIMIT` / `ISSUE_ADVERSE` = DENY.

### 4.5 Risk / compliance evaluator (`RISK_COMPLIANCE_EVAL`)

Fairness/Impact Evaluation screen only, approved purpose, de-identified or approved cohort diagnostics. No runtime decision path. Must not invent a legal fairness threshold.

### 4.6 AI agent (system actor, `AI_AGENT`)

Tool-scoped retrieve, summarize, draft, refer. Advisory only. Not a human persona and not a credit officer.

**Not in the authorization matrix:** `PORTFOLIO_ANALYST` (SME-L015 assigned label) is not an extra authority. Identity **adjudicator** is required by design (`CRD-AC-004`) but is not a new role invented here — escalate using existing human authority until a change request names an adjudicator.

**Affected persons:** legal entities, sole-trader businesses, natural-person owners and guarantors. Strategy: analyze purpose, actor and affected-person context; do not apply a sector-wide regulatory label in this artefact.

---

## 5. Strategic principles (non-negotiable)

From `architecture/Decision_Guardrails.md`:

1. AI has no autonomous final credit authority.
2. Active credit policy is deterministic and versioned; generation cannot modify it.
3. Material AI-assisted factors require evidence and provenance.
4. Tenant isolation runs before retrieval and display.
5. Restricted evaluation attributes do not enter runtime decision context by default.
6. Stale, missing and conflicting evidence remains visible.
7. Untrusted uploaded or retrieved text cannot override instructions or policy.
8. Sole-trader and natural-person-guarantor cases need explicit affected-person analysis.
9. Adverse and exception routes preserve human authority, material-reason evidence and recourse.
10. Manual underwriting remains available during AI outage.
11. Traces record evidence, context, tools, policy checks, versions, concise rationale and human action — not hidden CoT.
12. Feedback cannot silently rewrite policy, ontology, semantic definitions or model configuration.

**Success model:** hard gates first; business value second.

---

## 6. Release scope

Three promotion paths (`RELEASE_GATES.md`). Documentation alone does not close a gate.

### 6.1 Workshop demonstration (contracts only) — CONDITIONAL GO

**In scope now:** deterministic adapters in `src/credit_domain`; GS-01–GS-15 unittest evidence under `evidence/sdd/`; HG-01–HG-08 at contract layer.

**Operator caveats (mandatory):** this is assistance, not a credit decision; workbench screens are not implemented; TAT figures are not the 30-minute target; `CREDIT-POLICY-3.2` is the only active workshop policy.

### 6.2 Workbench beta (internal) — BLOCKED (G-UI-01)

**In scope when unblocked:** the twelve screens displaying P0/P1 state; GS-01–GS-15 on the path a user sees; Human Decision, Decision Trace and Outcome & Feedback **before** any user-visible memo.

**Not in this beta:** production adapters, TAT claims, fairness legal opinions, live LLM without gates.

### 6.3 Production release — BLOCKED

Required: hard gates re-run on workbench path; G-FB-01–03 green; G-RB-01 rollback drill; human override drilled (GS-10 + GS-02 + GS-13); named production adapters; human sign-off of high-impact controls; QT-05 if reported cites a production population distinct from 142 and 89.5.

Superseded `CREDIT-POLICY-2.9` is **never** a production rollback controller.

---

## 7. Out-of-scope capabilities

Do not plan, demo or measure these as product features:

- Autonomous AI final credit, adverse, exception or recourse.
- Extra credit thresholds beyond INR 5,000,000 and 7-day bank freshness in `CREDIT-POLICY-3.2`.
- Invented legal/fairness classifications or jurisdiction conclusions.
- Equating workshop TAT 89.5 or source TAT 142 with `CRD-BR-001`.
- Replacing LOS / bureau / bank / tax / exposure / policy systems with generated data.
- Treating `AI_ACCEPTED` or later portfolio outcome as gold or policy.
- Restricted fairness sample as a runtime decision feature.
- Using v2.9 as rollback.
- Marking `CRD-FR-*` **VERIFIED** from strategy documents.

Unresolved legal conclusions stay with qualified legal/compliance review (`OPEN_DECISION`).

---

## 8. Risks and assumptions

### Assumptions

| Assumption | Basis | If false |
|---|---|---|
| Workshop fixtures remain the verification corpus | `CRD-NFR-007` | Do not swap in live credit data to “make the demo pass” |
| Policy 3.2 stays the only ACTIVE workshop bundle | GS-12, HG-06 | Retrieval must still refuse v2.9 as controller |
| Contract gates stay in front of any future LLM | `CRD-FR-005` | Stop-ship; do not ship prompt-only controls |
| Human reviewers exist for authority changes | `DEFINITION_OF_DONE.md` | Do not self-approve high-impact control diffs |
| Specs change only via CR | `CHANGE_CONTROL.md` | Code must not redefine product intent |

### Product and delivery risks

| ID | Risk | Severity | Indicator | Response |
|---|---|---|---|---|
| R-01 | UI bypasses `check_access_and_authority` or tenant filters | Stop-ship | Checkpoint Q1 at day 30/60/90 | Screens display state; gates remain code |
| R-02 | Generated sentence treated as policy evidence | Stop-ship | GS-14 / AT-16 fail | Fidelity scan; explanation ≠ policy |
| R-03 | Feedback writes policy, prompts, models or gold | Stop-ship | G-FB-01 fail | `FEEDBACK-001` denylist |
| R-04 | Mixing TAT populations | Material | 89.5 or 142 reported as QT-05 | Label three populations |
| R-05 | Workbench never built; contracts over-claimed | Material | G-UI-01 still OPEN | Honest layering: contract ≠ workbench ≠ production |
| R-06 | Graph ADR / six traversals never accepted | Material | Template 06 blank | P2-06; simulate JSON but record ADR |
| R-07 | Live LLM without model-risk file | Production FAIL | `versions.model=NONE` then a hidden model | No production GO |
| R-08 | Rollback drill absent | Production FAIL | G-RB-01 OPEN | Days 61–90 design; never roll back to v2.9 |
| R-09 | Identity silent merge via `canonical_candidate` | Hard-gate adjacent | GS-04 fail | Keep AMBIGUOUS; hypothesis ≠ MATCHED |
| R-10 | Fairness eval mode used as runtime features | HG-05 | Restricted sample in context | Separate purpose only |

Checkpoint questions (`90_DAY_MODERNIZATION_ROADMAP.md`): yes to R-01–R-03 class failures is stop-ship. No to hard-gate re-run on UI or mislabelled TAT is not a production GO.

---

## 9. Future roadmap

Horizon copied from `90_DAY_MODERNIZATION_ROADMAP.md`. Do not reopen P0 authority decisions.

### Days 1–30 (2026-09-10 → 2026-10-09) — Workbench on existing gates

P2-01. Wire Control Tower, Application Context, Evidence Reconciliation, Context Graph Explorer, Hybrid Retrieval inspector, Policy & Authority, AI Analysis, Human Decision, Decision Trace, Failure Simulation to SME-L001–L015. Re-run HG-01–HG-08 on UI paths. Must not slip: GS-08, GS-14, GS-10.

### Days 31–60 (2026-10-10 → 2026-11-08) — Fairness, feedback, observability

P2-02, P2-03. Fairness/Impact Eval (`RISK_COMPLIANCE_EVAL` only); Outcome & Feedback on SME-L015; source-health observability; recourse / affected-person display for GS-03 and GS-13. Must not slip: G-FB-01; no invented legal fairness cutoff.

### Days 61–90 (2026-11-09 → 2026-12-08) — Production-shaped residuals, not a GO

P2-04 residual, P2-05, P2-06. Graph ADR vs six traversals; named production-adapter design; rollback drill that never applies v2.9; re-issue readiness pack; decide **workshop beta** vs **remain blocked**.

If TAT is measured, report workshop 89.5 and source 142 as **separate** figures. Do not claim `CRD-BR-001` / QT-05.

**Production GO in day 90 is not the default outcome.** It remains blocked until `RELEASE_GATES.md` section 5.3 is evidenced.

### Beyond 90 days (not scheduled here)

Only after workbench hard gates pass: production adapters, model-risk file for a real LLM, privacy DPIA / retention, durable audit store, on-call observability, dual-control policy-release pipeline. None of those are implied complete by this strategy.
