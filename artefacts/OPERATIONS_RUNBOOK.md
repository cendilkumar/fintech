# Operations Runbook — SME Credit Underwriting Intelligence Workbench

**Compiled:** 2026-09-10  
**CRD IDs:** `CRD-NFR-004`–`007`, `CRD-FR-008`–`011`, `CRD-SEC-001`–`012`, `CRD-DATA-013`, HG-01–HG-08, `FALLBACK-001`, `FEEDBACK-001`  
**Companions:** `artefacts/SUPPORT_MODEL.md`, `artefacts/INCIDENT_RESPONSE_PLAN.md`, `artefacts/DR_STRATEGY.md`, `artefacts/SLA_SLO_CATALOG.md`, `artefacts/ENVIRONMENT_STRATEGY.md`  
**Status:** Target operating procedures. **Production GO is BLOCKED.** Workbench screens are not implemented. This runbook does not authorize lending use, invent extra credit thresholds, or treat workshop TAT as QT-05.

**Standing orders**
1. Screens display gates; they are not the control plane.
2. AI has no final credit, adverse, exception or recourse authority.
3. Tenant isolation and document-as-DATA filters stay on during incidents (no fail-open).
4. Restore previous **ACTIVE** policy; **never** `CREDIT-POLICY-2.9`.
5. Do not ACK `HumanDecision` without a persisted AT-16 trace (RPO 0).
6. Preserve inconvenient evidence; do not overwrite traces to make an incident look clean.

---

## 1. Service ownership

Logical service = workbench + deterministic control plane + adapters. Brownfield sources remain owned by their inventory owners.

| Service / asset | Accountable owner | Operates | Escalates to |
|---|---|---|---|
| Workbench UI (12 screens) | Engineering | Operations | Credit Operations (usability of Human Decision) |
| Authority / isolation / safety gates (`CRD-TOOL-005/006`) | Engineering | Operations | Security (HG-04/07); Credit authority (HG-01) |
| Active policy retrieve (`CRD-TOOL-004`) | Credit Policy | Operations | Credit Policy (HG-02/06) |
| Context + hybrid retrieval | Engineering | Operations | Credit Risk / Data Partnerships (source facts) |
| Decision trace store | Credit Operations | Engineering / Operations | Independent reviewer on integrity |
| Governed feedback queue | Model risk / evals | Engineering | Credit Policy if write-protect fails |
| Eval suite / QT-01 | Model risk / evals | CI / Engineering | Policy owner on HG-02 |
| Fairness eval zone | Risk / compliance eval | Engineering | Security if sample reaches runtime |
| Optional LLM | Model risk / evals | Operations | Credit Operations (fallback), not for “approve anyway” |
| LOS / documents | Lending Operations | Source ops | Credit Operations |
| Bureau / tax | Credit Risk | Partner ops | Engineering (adapter) |
| Bank data | Data Partnerships | Partner ops | Engineering (adapter) |
| Exposure | Portfolio Risk | Source ops | Engineering |
| Policy engine | Credit Policy | Source ops | Engineering (adapter) |
| Case management | Credit Operations | Source ops | Engineering |

RACI for **credit outcome** is unchanged: `AI_AGENT` = consult (advisory); accountable = engine-required human role.

---

## 2. Monitoring procedures

`CRD-NFR-006`: source health, degraded mode, retrieval/tool failures and decision-trace completeness MUST be observable. Production metrics pipeline is **NOT PROVEN**; until it exists, TEST uses eval reports and contract logs.

### 2.1 What to watch (always)

