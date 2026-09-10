# Domain Ontology — NexLend SME Credit (workshop)

**Normative source:** `specs/05_data_contracts/DOMAIN_MODEL.md`. Relationships and constraints there are authoritative.

## 1. Scope

Support: who/what is underwritten; which source produced which measure; whether identity is MATCHED/AMBIGUOUS/UNRESOLVED; which policy version ran; who has authority; what was recommended vs decided.

## 2. Classes / concepts

Party kinds: LegalEntity, SoleTraderBusiness, NaturalPerson.  
Roles: Applicant, Guarantor.  
Case objects: Application, Facility, RequestedLimit, Exposure, Evidence, Consent.  
Measures: FinancialMetric, BankTransaction, TaxFiling, BureauRecord.  
Control objects: Policy, PolicyRule, PolicyEvaluation, Exception, AdverseFactor, Authority.  
Advice vs decision: CreditMemo, Recommendation, HumanDecision.

## 3. Relationships

Application HAS_APPLICANT_ROLE Applicant PLAYED_BY Party; MAY_HAVE Guarantor; REQUESTS Facility HAS RequestedLimit; HAS_INTERNAL Exposure; HAS Evidence OBSERVES a typed fact; EVALUATED_BY PolicyEvaluation USES Policy; MAY_HAVE CreditMemo MAY_CONTAIN Recommendation REQUIRES Authority; RESULTED_IN HumanDecision TAKEN_UNDER Authority.

## 4. Semantic constraints

SEM-01–SEM-10 in DOMAIN_MODEL.md. High-impact SEM-06/09/10 are deterministic controls, not prompt text.

## 5. Taxonomies

Identity: MATCHED | AMBIGUOUS | UNRESOLVED.  
Exception: MISSING_EVIDENCE | POLICY_EXCEPTION | IDENTITY | FINANCIAL_CONFLICT | FRESHNESS | ADVERSE.  
Recommendation stance vs HumanDecision outcome vs PolicyEvaluation.result — three vocabularies.

## 6. Boundary with policy engine

The ontology describes types. The policy engine remains authoritative for active rule results and required human role. The model MUST NOT treat PASS as APPROVE or a memo as policy.
