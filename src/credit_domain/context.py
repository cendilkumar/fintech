"""CRD-FR-001 / CRD-DATA-002 / CRD-DATA-008 task-specific runtime context graph.

Assembles a connected underwriting slice for one application, actor and as-of
time. Historical memos are not Policy and not objective truth. Stale and
conflicting evidence stay visible. Other applications and tenants are excluded.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from .evidence import (
    WORKSHOP_RETRIEVAL_TIME,
    ApplicationEvidencePack,
    MaterialEvidence,
    assemble_application_evidence,
)
from .model import (
    Applicant,
    ExceptionClass,
    Guarantor,
    Party,
    SemanticCollapseError,
    party_from_fixture,
)
from .policy import (
    ApplicationPolicyView,
    evaluate_application,
    retrieve_active_policy,
)

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "evidence" / "01_enterprise_sources"
HISTORY = ROOT / "evidence" / "05_history_feedback"

UNDERWRITE_TASK = "UNDERWRITE_APPLICATION"
REQUIRED_KINDS_WHEN_PRESENT = (
    "Application",
    "Applicant",
    "Entity",
    "Facility",
    "Guarantor",
    "Exposure",
    "BureauRecord",
    "BankEvidence",
    "TaxEvidence",
    "Policy",
    "Exception",
    "Decision",
    "Evidence",
)
CORE_KINDS = (
    "Application",
    "Applicant",
    "Entity",
    "Facility",
    "Exposure",
    "BureauRecord",
    "BankEvidence",
    "TaxEvidence",
    "Policy",
    "Decision",
    "Evidence",
)


class ContextAuthorityError(SemanticCollapseError):
    """Raised when context is used as the wrong authority object."""


class ContextScopeError(SemanticCollapseError):
    """Raised when a request would dump the repository or cross tenants."""


@dataclass(frozen=True)
class ContextRequest:
    task: str
    application_id: str
    actor_role: str
    actor_tenant: str
    as_of_time: str
    intent: str = "underwrite"
    requested_action: str = "assemble_context"
    context_budget: str = "target_application_only"


@dataclass(frozen=True)
class ContextNode:
    node_id: str
    kind: str
    application_id: str
    tenant_id: str
    label: str
    freshness_state: str = "unknown"
    conflict_state: str = "none"
    authority: str = "unknown"
    presented_as_current: bool = True
    provenance: str = ""
    value: Any = None
    attributes: dict[str, Any] = field(default_factory=dict)

    def as_policy(self) -> None:
        if self.kind == "Policy" and self.presented_as_current:
            return
        raise ContextAuthorityError(
            f"{self.kind} {self.node_id} is not active Policy (CRD-DATA-008)"
        )

    def as_human_decision(self) -> None:
        raise ContextAuthorityError(
            f"{self.kind} {self.node_id} is not a recorded HumanDecision (CRD-DATA-008)"
        )


@dataclass(frozen=True)
class ContextEdge:
    subject: str
    relationship: str
    object: str


@dataclass(frozen=True)
class ExcludedItem:
    ref: str
    reason_code: str
    detail: str


@dataclass(frozen=True)
class HistoricalMemo:
    narrative_id: str
    application_id: str
    tenant_id: str
    text: str
    policy_version_at_time: str
    authoritative_for_current_policy: bool

    def as_policy(self) -> None:
        raise ContextAuthorityError(
            f"{self.narrative_id} is a historical memo, not current Policy"
        )

    def as_objective_truth(self) -> None:
        raise ContextAuthorityError(
            f"{self.narrative_id} is not objective ground truth"
        )


@dataclass
class RuntimeContextGraph:
    request: ContextRequest
    snapshot_id: str
    nodes: list[ContextNode] = field(default_factory=list)
    edges: list[ContextEdge] = field(default_factory=list)
    excluded: list[ExcludedItem] = field(default_factory=list)
    source_health: list[dict[str, str]] = field(default_factory=list)
    policy_version: str | None = None
    unresolved_conflicts: list[dict[str, Any]] = field(default_factory=list)
    controls: tuple[str, ...] = ()

    def nodes_of(self, kind: str) -> list[ContextNode]:
        return [n for n in self.nodes if n.kind == kind]

    def node(self, node_id: str) -> ContextNode:
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        raise ContextScopeError(f"node {node_id} is not in snapshot {self.snapshot_id}")

    def kinds_present(self) -> set[str]:
        return {n.kind for n in self.nodes}

    def exclusion_codes(self) -> set[str]:
        return {item.reason_code for item in self.excluded}

    def application_ids_in_nodes(self) -> set[str]:
        return {n.application_id for n in self.nodes if n.application_id}


def _csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _live_applications() -> list[dict[str, str]]:
    return _csv(EVIDENCE / "live_applications.csv")


def _party_rows(application_id: str) -> list[dict[str, str]]:
    return [
        r
        for r in _csv(EVIDENCE / "application_parties.csv")
        if r["application_id"] == application_id
    ]


def load_historical_memos() -> list[HistoricalMemo]:
    memos: list[HistoricalMemo] = []
    for row in _jsonl(HISTORY / "historical_case_narratives.jsonl"):
        memos.append(
            HistoricalMemo(
                narrative_id=str(row["narrative_id"]),
                application_id=str(row["application_id"]),
                tenant_id=str(row["tenant_id"]),
                text=str(row["text"]),
                policy_version_at_time=str(row["policy_version_at_time"]),
                authoritative_for_current_policy=bool(row.get("authoritative_for_current_policy")),
            )
        )
    return memos


def refuse_repository_dump() -> None:
    raise ContextScopeError(
        "assemble_runtime_context requires a single application_id; "
        "repository dump is forbidden (CRD-FR-001)"
    )


def _add(graph: RuntimeContextGraph, node: ContextNode) -> ContextNode:
    graph.nodes.append(node)
    return node


def _edge(graph: RuntimeContextGraph, subject: str, relationship: str, obj: str) -> None:
    graph.edges.append(ContextEdge(subject=subject, relationship=relationship, object=obj))


def _is_guarantor(row: dict[str, str]) -> bool:
    return row.get("party_type") == "NATURAL_PERSON_GUARANTOR"


def _is_applicant(row: dict[str, str]) -> bool:
    return row.get("is_primary_applicant") == "1" or not _is_guarantor(row)


def _presented_as_current(freshness: str) -> bool:
    return freshness not in {"stale", "unavailable"}


def _evidence_node_kind(fact: MaterialEvidence) -> str:
    if fact.source_system == "BANK":
        return "BankEvidence"
    if fact.source_system == "TAX":
        return "TaxEvidence"
    if fact.source_system == "BUREAU":
        return "BureauRecord"
    if fact.source_system == "EXPOSURE":
        return "Exposure"
    return "Evidence"


def _record_corpus_exclusions(graph: RuntimeContextGraph, app: dict[str, str]) -> None:
    target = app["application_id"]
    actor_tenant = graph.request.actor_tenant
    for row in _live_applications():
        other = row["application_id"]
        if other == target:
            continue
        if row["tenant_id"] != actor_tenant:
            graph.excluded.append(
                ExcludedItem(other, "CROSS_TENANT", f"tenant {row['tenant_id']} != {actor_tenant}")
            )
        else:
            graph.excluded.append(
                ExcludedItem(other, "OTHER_APPLICATION", "not the underwriting target")
            )

    memos = load_historical_memos()
    graph.excluded.append(
        ExcludedItem(
            "historical_case_narratives.jsonl",
            "HISTORICAL_MEMO_NOT_POLICY",
            f"{len(memos)} narratives; authoritative_for_current_policy is false",
        )
    )
    hist_decisions = _jsonl(HISTORY / "historical_decisions.jsonl")
    graph.excluded.append(
        ExcludedItem(
            "historical_decisions.jsonl",
            "HISTORICAL_MEMO_NOT_POLICY",
            f"{len(hist_decisions)} historical decisions are not current HumanDecision",
        )
    )
    beta_memos = [m for m in memos if m.tenant_id != actor_tenant]
    if beta_memos:
        graph.excluded.append(
            ExcludedItem(
                "historical_case_narratives.jsonl:CROSS_TENANT",
                "CROSS_TENANT",
                f"{len(beta_memos)} narratives from other tenants",
            )
        )
    graph.excluded.append(
        ExcludedItem(
            "CREDIT-POLICY-2.9",
            "SUPERSEDED_POLICY",
            "superseded bundle excluded from active policy context",
        )
    )
    graph.excluded.append(
        ExcludedItem(
            "restricted_fairness_eval_sample.csv",
            "RESTRICTED_ATTRIBUTE",
            "EVALUATION_ONLY_APPROVED_PURPOSE; not runtime decision context",
        )
    )
    graph.excluded.append(
        ExcludedItem(
            "historical_applications.csv",
            "IRRELEVANT_TO_TASK",
            "source-case history is not the live underwriting slice",
        )
    )


def _party_entity_id(party: Party, fallback: str) -> str:
    return f"ENTITY:{party.party_id or fallback}"


def assemble_runtime_context(
    application_id: str | None,
    *,
    actor_role: str = "CREDIT_ANALYST",
    actor_tenant: str | None = None,
    as_of_time: str = WORKSHOP_RETRIEVAL_TIME,
    task: str = UNDERWRITE_TASK,
) -> RuntimeContextGraph:
    if not application_id:
        refuse_repository_dump()
    apps = [r for r in _live_applications() if r["application_id"] == application_id]
    if not apps:
        raise ContextScopeError(f"unknown live application {application_id}")
    app = apps[0]
    tenant = actor_tenant or app["tenant_id"]
    request = ContextRequest(
        task=task,
        application_id=application_id,
        actor_role=actor_role,
        actor_tenant=tenant,
        as_of_time=as_of_time,
    )
    graph = RuntimeContextGraph(
        request=request,
        snapshot_id=f"CTX:{application_id}:{as_of_time}",
    )
    _record_corpus_exclusions(graph, app)

    if tenant != app["tenant_id"]:
        graph.excluded.append(
            ExcludedItem(application_id, "CROSS_TENANT", f"actor {tenant} cannot retrieve {app['tenant_id']}")
        )
        graph.controls = ("tenant_isolation_before_retrieval",)
        return graph

    pack = assemble_application_evidence(application_id, retrieval_time=as_of_time)
    policy_view = evaluate_application(application_id, as_of=as_of_time)
    retrieval = retrieve_active_policy(as_of_time)
    graph.policy_version = None if retrieval.controlling is None else retrieval.controlling.version
    graph.source_health = [
        {
            "source": r["source"],
            "state": r["state"],
            "detail": r.get("detail", ""),
        }
        for r in _jsonl(EVIDENCE / "source_health_events.jsonl")
        if r["application_id"] == application_id
    ]
    graph.unresolved_conflicts = [
        {
            "left_evidence_id": c.left_evidence_id,
            "right_evidence_id": c.right_evidence_id,
            "left_semantic_type": c.left_semantic_type,
            "right_semantic_type": c.right_semantic_type,
            "left_value": c.left_value,
            "right_value": c.right_value,
            "conflict_state": c.conflict_state,
        }
        for c in pack.conflicts
    ]
    graph.controls = (
        "retrieve_active_policy",
        "evaluate_application",
        f"identity={pack.identity.state.value if pack.identity else 'unknown'}",
        "tenant_match",
    )

    app_node = _add(
        graph,
        ContextNode(
            node_id=f"APP:{application_id}",
            kind="Application",
            application_id=application_id,
            tenant_id=app["tenant_id"],
            label=app["applicant_name"],
            freshness_state="fresh",
            authority="authoritative",
            provenance=f"live_applications.csv:{application_id}",
            attributes={
                "workflow_status": app["status"],
                "stage": app["current_stage"],
                "identity_state": pack.identity.state.value if pack.identity else None,
            },
        ),
    )

    facility = _add(
        graph,
        ContextNode(
            node_id=f"FACILITY:{application_id}",
            kind="Facility",
            application_id=application_id,
            tenant_id=app["tenant_id"],
            label=app["product"],
            freshness_state="fresh",
            authority="authoritative",
            provenance=f"live_applications.csv:{application_id}:product,requested_limit",
            value={"product": app["product"], "requested_limit": int(app["requested_limit"])},
        ),
    )
    _edge(graph, app_node.node_id, "REQUESTS", facility.node_id)

    org_entity = _add_parties(graph, app, pack, app_node.node_id)
    _add_evidence_nodes(graph, pack, app_node.node_id)
    _add_policy_decision_exceptions(graph, app, pack, policy_view, retrieval, app_node.node_id)
    _add_documents(graph, application_id, app["tenant_id"], app_node.node_id)
    if org_entity:
        pass
    return graph


def _add_parties(
    graph: RuntimeContextGraph,
    app: dict[str, str],
    pack: ApplicationEvidencePack,
    app_node_id: str,
) -> ContextNode | None:
    application_id = app["application_id"]
    org_node: ContextNode | None = None
    identity = pack.identity
    org_ref = identity.safe_entity_ref() if identity else f"UNRESOLVED:{application_id}"
    for row in _party_rows(application_id):
        party = party_from_fixture(row)
        if _is_guarantor(row):
            entity = _add(
                graph,
                ContextNode(
                    node_id=_party_entity_id(party, row["party_id"]),
                    kind="Entity",
                    application_id=application_id,
                    tenant_id=row["tenant_id"],
                    label=party.observed_name,
                    freshness_state="fresh",
                    authority="authoritative",
                    provenance=f"application_parties.csv:{row['party_id']}",
                    attributes={
                        "party_kind": party.kind.value,
                        "role": "Guarantor",
                        "decision_feature_eligible": row.get("decision_feature_eligible"),
                        "restricted_attrs_excluded": True,
                    },
                ),
            )
            guar = _add(
                graph,
                ContextNode(
                    node_id=f"GUARANTOR:{row['party_id']}",
                    kind="Guarantor",
                    application_id=application_id,
                    tenant_id=row["tenant_id"],
                    label=f"Guarantor:{party.observed_name}",
                    freshness_state="fresh",
                    authority="authoritative",
                    provenance=f"application_parties.csv:{row['party_id']}",
                    attributes={"played_by": row["party_id"]},
                ),
            )
            _edge(graph, app_node_id, "MAY_HAVE_GUARANTOR", guar.node_id)
            _edge(graph, guar.node_id, "PLAYED_BY", entity.node_id)
            Guarantor(application_id=application_id, played_by=party)
            continue

        entity_id = (
            f"ENTITY:{org_ref}"
            if row["party_type"] in {"ORGANIZATION", "SOLE_TRADER_BUSINESS"}
            else _party_entity_id(party, row["party_id"])
        )
        entity = _add(
            graph,
            ContextNode(
                node_id=entity_id,
                kind="Entity",
                application_id=application_id,
                tenant_id=row["tenant_id"],
                label=party.observed_name,
                freshness_state="fresh",
                authority="authoritative",
                provenance=f"application_parties.csv:{row['party_id']}",
                attributes={
                    "party_kind": party.kind.value,
                    "party_id": row["party_id"],
                    "identity_state": identity.state.value if identity else None,
                    "canonical_party_id": identity.organization.canonical_party_id if identity else None,
                    "hypothesized_candidate": identity.organization.hypothesized_candidate if identity else None,
                },
            ),
        )
        if row["party_type"] in {"ORGANIZATION", "SOLE_TRADER_BUSINESS"}:
            org_node = entity
        if _is_applicant(row):
            applicant = _add(
                graph,
                ContextNode(
                    node_id=f"APPLICANT:{row['party_id']}",
                    kind="Applicant",
                    application_id=application_id,
                    tenant_id=row["tenant_id"],
                    label=f"Applicant:{party.observed_name}",
                    freshness_state="fresh",
                    authority="authoritative",
                    provenance=f"application_parties.csv:{row['party_id']}",
                    attributes={"is_primary": row.get("is_primary_applicant") == "1"},
                ),
            )
            _edge(graph, app_node_id, "HAS_APPLICANT_ROLE", applicant.node_id)
            _edge(graph, applicant.node_id, "PLAYED_BY", entity.node_id)
            Applicant(application_id=application_id, played_by=party)
    return org_node


def _add_evidence_nodes(
    graph: RuntimeContextGraph,
    pack: ApplicationEvidencePack,
    app_node_id: str,
) -> dict[str, str]:
    ids: dict[str, str] = {}
    for fact in pack.facts:
        kind = _evidence_node_kind(fact)
        node_id = f"{kind.upper()}:{fact.evidence_id}"
        current = _presented_as_current(fact.freshness_state)
        node = _add(
            graph,
            ContextNode(
                node_id=node_id,
                kind=kind,
                application_id=fact.application_id,
                tenant_id=fact.tenant_id,
                label=fact.semantic_type,
                freshness_state=fact.freshness_state,
                conflict_state=fact.conflict_state,
                authority=fact.authority,
                presented_as_current=current,
                provenance=fact.provenance,
                value=fact.value,
                attributes={
                    "semantic_type": fact.semantic_type,
                    "source_system": fact.source_system,
                    "source_record_id": fact.source_record_id,
                    "entity_ref": fact.entity_ref,
                    "period": fact.period,
                    "event_time": fact.event_time,
                    "retrieval_time": fact.retrieval_time,
                },
            ),
        )
        ids[fact.evidence_id] = node.node_id
        rel = "HAS_EXPOSURE" if kind == "Exposure" else "HAS_EVIDENCE"
        _edge(graph, app_node_id, rel, node.node_id)
        _edge(graph, node.node_id, "OBSERVES", f"MEASURE:{fact.semantic_type}")
    for conflict in pack.conflicts:
        left = ids.get(conflict.left_evidence_id)
        right = ids.get(conflict.right_evidence_id)
        if left and right:
            _edge(graph, left, "CONFLICTS_WITH", right)
    return ids


def _add_policy_decision_exceptions(
    graph: RuntimeContextGraph,
    app: dict[str, str],
    pack: ApplicationEvidencePack,
    policy_view: ApplicationPolicyView,
    retrieval: Any,
    app_node_id: str,
) -> None:
    application_id = app["application_id"]
    controlling = retrieval.controlling
    policy_node = _add(
        graph,
        ContextNode(
            node_id=f"POLICY:{application_id}:{graph.policy_version or 'ABSTAIN'}",
            kind="Policy",
            application_id=application_id,
            tenant_id=app["tenant_id"],
            label=graph.policy_version or "ABSTAIN",
            freshness_state="fresh" if controlling else "unavailable",
            authority="authoritative" if controlling and controlling.controlling else "non_authoritative",
            presented_as_current=bool(controlling and controlling.controlling),
            provenance="retrieve_active_policy+policy_engine_results.jsonl",
            value=None if policy_view.engine is None else policy_view.engine.result,
            attributes={
                "controlling": bool(controlling and controlling.controlling),
                "status": None if controlling is None else controlling.status,
                "engine_result": None if policy_view.engine is None else policy_view.engine.result,
                "triggered_rule_ids": []
                if policy_view.engine is None
                else list(policy_view.engine.triggered_rule_ids),
                "required_human_role": policy_view.required_human_role,
                "los_assigned_role": policy_view.los_assigned_role,
                "stance": policy_view.stance.value,
            },
        ),
    )
    _edge(graph, app_node_id, "EVALUATED_BY", policy_node.node_id)
    _edge(graph, policy_node.node_id, "USES_POLICY", graph.policy_version or "NONE")

    decision = _add(
        graph,
        ContextNode(
            node_id=f"DECISION:{application_id}:PENDING",
            kind="Decision",
            application_id=application_id,
            tenant_id=app["tenant_id"],
            label="PENDING",
            freshness_state="unknown",
            authority="human_required",
            presented_as_current=False,
            provenance="no recorded HumanDecision on live application",
            value=None,
            attributes={
                "status": "PENDING",
                "outcome": None,
                "required_human_role": policy_view.required_human_role,
                "policy_result_is_not_decision": True,
            },
        ),
    )
    _edge(graph, app_node_id, "AWAITS", decision.node_id)

    exceptions: list[tuple[ExceptionClass, str]] = []
    if pack.identity and pack.identity.exceptions:
        for exc in pack.identity.exceptions:
            exceptions.append((exc.exception_class, exc.detail))
    for conflict in pack.conflicts:
        exceptions.append(
            (
                ExceptionClass.FINANCIAL_CONFLICT,
                f"{conflict.left_semantic_type} vs {conflict.right_semantic_type}",
            )
        )
    if policy_view.exception_class is not None:
        exceptions.append((policy_view.exception_class, policy_view.engine.result if policy_view.engine else ""))
    if any(n.kind == "BankEvidence" and n.freshness_state == "stale" for n in graph.nodes):
        exceptions.append((ExceptionClass.FRESHNESS, "bank evidence stale; not current"))

    seen: set[tuple[str, str]] = set()
    for klass, detail in exceptions:
        key = (klass.value, detail)
        if key in seen:
            continue
        seen.add(key)
        node = _add(
            graph,
            ContextNode(
                node_id=f"EXCEPTION:{application_id}:{klass.value}:{len(seen)}",
                kind="Exception",
                application_id=application_id,
                tenant_id=app["tenant_id"],
                label=klass.value,
                freshness_state="fresh",
                authority="authoritative",
                provenance="context assembly",
                attributes={"exception_class": klass.value, "detail": detail},
            ),
        )
        _edge(graph, app_node_id, "MAY_RAISE", node.node_id)
        _edge(graph, policy_node.node_id, "MAY_RAISE", node.node_id)


def _add_documents(
    graph: RuntimeContextGraph,
    application_id: str,
    tenant_id: str,
    app_node_id: str,
) -> None:
    for row in _jsonl(EVIDENCE / "documents_received.jsonl"):
        if row.get("application_id") != application_id:
            continue
        node = _add(
            graph,
            ContextNode(
                node_id=f"EVIDENCE:{row['document_id']}",
                kind="Evidence",
                application_id=application_id,
                tenant_id=tenant_id,
                label=row["document_type"],
                freshness_state="fresh",
                authority="non_authoritative",
                provenance=f"documents_received.jsonl:{row['document_id']}",
                value=row.get("text_excerpt"),
                attributes={
                    "trust_class": row.get("trust_class"),
                    "filename": row.get("filename"),
                    "untrusted_content": True,
                },
            ),
        )
        _edge(graph, app_node_id, "HAS_EVIDENCE", node.node_id)


def traverse_connected_context(
    graph: RuntimeContextGraph,
    start_node_id: str,
    relationship: str | None = None,
) -> list[tuple[ContextEdge, ContextNode]]:
    """CRD-TOOL-002: walk only nodes already in the approved snapshot."""
    graph.node(start_node_id)
    out: list[tuple[ContextEdge, ContextNode]] = []
    for edge in graph.edges:
        if edge.subject != start_node_id:
            continue
        if relationship and edge.relationship != relationship:
            continue
        if edge.object.startswith("MEASURE:") or edge.object in {"NONE", "CREDIT-POLICY-3.2"}:
            continue
        try:
            out.append((edge, graph.node(edge.object)))
        except ContextScopeError:
            continue
    return out


def historical_memo_as_policy(memo: HistoricalMemo) -> None:
    memo.as_policy()
