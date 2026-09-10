# SME Credit Underwriting Policy — Workshop Version 3.2

**Status:** ACTIVE  
**Owner:** Credit Policy  
**Effective:** 2026-07-01  
**Fictional workshop policy; not lending advice or a real institution's policy.**

1. Final approve/decline/conditional decisions are made only by an authorized human credit role.
2. The policy engine, not an LLM, is authoritative for active deterministic rules and authority routing.
3. Applications with a requested limit above INR 5,000,000 require `CREDIT_AUTHORITY` approval in this workshop scenario.
4. A bank-data summary older than 7 days is stale for automated financial reconciliation and must be refreshed or explicitly handled as an exception.
5. Required external evidence that is unavailable must be represented as missing; absence may not be hallucinated or imputed as a positive fact.
6. Material factors shown in an AI-assisted memo must identify supporting source records, freshness and policy rule references where applicable.
7. Protected/sensitive attributes are not default underwriting features. Any fairness evaluation use requires approved governance, purpose limitation and restricted access.
8. Tenant/customer isolation applies before retrieval and before display.
9. Adverse or exception pathways require an inspectable human decision record and applicable recourse/appeal handling.
10. AI-generated text cannot create, change or waive a credit threshold.
