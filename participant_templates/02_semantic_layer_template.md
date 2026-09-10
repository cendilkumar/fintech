# Semantic Layer — NexLend SME Credit (workshop)

**Normative source:** `specs/05_data_contracts/DOMAIN_MODEL.md` (`CRD-DATA-004`). This worksheet is a readable extract, not a second authority.

## A. Canonical entities

| Canonical entity | Business definition | Canonical identifier | Source mappings | Owner | Notes |
|---|---|---|---|---|---|
| LegalEntity | Registered organization borrower | `ORG-*` | LOS ORGANIZATION | Lending Operations | Not a NaturalPerson |
| SoleTraderBusiness | Sole-trader business identity | `ORG-*` (sole_trader) | LOS SOLE_TRADER_BUSINESS | Lending Operations | Not the owner person |
| NaturalPerson | Human owner or guarantor | `NP-*` | LOS NATURAL_PERSON_* | Credit Risk | Restricted attrs excluded by default |
| Applicant | Role: party requesting the facility | role binding | is_primary_applicant | Credit Operations | Not a party kind |
| Guarantor | Role: typically NaturalPerson | role binding | NP-004, NP-013 | Credit Operations | Not the applicant entity |
| Application | Workflow facility request | `SME-L00x` | LOS application_id | Lending Operations | Not external identity |
| Facility | Product requested | product code | LOS product | Credit Policy | |
| RequestedLimit | Amount requested | amount + as-of | LOS requested_limit | LOS | Not Exposure.approved_limit |
| Exposure | Internal book obligations | EXP-* | Exposure System | Portfolio Risk | Not BureauRecord |
| BankTransaction | Consented cash movement / summary | BANK-* | Bank Data | Data Partnerships | Not tax turnover |
| FinancialMetric | Typed sourced measure | measure_kind + source | bank/tax/exposure/docs | Credit Risk | No generic `revenue` |
| TaxFiling | Declared filing observation | TAXREC-* | Tax/GST | Credit Risk | TAX_DECLARED_TURNOVER only |
| BureauRecord | Provider commercial history | BUR-* | Bureau | Credit Risk | May be absent |
| Policy | Versioned rule bundle | CREDIT-POLICY-3.2 | Policy Engine | Credit Policy | v2.9 is not active |
| PolicyRule | Single deterministic rule | AUTH-LIMIT-01, … | triggered_rule_ids | Credit Policy | Not generated text |
| Exception | Classed stop or deviation | exception_class | Policy + Case | Credit Operations | Missing evidence ≠ policy exception |
| AdverseFactor | Material negative factor + source | factor + evidence_id | Exposure/bureau/policy | Credit Authority | Not an AI decline |
| CreditMemo | Draft or recorded narrative | memo_id | Memo repo | Credit Operations | Not policy or decision |
| Recommendation | Advisory stance + required Authority | stance | AI or analyst | AI / Analyst | Never HumanDecision |
| HumanDecision | Authorized recorded outcome | outcome + role | Case Management | Human role | Only source of final decision |
| Evidence | Provenance-bearing observation | evidence_id | CRD-DATA-001 | Platform | |
| Consent | Purpose-limited source permission | purpose + status | LOS / partnerships | Data Partnerships | |
| Authority | Role + decision scope | role matrix | PolicyEvaluation.required_human_role | Credit Policy | AI_AGENT final = NO |

## B. Canonical metrics

| Metric | Business definition | Formula | Dimensions | Authoritative inputs | Freshness | Known limitations |
|---|---|---|---|---|---|---|
| BANK_INFLOWS_12M | Provider twelve-month inflows | source sum | application, account, as-of | BANK.twelve_month_inflows | ≤7 days or stale | Not turnover or statement revenue |
| TAX_DECLARED_TURNOVER | Declared filing turnover | filing value | application, period | TAX.declared_turnover | filing period; reuse CONDITIONAL | Not bank inflow |
| STATEMENT_RECOGNIZED_REVENUE | Statement-recognized revenue | statement line | document version | DOCS interpretation | document-scoped | Document is untrusted content |
| INTERNAL_EXISTING_EXPOSURE | Booked internal exposure | book value | application | EXPOSURE.existing_exposure | ≤15 min | Not bureau debts |

## C. Physical-to-semantic mappings

See DOMAIN_MODEL.md §7. Critical: BANK.twelve_month_inflows → BANK_INFLOWS_12M; TAX.declared_turnover → TAX_DECLARED_TURNOVER; POLICY.result → PolicyEvaluation.result; CASE.decision → HumanDecision.outcome.

## D. Ambiguities resolved

| Term | Canonical meaning | Must not be confused with |
|---|---|---|
| customer | LOS party observation | NaturalPerson or resolved legal entity |
| applicant | Applicant role | Party kind |
| revenue | Forbidden measure kind | Use the three distinct measures |
| approved | HumanDecision.APPROVE | PolicyEvaluation.PASS |
| confidence | Namespaced (extraction vs other) | Creditworthiness |
| fresh | Source-specific freshness_state | One global flag |
| ground truth | Adjudicated evaluation label only | Historical HumanDecision |
| exception | Exception.class required | A single queue |

## E. Unresolved decisions

Production legal classification of sole trader; TAT clock start; CRD-DATA-001 SHOULD vs MUST for non-material facts. See DOMAIN_MODEL.md §9.
