# Executive Dashboard Spec — SME Credit Underwriting Intelligence Workbench

**Compiled:** 2026-09-10  
**CRD IDs:** `CRD-BR-001`–`004`, `CRD-NFR-006`, HG-01–HG-08, QT-05, G-UI-01  
**Companions:** `artefacts/VALUE_REALIZATION_FRAMEWORK.md`, `artefacts/BUSINESS_METRICS_CATALOG.md`, `artefacts/SUCCESS_METRICS.md`, `google_ai_build/03_APP_SCREEN_REQUIREMENTS.md`  
**Status:** Reporting specification for steerco and control-function packs **after go-live**. **Not built.** These views are **not** a 13th required underwriting screen and do **not** extend G-UI-01. Control Tower remains the operational queue (application, tenant, stage, source-health) — not this exec pack.

Production GO is **BLOCKED**. Until then, the only honest exec view is the **honesty strip** in §4.

---

## 1. Purpose and audiences

| Dashboard | Audience | Decision it supports | Cadence |
|---|---|---|---|
| **D1 Steerco one-pager** | Sponsors, independent reviewer, exec | Continue / pause value campaign; GO health | 30/60/90 then quarterly |
| **D2 Hard-control board** | Security, Model risk, Credit Policy | Stop-ship | Daily in hypercare; else weekly |
| **D3 Value & productivity** | Credit Operations, sponsors | SM-05/06/07 and SM-01 **with population label** | Weekly after day 31 |
| **D4 Adoption & engagement** | Credit Operations, training lead | Enablement vs shadow tools | Weekly in hypercare |
| **D5 Financial bridge** | Finance (when named), sponsors | Hours first; $ only if BM-F04 signed | Monthly after hours exist |

All five share one **honesty strip** (§4). If the strip is red, D3–D5 render **paused** — not green TAT.

---

## 2. Design rules

1. **Gates above value.** HG traffic lights occupy the first row of D1 and all of D2.
2. **Label every number** with population (source 142 / workshop 89.5 / golden 15 / named production book) and layer (contract / workbench / production).
3. **No other-tenant rows.** Aggregates are tenant-scoped or independently reviewed cross-tenant **counts of DENY**, never content.
4. **No restricted eval attributes** on D1–D5. Fairness diagnostics stay on the Fairness/Impact Evaluation screen (`RISK_COMPLIANCE_EVAL`).
5. **No hidden CoT.** Trace fields only: evidence, tools, policy version, rationale, human action.
6. **DENY is green** for isolation, injection, AI-final, catalog write.
7. **Screens display gates; they are not the control plane.** A dashboard tile cannot authorize credit, disable isolation, or activate v2.9.
8. **Do not chart 89.5 or 142 as the <30 SLO.** Those series may appear only as **labelled baselines**, visually distinct from the production series and from the 30-minute reference line.

Suggested visual encoding: production series = solid; source baseline = dashed labelled “source case 142”; workshop = dotted labelled “fixture 89.5 — not QT-05”; 30-minute target = reference line labelled “CRD-BR-001 target — not proven until named book.”

---

## 3. Data sources (when instrumented)

| Source | Used for | Must not used for |
|---|---|---|
| Decision traces | TAT clocks, HumanDecision, versions, provenance flags | Chain-of-thought |
| Policy engine | ACTIVE version, required role, PASS≠APPROVE | Generated text as policy |
| Access/authority checks | Isolation, role sufficiency | VIP override |
| Evidence envelopes | Freshness, conflict, source-ref | OCR confidence as creditworthiness |
| Training records | BM-A01, BM-E04 | Trainee “reasoning” dumps |
| Support tickets | BM-A03, BM-E07, BM-R07 | Granting authority to L1 |
| `source_case_baseline.json` | Dashed baseline overlays | Current operating result |
| Workshop fixture profile | Optional dotted overlay, labelled | QT-05 achievement |
| Golden 15 | Behavioral HG/QT on claimed layer | Production TAT |

Refresh: D2 near-real-time or ≤15 min for control counts (exposure freshness class is a **source** SLO, not a dashboard SLA). D1/D3/D4 daily snapshot in hypercare. D5 monthly. Exact platform nines remain **OPEN**.

---

## 4. Honesty strip (required on every dashboard)

| Tile | Display | Green | Red |
|---|---|---|---|
| **Release** | GO / BLOCKED | Signed §5.3 | BLOCKED (current) |
| **Layer** | Contract / Workbench / Production | Matches the numbers below | Mixing layers |
| **Population** | Named book id + n | Named production | Unlabelled or fixture-as-PROD |
| **HG window** | HG-01–HG-08 in claim window | All pass | Any fail |
| **Policy** | Controlling = `CREDIT-POLICY-3.2` | 3.2 ACTIVE | 2.9 or unknown |
| **Rollback** | G-RB-01 | Drill PASS | OPEN / v2.9 folklore |
| **UI** | Screens k/12 | 12/12 | 0/12 (current) |
| **QT-05** | Proven / NOT PROVEN | Proven **and** HG green on named book | Charting 89.5 or 142 as <30 |

