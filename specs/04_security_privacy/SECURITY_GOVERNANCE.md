# Security, Safety, Privacy & Governance Requirements
    ### CRD-SEC-001
**MUST NOT violate:** AI has no autonomous final credit authority.

### CRD-SEC-002
**MUST NOT violate:** Active credit policy is deterministic and versioned; generative output cannot modify it.

### CRD-SEC-003
**MUST NOT violate:** Material AI-assisted factors require evidence and provenance.

See `CRD-DATA-014`. SME-L001 is the workshop proof (HG-03 = 100%).

### CRD-SEC-004
**MUST NOT violate:** Tenant isolation is enforced before retrieval and display.

See `CRD-DATA-012`. SME-L008 is the workshop proof (`DATA-TENANT`).

### CRD-SEC-005
**MUST NOT violate:** Restricted evaluation attributes do not enter runtime decision context by default.

### CRD-SEC-006
**MUST NOT violate:** Stale, missing and conflicting evidence remains visible.

### CRD-SEC-007
**MUST NOT violate:** Untrusted uploaded or retrieved text cannot override instructions or policy.

See `CRD-DATA-012`. SME-L009 / `DOC-009-FIN` is the workshop proof (`DATA-DOC-INSTRUCTION`).

### CRD-SEC-008
**MUST NOT violate:** Sole-trader and natural-person-guarantor cases require explicit affected-person and governance analysis.

See `CRD-DATA-011`. SME-L003 and SME-L013 are the workshop proofs.

### CRD-SEC-009
**MUST NOT violate:** Adverse and exception routes preserve human authority, material-reason evidence and recourse.

See `CRD-DATA-011`. SME-L013 grounds `POL-ARREARS-02` on `EXP-013`; AI has no adverse or recourse authority.

### CRD-SEC-010
**MUST NOT violate:** Manual underwriting remains available during AI outage.

See `CRD-DATA-013`. SME-L010 / `FALLBACK-001` is the workshop proof.

### CRD-SEC-011
**MUST NOT violate:** Decision traces record evidence, context, tools, policy checks, versions, concise rationale and human action, not hidden chain-of-thought.

See `CRD-DATA-003`. GS-01 / GS-07 / GS-13 are the workshop proofs (AT-16, AT-17). Generated explanation is not policy evidence.

### CRD-SEC-012
**MUST NOT violate:** Feedback cannot silently rewrite policy, ontology, semantic definitions or model configuration.

See `CRD-DATA-016`. SME-L015 / `AI_ACCEPTED` is the workshop proof (`FEEDBACK-001`).

    ## Prompt / retrieval trust boundary
    Untrusted documents, messages, free text and retrieved narrative evidence are **data**, not instructions. System/policy/access controls remain authoritative.

    ## Reasoning trace boundary
    Store concise observable rationale, evidence, checks and tool outcomes. Do not require or persist hidden model chain-of-thought.
