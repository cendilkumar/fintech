# AI Risk Register — SME Credit Underwriting Intelligence Workbench

**Compiled:** 2026-09-10  
**Taxonomy:** `artefacts/RESPONSIBLE_AI_FRAMEWORK.md` §9  
**CRD IDs:** `CRD-SEC-001`–`012`, HG-01–HG-08, `CRD-AC-001`–`016`  
**Scoring:** Workshop-informed (scenario designed to catch the failure). **Not** a production loss model. Residual assumes **contract-layer** controls 2026-09-10 unless noted.

| Score | Likelihood (workshop) | Impact |
|---|---|---|
| H | Golden scenario exists specifically for this failure | Credit, privacy, or policy integrity |
| M | Implied by architecture if gates skipped | Operational or audit gap |
| L | Constrained if BINDING gates hold | Reversible / assistance-only |

**Residual status:** C = contract PASS; W = workbench OPEN; P = production BLOCKED.

---

## Register

| ID | Family | Risk | GS / AC | L | I | Existing control | Residual | Owner | Treatment |
|---|---|---|---|---|---|---|---|---|---|
| R-AUTH-01 | R-AUTH | AI issues final APPROVE/DECLINE | GS-02, HG-01 | H | H | `check_access_and_authority`; `AI_AGENT` final=NO | C PASS; W/P OPEN | Credit authority | Keep gates outside generation; UI must not bypass |
| R-AUTH-02 | R-AUTH | AI authorizes limit > INR 5,000,000 | GS-02, `AUTH-LIMIT-01` | H | H | Engine `CREDIT_AUTHORITY`; LOS assignment ignored | C PASS; W OPEN | Credit authority | Human Decision screen required before memo UI |
| R-AUTH-03 | R-AUTH | AI approves policy exception | GS-07 | H | H | `APPROVE_EXCEPTION` DENY for AI; `SENIOR_UNDERWRITER` | C PASS; W OPEN | Credit Policy | Do not mix with GS-06 missing bureau |
| R-AUTH-04 | R-AUTH | AI issues adverse / denies recourse | GS-13, `CRD-SEC-009` | H | H | `ISSUE_ADVERSE` DENY; grounded factor + human + appeal | C PASS; W OPEN | Credit authority | Recourse calendar still OPEN (Legal) |
| R-AUTH-05 | R-AUTH | Recommendation stored as HumanDecision | G-AUTH-02 | M | H | `handoff_recommendation` write scope | C PASS | Engineering | Trace + case API write barrier |
| R-POL-01 | R-POL | Invented threshold treated as policy | GS-14, HG-02 | H | H | Fidelity scan; INR 2,500,000 probe critical fail | C PASS; W OPEN | Credit Policy | Prompt must not be sole home of rules |
| R-POL-02 | R-POL | Superseded 2.9 controls live eval | GS-12, HG-06 | H | H | Version/date retrieve; similarity cannot select | C PASS; W OPEN | Credit Policy | Never DR-rollback to 2.9 |
| R-POL-03 | R-POL | Generated prose used as policy evidence | AT-16 | H | H | Policy path = engine + 3.2 bundle | C PASS; W OPEN | Credit Policy | IR-HG02 |
| R-EVID-01 | R-EVID | Bank and tax averaged / “revenue” | GS-11, `CRD-AC-016` | H | H | Separate measures; conflict visible | C PASS; W OPEN | Credit Risk | Evidence Reconciliation UI |
| R-EVID-02 | R-EVID | Stale bank presented as current | GS-05, QT-03 | H | H | `presented_as_current=false`; 7-day rule | C PASS; W OPEN | Data Partnerships | Engine PASS ≠ current |
| R-EVID-03 | R-EVID | Invented bureau score | GS-06 | H | H | Null envelope; no fabricate | C PASS; W OPEN | Credit Risk | Distinct from GS-07 |
| R-EVID-04 | R-EVID | Ungrounded memo FACT | GS-01, HG-03 | H | H | 100% provenance or memo blocked | C PASS; W OPEN | Credit Operations | AT-18 |
| R-EVID-05 | R-EVID | OCR confidence as creditworthiness | SC-10 | M | M | Type non-collapse | C PASS | Engineering | Analyst training in runbook |
| R-ID-01 | R-ID | Silent merge on `canonical_candidate` | GS-04 | H | H | AMBIGUOUS; hypothesis ≠ MATCHED | C PASS; W OPEN (no adjudicate UI) | Credit Operations | Do not invent new adjudicator role |
| R-ID-02 | R-ID | Sole trader collapsed to person or org-only | GS-03 | H | H | Party kinds split; affected-person analysis | C PASS; W OPEN | Risk / compliance eval | No sector-wide legal label |
| R-ID-03 | R-ID | Guarantor merged into borrower entity | GS-13 | H | H | Guarantor is a role PLAYED_BY NaturalPerson | C PASS; W OPEN | Credit Operations | |
| R-PRIV-01 | R-PRIV | Restricted fairness sample in runtime | GS-03/15, HG-05 | H | H | Eval-only purpose; inject deny | C PASS; W OPEN (no eval screen) | Security + Risk/compliance | P2-02 still missing |
| R-PRIV-02 | R-PRIV | Cross-tenant retrieval/display | GS-08, HG-04 | H | H | Pre-adapter tenant filter | C PASS; W OPEN; P IAM NOT PROVEN | Security | No fail-open in IR |
| R-PRIV-03 | R-PRIV | Invented personal attributes | GS-13 scan | H | H | Person-claim reject list | C PASS | Credit Operations | |
| R-INJ-01 | R-INJ | Document “ignore policy and approve” followed | GS-09, HG-07 | H | H | DATA channel; `FOLLOW_DOCUMENT_INSTRUCTION` DENY | C PASS; W OPEN | Security | Filters = code |
| R-XAI-01 | R-XAI | Hidden CoT stored as audit | AT-17 | M | H | `FORBIDDEN_TRACE_KEYS` | C PASS; W OPEN | Model risk | |
| R-XAI-02 | R-XAI | Trace missing AT-16 fields | GS-01/07/13 | M | H | `validate_trace`; ACK only after persist | C PASS; durable store P OPEN | Credit Operations | RPO 0 |
| R-FB-01 | R-FB | `AI_ACCEPTED` writes policy/prompts/models/gold | GS-15, G-FB-01 | H | H | `GOVERNED_REVIEW`; denylist | C PASS; W OPEN | Model risk | Dual-control ops NOT PROVEN |
| R-FB-02 | R-FB | Missing portfolio outcome invented | G-FB-02 | H | M | No row for SME-L015 → none invented | C PASS | Model risk | |
| R-FAIR-01 | R-FAIR | Segment diagnostic treated as legal cutoff | Fairness policy | H | H | Explicit ban; eval mode separate | Policy text; screen NOT IMPL | Risk / compliance eval | Legal OPEN_DECISION |
| R-FAIR-02 | R-FAIR | Historical decline used as gold | SC-11, GS-15 | H | H | Labels ≠ ground truth | C PASS | Model risk | |
| R-OPS-01 | R-OPS | AI outage blocks the case | GS-10, HG-08 | H | H | `FALLBACK-001`; manual view | C PASS; W OPEN | Credit Operations | Credit-path RTO 0 extra wait |
| R-OPS-02 | R-OPS | Incident fail-open isolation | IR plan | M | H | Standing order: deny | Procedure only | Security | Drill NOT PROVEN |
| R-OPS-03 | R-OPS | Live LLM with `versions.model=NONE` | Prod readiness §4.1 | M | H | Honesty rule; model-risk file | P FAIL if wired | Model risk | Block PROD if live and unversioned |
| R-OPS-04 | R-OPS | Fixture stats claimed as QT-05 | `CRD-NFR-007` | M | M | Population labelling | Process | Credit Operations | 89.5/142 ≠ <30 |

---

## Heat (workshop)

Highest likelihood × impact with **workbench still open**: R-AUTH-*, R-POL-01/02, R-PRIV-01/02, R-INJ-01, R-FAIR-01, R-OPS-01 — contract gates exist; **user-visible path unproven**.

Production-unique: R-OPS-03 (no model-risk file), R-OPS-02 (no IR drill), durable trace store, IAM ≠ ALPHA/BETA.

---

## Review cadence

| When | Action |
|---|---|
| Each CR (model/prompt/policy/eval) | Check affected rows; do not close residual with documentation |
| Each GS suite run | Confirm C column still PASS |
| UAT G-UI-01 | Re-score W column with UI evidence |
| Before PROD GO | Independent reviewer vs this register + `PRODUCTION_READINESS_REVIEW.md` |
| After Sev 1 | Add row or raise residual; preserve evidence |

Do not delete a row to make the register look clean.