**Current strip (2026-09-10):** GO **BLOCKED**; layer **contract**; population **golden 15 + fixture (not PROD)**; HG **contract PASS / UI OPEN**; policy **3.2**; G-RB-01 **OPEN**; UI **0/12**; QT-05 **NOT PROVEN**.

---

## 5. D1 — Steerco one-pager

**Layout (top → bottom).** Time window: last 7 / 30 / 90 days selectable; default 30 after GO.

### Row A — Honesty strip (§4)

### Row B — Hard gates (traffic lights)

| Tile | Metric | Green | Amber | Red |
|---|---|---|---|---|
| AI-final | BM-Q01 / HG-01 | 0 | — | ≥1 |
| Invented threshold | BM-Q02 / HG-02 | 0 | — | ≥1 (critical) |
| Provenance | BM-Q03 / HG-03 | 100% | <100% on sample, no Sev 1 | Material FACT without source on UI path |
| Cross-tenant | BM-R01 / HG-04 | 0 successes | — | ≥1 |
| Restricted runtime | BM-R03 / HG-05 | 0 | — | ≥1 |
| Policy version | BM-R04 / HG-06 | 0 superseded | — | 2.9 controlling |
| Injection | BM-R02 / HG-07 | 0 followed | — | ≥1 |
| Manual fallback | BM-R06 / HG-08 | true | Degraded but completing | Credit path blocked **or** fabricated memo |

Amber is unused for binary HG where case evidence is 0/100%/true. Do not invent an error budget.

### Row C — Value snapshot (paused if Row B red)

| Tile | Metric | Caption required |
|---|---|---|
| Uncomplicated TAT median | BM-P01 | “Named book {id}; source baseline 142; fixture 89.5 is not this tile” |
| Memo minutes | BM-P03 | “vs source 38; HG-03 must be 100%” |
| >3 lookups | BM-P04 | “vs source 57%” |
| Document rework | BM-P05 | “vs source 31.2%” |
| In-workbench completion | BM-A02 | “Shadow tools excluded” |
| Sev 1 | BM-R07 | Count; link to IR |

### Row D — Steerco questions (checklist, not a score)

- Bypassed gates this window?
- Generated text used as policy?
- Feedback wrote 3.2 / prompts / models / gold?
- HG re-run on **UI** path?
- TAT population labelled?

---

## 6. D2 — Hard-control board

Audience: Security, Model risk, Credit Policy. **No TAT tile.**

| Panel | Tiles | Drill-down |
|---|---|---|
| Isolation | BM-R01 count; DENY volume (success) | Tenant pair counts **without** payload |
| Injection | BM-R02; GS-09 class | Document id, treated-as-DATA flag |
| Authority | BM-Q01, BM-Q06, BM-A07 | Application, engine required role, actor, ALLOW/DENY |
| Policy | BM-R04, BM-Q02, ACTIVE hash | Version ids 3.2 vs 2.9; fidelity scan hits |
| Fairness boundary | BM-R03, BM-E06 | Purpose; **no** attribute values on this board |
| Learning loop | BM-A06, BM-R09, BM-E05 | Event id → `GOVERNED_REVIEW`; catalog hash unchanged |
| Fallback | BM-R06, BM-P07 | Outage window, cases completed manually, fabricated-memo = 0 |
| Incidents | BM-R07 | Sev 1 list per `INCIDENT_RESPONSE_PLAN.md` |
| Rollback | BM-R10 | Last drill date; controller ≠ 2.9 |

**Alerting:** any red tile = Sev 1 path. Dashboard does not fail-open.

---

## 7. D3 — Value and productivity

Shown only when honesty strip allows. Two series discipline:

```text
[Chart] Uncomplicated TAT median
  - Production named book (solid)
  - Reference line: 30 min labelled "CRD-BR-001 target"
  - Dashed: source 142
  - Dotted: fixture 89.5 (legend: not QT-05)
  - Banner if HG red: "Productivity paused"
```

| Panel | Metrics | Notes |
|---|---|---|
| Cycle time | BM-P01, BM-P02 | P90 has no binding SLO; show vs 648 as context only |
| Memo burden | BM-P03 | Suppress if HG-03 ≠ 100% |
| Lookup / rework | BM-P04, BM-P05 | Sample n visible |
| Provenance defect | BM-P06 / BM-R08 | vs 13.7% source audit |
| Exception quality | BM-Q07, BM-P08 | Do **not** sparkline 8.4% as “down is good” |
| Semantics | BM-Q04, BM-Q12 | Conflict/stale **visible** counts |
| Quality of assistance | BM-Q11 | Caption: “grounded reject is healthy; do not maximize accept” |

