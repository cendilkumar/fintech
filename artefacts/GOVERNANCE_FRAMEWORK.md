# Governance Framework — SME Credit Underwriting Intelligence Workbench

**Compiled:** 2026-09-10  
**CRD IDs:** `CRD-FR-005`, `CRD-FR-007`, `CRD-FR-010`, `CRD-FR-011`, `CRD-SEC-001`–`002`, `CRD-SEC-011`–`012`, `CRD-NFR-007`, `FEEDBACK-001`, HG-01–HG-08, G-POL-*, G-FB-*, G-AUTH-*  
**Companions:** `CHANGE_CONTROL.md`, `DEFINITION_OF_READY.md`, `DEFINITION_OF_DONE.md`, `RELEASE_GATES.md`, `artefacts/CHANGE_CONTROL_PROCESS.md`, `artefacts/APPROVAL_WORKFLOWS.md`  
**Status:** Target governance. Does **not** replace `CHANGE_CONTROL.md` or approved specs. Does **not** mark `CRD-FR-*` `VERIFIED`. Does **not** authorize production lending.

**Principle:** Code does not redefine product intent. Generation does not redefine policy. `AI_ACCEPTED` is not a change-control vote.

---

## 1. What is governed

| Domain | Authority object | Must not be changed by |
|---|---|---|
| **Requirements** | Approved `CRD-*` specs + acceptance + traceability | Implementation convenience, demo narrative, generated text |
| **Policies** | ACTIVE `CREDIT-POLICY-3.2` + Policy Engine results | Similarity retrieval, memos, `AI_ACCEPTED`, v2.9 |
| **Models** | Versioned model id in traces (`versions.model`) | Silent swap; treating `NONE` as a live model |
| **Prompts** | Versioned prompt id (`versions.prompt`); system/policy channel | Applicant documents, historical memos, operator chat as instructions |
| **Evaluations** | Golden scenarios, HG/QT, gold labels, eval suite | Ungoverned feedback, invented GS-16, weakening `hard_fail_if` to pass |
| **Production releases** | Signed build SHA + catalog hash + eval report | Fixture-as-live-data; UI that bypasses gates |

Ontology, semantic definitions, KG schema and retrieval policy are **policy-adjacent catalogs**. They follow the same “specs first, dual control, no silent feedback write” rule (`CRD-SEC-012`).

---

## 2. Decision rights

No extra lending role is created. Approvers match `RELEASE_GATES.md` §6 and the role matrix.

| Decision | Accountable approver | Must consult | Veto |
|---|---|---|---|
| Requirement / AC / FR text | Spec owner + workshop/team human approval (`CHANGE_CONTROL.md`) | Credit Operations | Independent reviewer if guardrails move |
| ACTIVE credit policy | Credit Policy (**dual-control**) | Credit authority for AUTH-* routes | Credit authority if HG-01/limit routes change |
| Policy Engine thresholds | Credit Policy only; known literals remain INR 5,000,000 and 7-day bank freshness unless a CR says otherwise | — | Do not invent extra cut-offs in ops |
| Model promotion | Model risk / evals | Engineering; Credit Policy if outputs touch thresholds | HG-02/07/09 fail = veto |
| Prompt promotion | Model risk / evals | Security (instruction channel); Credit Policy | Documents must stay DATA |
| Gold labels / eval suite | Model risk / evals | Spec owner for AC mapping | Invented threshold not critical = veto |
| Fairness eval jobs | Risk / compliance eval | Security (purpose) | Runtime injection of restricted attrs |
| Production release | Independent reviewer **after** §5.3 | All sign-off families | Any HG fail on workbench path |
| High-impact authority/control change | Named human reviewer (`DEFINITION_OF_DONE.md`) | Engineering | Shipping without that review |

**Explicitly not approvers:** `AI_AGENT`, vector similarity, Relationship Manager, `PORTFOLIO_ANALYST` (fixture label), applicant-document text.

Legal / jurisdiction conclusions remain `OPEN_DECISION` for qualified legal/compliance review — not a PRD or model vote.

---

## 3. Governance by domain

### 3.1 Requirements