| Signal | Binding threshold | Alert if | Owner |
|---|---|---|---|
| Degraded mode | One of four modes (`CRD-DATA-013`) | Unknown mode; AI down but case blocked; bureau missing classified as policy exception | Operations + Credit Operations |
| `AI_ASSIST` health | HG-08 | Unavailability **and** fabricated memo or blocked case | Operations |
| Bank freshness | >7 days = stale, not current | Presented as current (GS-05 class) | Data Partnerships |
| Bureau envelope | Null if unavailable | Invented score band | Credit Risk |
| Exposure freshness | ≤15 min expected | Silent omit of past-due | Portfolio Risk |
| Policy controlling version | `CREDIT-POLICY-3.2` | v2.9 `controlling=true` (HG-06) | Credit Policy |
| Cross-tenant retrieve/display | HG-04 = 0 | Any TENANT-BETA content to ALPHA actor | Security — **severity 1** |
| Injection followed | HG-07 = 0 | Document instruction changed policy/role/approval | Security — **severity 1** |
| Restricted attr in runtime | HG-05 = 0 | Fairness sample or CONDITIONAL person attrs in underwriting context | Security + Risk/compliance |
| AI final action ALLOW | HG-01 = 0 | `APPROVE`/`DECLINE`/`ISSUE_ADVERSE`/… ALLOW for `AI_AGENT` | Credit authority — **severity 1** |
| Invented threshold | HG-02 = 0 (critical) | Generated cutoff not in 3.2 | Credit Policy — **severity 1** |
| Trace persist | RPO 0 | HumanDecision ACK without AT-16 | Credit Operations |
| Feedback writes | G-FB-01 | Policy/ontology/prompt/model/gold mutation | Model risk — **severity 1** |
| Source health board | Visible on Control Tower (when built) | Missing health for BANK/BUREAU/POLICY/AI | Operations |

Hard-control signals have **no error budget** (`artefacts/SLA_SLO_CATALOG.md` §3).

### 2.2 Cadence

| Cadence | Activity | Environment |
|---|---|---|
| Continuous (when probes exist) | Synthetic Human Decision + Control Tower; tenant-isolation canary (GS-08 class) | UAT/PROD |
| Each deploy | `CRD-TOOL-009` golden suite; HG-01–HG-08 | TEST, then UAT on UI path |
| Daily (PROD, when live) | Source-health review; degraded-mode counts; unprotected-hash check on 3.2 | PROD |
| Weekly | Eval QUALITY rows; stale/conflict visibility QT-03/04 | UAT/PROD |
| Before GO / quarterly after | G-RB-01 catalog restore; GS-10+02+13 human override | DR/PROD |
| On every CR | Specs first; high-impact authority review (`DEFINITION_OF_DONE.md`) | All |

Until UAT exists, “continuous probes” are **OPEN**. Contract-layer suite remains the TEST monitor.

### 2.3 Dashboards (target)

1. **Control Tower:** application, tenant, stage, source-health, exception class (missing evidence ≠ policy exception).
2. **Degraded mode:** counts of the four modes; AI-outage with manual path success rate (target 100%).
3. **Hard gates:** rolling 0/100%/true for HG-01–HG-08 on the **claimed layer**.
4. **Trace integrity:** persist failures, missing AT-16 fields, forbidden CoT keys.
5. **Partner latency:** excluded from NFR-PERF-04 p95; still shown so TAT is not blamed on the workbench alone.

Do not chart workshop 89.5 or source 142 as the 30-minute SLO.

---

## 3. Troubleshooting guides

Classify first: **credit-path** vs **assistance** vs **control-plane breach**. Control-plane breach → `INCIDENT_RESPONSE_PLAN.md` immediately.

### 3.1 Analyst cannot finish a case because AI is down

| Check | Expect | Action |
|---|---|---|
| Health `AI_ASSIST` | `UNAVAILABLE` | Expected; not a credit outage |
| Mode | `AI_ASSISTANCE_UNAVAILABLE` | Open Human Decision / LOS case path |
| Memo | No fabricated “AI recommends” | Delete/block if present |
| Engine role | Still from Policy Engine | GS-10: large limit still `CREDIT_AUTHORITY` |
| Trace | AI unused; human action recorded | Continue |

If the **case is blocked solely because the model is down**, that is an HG-08 incident (severity 1 for credit path).

### 3.2 Bureau missing vs true policy exception

| Symptom | Mode | Do not |
|---|---|---|
| No bureau row / `UNAVAILABLE` | `REQUIRES_ADDITIONAL_EVIDENCE` (GS-06) | Invent a score; treat as GS-07 |
| Engine `EXCEPTION_REVIEW` / `POL-EXC-07` | Route `SENIOR_UNDERWRITER` (GS-07) | Let AI `APPROVE_EXCEPTION` |

### 3.3 Bank looks “wrong” or old

1. Read `freshness_state`. If stale, it MUST be visible and `presented_as_current=false`.
2. Engine `PASS` does **not** make the feed current.
3. Do not average with tax turnover (GS-11). Surface both envelopes.
4. Request refresh or continue with explicit stale handling.

### 3.4 Identity looks like one company in three names

1. Keep `AMBIGUOUS` / `UNRESOLVED` (GS-04).
2. `canonical_candidate` is a hypothesis, not MATCHED.
3. Escalate adjudication to existing human authority — do not invent a new role or silent-merge in ops.