**Workbench vs production:** if G-UI-01 still open, D3 shows a single full-width state: **“Productivity not measured — 0/12 screens.”** Do not fill with contract 15/15.

---

## 8. D4 — Adoption and engagement

| Panel | Metrics | Green / red |
|---|---|---|
| Lab gate | BM-A01, BM-E04 | <100% of named memo cohort = no new memo privilege |
| Completion | BM-A02, BM-E02 | Path missing Human Decision = red |
| Bypass pressure | BM-A03, BM-E07 | Bypass ≥1 in window = amber (coach) or red if isolation/approve |
| Shadow tools | BM-A05 | ≥1 material = red for value claim |
| Cohort | BM-A04, BM-E01 | Vanity org-wide WAU **hidden** |
| First decision | BM-E03 | Diagnostic only |
| RM boundary | BM-A07 | Any ALLOW = red |
| Feedback hygiene | BM-E05 | Catalog mutation = red (also D2) |

**Persona filter:** analyst / senior UW / credit authority / RM / eval. Eval filter must not expose restricted attributes.

---

## 9. D5 — Financial bridge

Default view is **hours and counts**. Currency view is disabled until BM-F04 is a signed CR.

| Tile | Default | If Finance CR signed |
|---|---|---|
| Memo hours avoided | BM-F01 hours | × named rate |
| Lookup/rework hours | BM-F02 (sample) | × named rate |
| Control incidents | BM-F03 count = 0 | **Still no** expected-loss $ from this pack |
| Capacity | BM-F06 **OPEN** | Only if CR names definition |
| Credit-book P&L | Tile reads **“Out of workbench authority (BM-F05)”** | Never sourced from AI scores |
| Payback / ROI | **Hidden** | Hidden unless independent Finance model (not this spec) |

Footer: “Hours valid only if HG green and population named. Workshop PASS is not ROI.”

---

## 10. Wireframe (D1)

```text
┌─────────────────────────────────────────────────────────────────┐
│ HONESTY: GO | Layer | Population | HG window | 3.2 | RB | UI | QT-05 │
├─────────────────────────────────────────────────────────────────┤
│ HG-01 HG-02 HG-03 HG-04 HG-05 HG-06 HG-07 HG-08                 │
├─────────────────────────────────────────────────────────────────┤
│ TAT named book   Memo min    Lookups>3    Rework    In-WB %    │
│ Sev1 count       (paused banner if any HG red)                  │
├─────────────────────────────────────────────────────────────────┤
│ ☐ gates bypassed ☐ text-as-policy ☐ feedback wrote catalog      │
│ ☐ HG on UI       ☐ TAT labelled                                 │
└─────────────────────────────────────────────────────────────────┘
```

Accessible: not colour-only; each light has PASS/FAIL text. Tenant and applicant identifiers follow least-privilege; exec pack uses aggregates.

---

## 11. Role access

| Role | D1 | D2 | D3 | D4 | D5 |
|---|---|---|---|---|---|
| Exec / sponsors | Yes | Summary lights only | Yes | Summary | Hours; $ if CR |
| Independent reviewer | Yes | Yes | Yes | Yes | Yes |
| Credit Operations | Yes | Limited | Yes | Yes | Hours |
| Credit Policy | Yes | Policy panels | Exception panel | Lab | No $ invent |
| Security / Model risk | Yes | **Home** | No TAT edit | Bypass | No |
| `RISK_COMPLIANCE_EVAL` | No runtime board | Fairness **boundary** only | No | Eval containment | No |
| `RELATIONSHIP_MANAGER` | No | No | No | No | No |
| `AI_AGENT` | No | No | No | No | No |

Exec aggregations still run **after** tenant and purpose checks. A sponsor in TENANT-ALPHA does not see TENANT-BETA application lists.

---

## 12. Implementation notes

| Item | Spec |
|---|---|
| Delivery | Scheduled pack (PDF/CSV) + optional internal BI; **not** G-UI-01 scope |
| Build order | Honesty strip + D2 first; D4 with UAT cohort; D3 after day 31; D5 after hours |
| Consistency | Tile IDs = BM-* in the catalog; SM/HG/QT captions on hover |
| Tests | Golden: mixing 89.5 into QT-05 tile = **fail**; HG-02 fail still shows critical even if TAT <30; empty UI still shows 0/12 |
| Non-goals | Applicant-facing dashboard; fairness cutoff gauge; chatbot CSAT; NPL from the model |

---

## 13. Readiness (2026-09-10)

- [x] Tile IDs mapped to BM-* / HG-* / SM-*
- [x] Forbidden charts documented
- [ ] Instrumentation (blocked on G-UI-01 and traces UI)
- [ ] Named production book id
- [ ] Finance rate for BM-F04
- [ ] Independent reviewer sign-off on first live D1

Until then, brief executives with the honesty strip only: **assistance is not a credit decision; value is not being realized from this workshop.**
