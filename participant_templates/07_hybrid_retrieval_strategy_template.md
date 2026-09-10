# Template 07 — Hybrid Retrieval Strategy

**Normative source:** `specs/05_data_contracts/DATA_CONTRACTS.md` (`CRD-DATA-009`). This worksheet is a readable extract, not a second authority.

## Retrieval routing table

| Task/question pattern | Retrieval type | Source/index | Filters | Ranking/fusion | Returned evidence contract | Fallback |
|---|---|---|---|---|---|---|
| Exact current metric/state | structured `CRD-TOOL-001` | LOS / bank / tax / exposure / source health | tenant, application | exact key | CRD-DATA-001 envelope | abstain if missing |
| Connected dependency / multi-hop impact | graph `CRD-TOOL-002` | runtime context graph | tenant, snapshot | relationship walk | node + provenance + identity/freshness | empty hop |
| Similar historical narrative | semantic `CRD-TOOL-003` | historical memos + applicant docs | tenant; untrusted | lexical overlap (vector stand-in) | non-controlling DATA | no hit |
| Active policy / authority | policy `CRD-TOOL-004` | CREDIT-POLICY-3.2 + engine | as-of, ACTIVE | deterministic version/date | controlling Policy + PolicyEvaluation | abstain |
| Prior decision / outcome | memory | historical_decisions.jsonl | tenant | recency in fixture order | historical only | exclude from Decision |

## Mandatory design decisions

- How is task intent classified? Deterministic `NEED_CATALOG` / question regex. Unknown need raises.
- How is tenant access enforced before retrieval? Actor tenant must match application tenant or the plan is `CROSS_TENANT` with no hops.
- How are active document versions selected? `retrieve_active_policy` by status/as-of. Similarity cannot choose authority.
- How is authoritative source precedence represented? Only `policy` hops may have `controlling=true`.
- How are structured/graph/vector/policy/memory results fused? Concatenate hops; `fuse_plan` rejects controlling semantic/memory hops.
- What happens when results conflict? Bank and tax both return; `conflict_state=unresolved`; no average.
- What does the LLM receive versus what remains in tool metadata? Facts + hop trace; policy authority stays in the policy hop.
- What metrics evaluate retrieval-route correctness? Family/tool/source_ref/controlling on GS-02, GS-05, GS-11, GS-12.