### 3.5 Memo mentions a threshold not in 3.2

1. Treat as HG-02 critical (GS-14 class; workshop probe INR 2,500,000 is not policy).
2. Reject/flag memo; do not promote text into the catalog.
3. Page Credit Policy + Model risk. See incident plan.

### 3.6 User asks to “just use the other tenant’s file” or document says ignore policy

1. Isolation/injection: **deny**. Do not widen scope because a stakeholder is in a hurry.
2. Preserve the document as `UNTRUSTED_CONTENT`.
3. Page Security. Do not fail-open.

### 3.7 HumanDecision save fails

1. Do not tell the user it is decided.
2. Check trace store; RPO 0 means ACK is forbidden.
3. Fail over store per `DR_STRATEGY.md` §4.3.
4. Do not invent the missing outcome later (G-FB-02).

### 3.8 Feedback “accepted the AI draft” and someone wants policy updated

1. Queue `GOVERNED_REVIEW` only.
2. Confirm hashes of 3.2 / ontology / gold / prompts unchanged.
3. If mutated → severity 1 (G-FB-01). Revert via dual-control; never via 2.9.

### 3.9 Workbench vs LOS assigned role disagree

Trust **engine `required_human_role`**, not LOS `assigned_role` (GS-02). Senior underwriter cannot self-authorize a Credit Authority limit.

---

## 4. Recovery procedures

Detailed regional DR: `artefacts/DR_STRATEGY.md`. Day-2 recoveries:

| Event | Immediate recovery | Verify |
|---|---|---|
| AI down | Manual path; do not wait for LLM | HG-08; policy/source visible |
| Partner down | Null/stale envelopes; abstain if policy/structured out | No invented facts |
| Trace store down | Stop ACK; restore replica | AT-16 persist |
| Bad policy promote | Previous ACTIVE; **never 2.9** | GS-12 controlling=3.2 |
| Region loss | Promote DR gates+UI+traces | Isolation still on |
| Tenant/injection breach | Deny traffic; preserve evidence | GS-08/09 before resume |
| Restricted sample in runtime | Isolate eval zone; purge from context | HG-05 = 0 |

**After recovery:** store evidence; do not overwrite prior traces; re-run the matching GS on the **claimed layer**.

---

## 5. Maintenance processes

| Process | Rule | Owner |
|---|---|---|
| Change intent | Specs/traceability before code (`CHANGE_CONTROL.md`) | Engineering + spec owner |
| High-impact gate change | Human reviewer (`DEFINITION_OF_DONE.md`) | Credit authority / Policy / Security as applicable |
| Policy catalog edit | Dual-control; eval GS-12/14 | Credit Policy |
| Model/prompt change | Version in traces; HG-02/07/09 still pass; `versions` not silently NONE while calling a live model | Model risk |
| Ontology / gold | Governed CR only; not from `AI_ACCEPTED` | Model risk + Credit Policy |
| Dependency patch | Recycle adapters; gates stay on | Operations |
| Fixture refresh | Workshop only; never as live book | Engineering |
| Maintenance window | Proposed UI 99.5% **excludes** agreed maintenance; **cannot** pause HG-* | Operations |
| Fairness eval job | Separate purpose; no runtime feature injection | Risk / compliance eval |
| Backup | Traces + ACTIVE catalog + IAM; vector lowest priority | Operations |

**Forbidden maintenance**
- Prompt-only hotfix for isolation, injection, or invented thresholds
- Disabling `check_access_and_authority` “temporarily”
- Loading fixtures into PROD
- Using v2.9 because it is “simpler to roll back to”

---

## 6. Shift checklist (when PROD exists)

**Start of shift**
- [ ] Source health: LOS, BANK, BUREAU, TAX, EXPOSURE, POLICY, AI
- [ ] Degraded-mode histogram sane (L006 ≠ L007)
- [ ] No HG-01–HG-07 counters > 0
- [ ] Trace persist errors = 0
- [ ] Protected policy hash unchanged unless a signed CR says otherwise

**End of shift**
- [ ] Open incidents have severity, owner, credit-path impact (yes/no)
- [ ] Cases left in `MANDATORY_ABSTENTION` have human owners
- [ ] No unsigned catalog or model change

Until PROD exists, Engineering runs the TEST equivalent after each slice: eval suite + sanity check.