- Intake via change request `CRD-CR-YYYY-NNN`.
- Affected IDs, ACs, golden scenarios, contracts and guardrails listed before code.
- Specs updated **first**; then tasks; then implementation (`00-sdd-core`).
- Traceability stays honest: `OPEN` / `IN_PROGRESS` / `VERIFIED` / `BLOCKED`. Docs alone do not `VERIFIED`.
- Preserve prior evidence; do not overwrite inconvenient results.

### 3.2 Policies

- ACTIVE bundle is versioned and deterministic (`CRD-SEC-002`).
- Retrieval by version/status/as-of date (`CRD-TOOL-004`); similarity cannot choose authority.
- Generated explanation is not policy evidence (AT-16).
- Dual-control catalog edits; previous ACTIVE restore **never** uses v2.9 (G-RB-01).
- Formal exception process only for human policy override (role matrix).

### 3.3 Models

- A live model MUST have a version, owner, eval report and gates **outside** generation.
- `versions.model=NONE` is honest only when no live model is called.
- Model risk file is a production blocker if an LLM is wired (`PRODUCTION_READINESS_REVIEW.md` §4.1).
- Outputs remain `Recommendation`; they cannot persist `HumanDecision`.

### 3.4 Prompts

- System/policy/access prompts are controlled artifacts with versions in the trace.
- Untrusted documents and memos never enter the instruction channel (`DATA-DOC-INSTRUCTION`).
- Prompt change cannot widen tenant scope or grant `AI_AGENT` final credit.

### 3.5 Evaluations

- GS-01–GS-15 / `CRD-AC-001`–`015` are normative. `CRD-AC-016` is a model contract, not a 16th GS.
- Invented thresholds are a **critical** fail (HG-02).
- QT-01 cannot be claimed unless hard-gate scenarios pass; layer must be named (contract / workbench / production).
- Gold labels and `expected_behaviors.json` are write-protected from the feedback path.

### 3.6 Production releases

- Promotion: DEV → TEST → UAT → PROD per `ENVIRONMENT_STRATEGY.md`.
- §5.1 workshop demo ≠ §5.2 workbench beta ≠ §5.3 production.
- Fixtures are not live credit data (`CRD-NFR-007`).
- Sign-off table must be actually signed; this framework is not a signature.

---

## 4. Feedback is not governance

| Event | Enters | Does not do |
|---|---|---|
| `AI_ACCEPTED` / `AI_MODIFIED` / `AI_REJECTED` | `GOVERNED_REVIEW` queue | Mutate 3.2, ontology, prompts, models, gold |
| `HumanDecision` | Case record | Catalog edit |
| Portfolio outcome | Outcome store; missing rows not invented | Gold or policy |
| Restricted fairness row | Eval-only purpose | Runtime context |

A governed review **may** open a `CRD-CR-*`. It **must not** auto-merge.

---

## 5. Segregation of duties

| Pair | Rule |
|---|---|
| Author vs approver of ACTIVE policy | Different humans (dual-control) |
| Model developer vs eval owner | Eval owner can veto promotion |
| Workbench implementer vs authority reviewer | High-impact gates need a human who is not only the implementer |
| Fairness eval operator vs underwriting runtime | Separate purpose and store |
| Independent production reviewer vs delivery team | `RELEASE_GATES.md` §6 last row |

---

## 6. Records

Every approved change SHALL leave: CR id, approver role+name, timestamp, before/after version hashes, affected `CRD-*` / GS ids, eval evidence path, decision to promote or not. Traces copy model/prompt/policy/ontology versions (`CRD-FR-009`). Hidden CoT is not a governance record (AT-17).

---

## 7. Exceptions

- **True policy exception (GS-07 class):** human `SENIOR_UNDERWRITER` (or sufficient role) via engine route — not a CR to the catalog.
- **Formal policy override:** `CREDIT_AUTHORITY` documented process — still not a silent catalog write from AI.
- **Emergency production incident:** `INCIDENT_RESPONSE_PLAN.md` may freeze assistance; it may **not** skip dual-control to activate v2.9 or disable isolation.

Unresolved items stay `OPEN_DECISION` with owner and required evidence — no guessing in governance docs.
