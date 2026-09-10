"""CRD-FR-004 / CRD-DATA-009 hybrid retrieval routing.

Structured = numeric/current facts; graph = ownership/guarantor/exposure;
semantic = supporting narrative/history; policy = versioned rules.
Vector/lexical similarity cannot override deterministic policy.
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Iterable

from .context import (
    assemble_runtime_context,
    load_historical_memos,
    traverse_connected_context,
)
from .evidence import WORKSHOP_RETRIEVAL_TIME, assemble_application_evidence
from .model import SemanticCollapseError
from .policy import (
    evaluate_application,
    retrieve_active_policy,
    use_similarity_hit_as_authority,
)

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "evidence" / "01_enterprise_sources"
HISTORY = ROOT / "evidence" / "05_history_feedback"


class RetrievalFamily(str, Enum):
    STRUCTURED = "structured"
    GRAPH = "graph"
    SEMANTIC = "semantic"
    POLICY = "policy"
    MEMORY = "memory"


TOOL_FOR_FAMILY = {
    RetrievalFamily.STRUCTURED: "CRD-TOOL-001",
    RetrievalFamily.GRAPH: "CRD-TOOL-002",
    RetrievalFamily.SEMANTIC: "CRD-TOOL-003",
    RetrievalFamily.POLICY: "CRD-TOOL-004",
    RetrievalFamily.MEMORY: "CRD-TOOL-003",
}

NEED_CATALOG: dict[str, RetrievalFamily] = {
    "requested_limit": RetrievalFamily.STRUCTURED,
    "current_exposure": RetrievalFamily.STRUCTURED,
    "source_health": RetrievalFamily.STRUCTURED,
    "bank_inflows": RetrievalFamily.STRUCTURED,
    "tax_turnover": RetrievalFamily.STRUCTURED,
    "numeric_current_facts": RetrievalFamily.STRUCTURED,
    "ownership": RetrievalFamily.GRAPH,
    "guarantor": RetrievalFamily.GRAPH,
    "exposure_relationship": RetrievalFamily.GRAPH,
    "supporting_narrative": RetrievalFamily.SEMANTIC,
    "historical_narrative": RetrievalFamily.SEMANTIC,
    "similar_memo": RetrievalFamily.SEMANTIC,
    "active_policy": RetrievalFamily.POLICY,
    "authority_route": RetrievalFamily.POLICY,
    "prior_decision": RetrievalFamily.MEMORY,
}

QUESTION_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"active policy|authority route|credit.?authority|which policy|policy version|threshold", "active_policy"),
    (r"requested limit|current exposure|source health|inflow|turnover|numeric", "numeric_current_facts"),
    (r"guarantor|ownership|played by|exposure relationship", "guarantor"),
    (r"prior decision|historical outcome|authorized override", "prior_decision"),
    (r"similar|historical memo|narrative|interview note|former|superseded", "supporting_narrative"),
)

UNDERWRITE_NEEDS = (
    "requested_limit",
    "current_exposure",
    "bank_inflows",
    "tax_turnover",
    "source_health",
    "ownership",
    "guarantor",
    "exposure_relationship",
    "supporting_narrative",
    "active_policy",
    "authority_route",
)


class RetrievalAuthorityError(SemanticCollapseError):
    """Raised when a non-policy route is used as policy authority."""


class UnknownRetrievalNeed(SemanticCollapseError):
    """Raised when a need is not in the routing catalog."""


@dataclass(frozen=True)
class RetrievedFact:
    source_ref: str
    semantic_type: str
    value: Any
    authority: str
    freshness_state: str = "unknown"
    conflict_state: str = "none"
    controlling: bool = False
    untrusted: bool = False


@dataclass(frozen=True)
class RetrievalHop:
    family: RetrievalFamily
    tool: str
    need: str
    source_refs: tuple[str, ...]
    authority: str
    controlling: bool
    facts: tuple[RetrievedFact, ...] = ()

    def as_trace_row(self) -> dict[str, Any]:
        return {
            "family": self.family.value,
            "tool": self.tool,
            "need": self.need,
            "source_refs": list(self.source_refs),
            "authority": self.authority,
            "controlling": self.controlling,
        }


@dataclass
class RetrievalPlan:
    application_id: str
    actor_tenant: str
    hops: list[RetrievalHop] = field(default_factory=list)
    denied: str | None = None

    def hops_for(self, family: RetrievalFamily | str) -> list[RetrievalHop]:
        token = family.value if isinstance(family, RetrievalFamily) else family
        return [h for h in self.hops if h.family.value == token]

    def trace(self) -> list[dict[str, Any]]:
        return [h.as_trace_row() for h in self.hops]

    def controlling_policy_sources(self) -> list[str]:
        refs: list[str] = []
        for hop in self.hops:
            if hop.family is RetrievalFamily.POLICY and hop.controlling:
                refs.extend(hop.source_refs)
        return refs


def _csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _live_app(application_id: str) -> dict[str, str]:
    for row in _csv(EVIDENCE / "live_applications.csv"):
        if row["application_id"] == application_id:
            return row
    raise UnknownRetrievalNeed(f"unknown live application {application_id}")


def classify_need(need: str) -> RetrievalFamily:
    family = NEED_CATALOG.get(need)
    if family is None:
        raise UnknownRetrievalNeed(
            f"unknown retrieval need {need!r}; will not default to semantic or invent policy"
        )
    return family


def classify_question(question: str) -> list[str]:
    """Deterministic need list. Policy keywords keep a policy need even if narrative words appear."""
    text = (question or "").lower()
    needs: list[str] = []
    for pattern, need in QUESTION_PATTERNS:
        if re.search(pattern, text) and need not in needs:
            needs.append(need)
    if not needs:
        raise UnknownRetrievalNeed("question did not match a routed underwriting need")
    return needs


def retrieve_structured_state(
    application_id: str,
    need: str,
    *,
    as_of_time: str = WORKSHOP_RETRIEVAL_TIME,
    actor_tenant: str | None = None,
) -> tuple[RetrievedFact, ...]:
    app = _live_app(application_id)
    if actor_tenant is not None and actor_tenant != app["tenant_id"]:
        return ()
    pack = assemble_application_evidence(application_id, retrieval_time=as_of_time)
    facts: list[RetrievedFact] = []
    if need in {"requested_limit", "numeric_current_facts"}:
        facts.append(
            RetrievedFact(
                source_ref=f"live_applications.csv:{application_id}:requested_limit",
                semantic_type="RequestedLimit",
                value=int(app["requested_limit"]),
                authority="authoritative",
                freshness_state="fresh",
            )
        )
    if need in {"current_exposure", "numeric_current_facts"}:
        for fact in pack.facts_for("EXPOSURE"):
            facts.append(
                RetrievedFact(
                    source_ref=fact.provenance,
                    semantic_type=fact.semantic_type,
                    value=fact.value,
                    authority=fact.authority,
                    freshness_state=fact.freshness_state,
                    conflict_state=fact.conflict_state,
                )
            )
    if need in {"bank_inflows", "numeric_current_facts"}:
        for fact in pack.facts:
            if fact.semantic_type == "BANK_INFLOWS_12M":
                facts.append(
                    RetrievedFact(
                        source_ref=fact.provenance,
                        semantic_type=fact.semantic_type,
                        value=fact.value,
                        authority=fact.authority,
                        freshness_state=fact.freshness_state,
                        conflict_state=fact.conflict_state,
                    )
                )
    if need in {"tax_turnover", "numeric_current_facts"}:
        for fact in pack.facts:
            if fact.semantic_type == "TAX_DECLARED_TURNOVER":
                facts.append(
                    RetrievedFact(
                        source_ref=fact.provenance,
                        semantic_type=fact.semantic_type,
                        value=fact.value,
                        authority=fact.authority,
                        freshness_state=fact.freshness_state,
                        conflict_state=fact.conflict_state,
                    )
                )
    if need == "source_health":
        for row in _jsonl(EVIDENCE / "source_health_events.jsonl"):
            if row.get("application_id") != application_id:
                continue
            facts.append(
                RetrievedFact(
                    source_ref=row["health_event_id"],
                    semantic_type=f"SourceHealth.{row['source']}",
                    value=row["state"],
                    authority="authoritative",
                    freshness_state=(
                        "stale"
                        if row["state"] == "STALE"
                        else "unavailable"
                        if row["state"] == "UNAVAILABLE"
                        else "fresh"
                    ),
                )
            )
    return tuple(facts)


def retrieve_graph_relationships(
    application_id: str,
    need: str,
    *,
    actor_tenant: str,
    as_of_time: str = WORKSHOP_RETRIEVAL_TIME,
) -> tuple[RetrievedFact, ...]:
    graph = assemble_runtime_context(
        application_id, actor_tenant=actor_tenant, as_of_time=as_of_time
    )
    if not graph.nodes:
        return ()
    wanted = {
        "ownership": ("HAS_APPLICANT_ROLE", "PLAYED_BY"),
        "guarantor": ("MAY_HAVE_GUARANTOR", "PLAYED_BY"),
        "exposure_relationship": ("HAS_EXPOSURE",),
    }[need]
    facts: list[RetrievedFact] = []
    start = f"APP:{application_id}"
    for rel in wanted:
        for edge, node in traverse_connected_context(graph, start, rel):
            facts.append(
                RetrievedFact(
                    source_ref=node.provenance or node.node_id,
                    semantic_type=f"{edge.relationship}:{node.kind}",
                    value=node.label,
                    authority=node.authority,
                    freshness_state=node.freshness_state,
                    conflict_state=node.conflict_state,
                )
            )
            if rel != "PLAYED_BY":
                for nested_edge, nested in traverse_connected_context(graph, node.node_id, "PLAYED_BY"):
                    facts.append(
                        RetrievedFact(
                            source_ref=nested.provenance or nested.node_id,
                            semantic_type=f"{nested_edge.relationship}:{nested.kind}",
                            value=nested.attributes.get("party_kind") or nested.label,
                            authority=nested.authority,
                            freshness_state=nested.freshness_state,
                        )
                    )
    return tuple(facts)


def retrieve_narrative_evidence(
    application_id: str,
    query: str,
    *,
    actor_tenant: str,
) -> tuple[RetrievedFact, ...]:
    """Lexical stand-in for vector search. Hits are untrusted and never controlling."""
    tokens = {t for t in re.findall(r"[a-z0-9.]+", (query or "historical memo").lower()) if len(t) > 2}
    hits: list[tuple[int, RetrievedFact]] = []
    for memo in load_historical_memos():
        if memo.tenant_id != actor_tenant:
            continue
        body = set(re.findall(r"[a-z0-9.]+", memo.text.lower()))
        score = len(tokens & body)
        if score == 0 and not tokens:
            score = 1
        if score == 0:
            continue
        hits.append(
            (
                score,
                RetrievedFact(
                    source_ref=memo.narrative_id,
                    semantic_type="HistoricalMemo",
                    value=memo.text,
                    authority="non_authoritative",
                    controlling=False,
                    untrusted=True,
                ),
            )
        )
    app_docs = [
        row
        for row in _jsonl(EVIDENCE / "documents_received.jsonl")
        if row.get("application_id") == application_id and row.get("tenant_id") == actor_tenant
    ]
    for row in app_docs:
        excerpt = str(row.get("text_excerpt") or "")
        body = set(re.findall(r"[a-z0-9.]+", excerpt.lower()))
        score = len(tokens & body) or 1
        hits.append(
            (
                score,
                RetrievedFact(
                    source_ref=row["document_id"],
                    semantic_type="ApplicantDocument",
                    value=excerpt,
                    authority="non_authoritative",
                    controlling=False,
                    untrusted=True,
                ),
            )
        )
    hits.sort(key=lambda item: (-item[0], item[1].source_ref))
    return tuple(item[1] for item in hits[:5])


def retrieve_prior_decisions(*, actor_tenant: str) -> tuple[RetrievedFact, ...]:
    facts: list[RetrievedFact] = []
    for row in _jsonl(HISTORY / "historical_decisions.jsonl"):
        if row.get("tenant_id") != actor_tenant:
            continue
        facts.append(
            RetrievedFact(
                source_ref=row["decision_id"],
                semantic_type="HistoricalDecision",
                value=row.get("human_final_decision"),
                authority="non_authoritative",
                controlling=False,
                untrusted=True,
            )
        )
    return tuple(facts[:5])


def retrieve_policy_rules(
    application_id: str,
    *,
    as_of_time: str = WORKSHOP_RETRIEVAL_TIME,
) -> tuple[RetrievedFact, ...]:
    retrieval = retrieve_active_policy(as_of_time)
    view = evaluate_application(application_id, as_of=as_of_time)
    facts: list[RetrievedFact] = []
    if retrieval.controlling is not None:
        facts.append(
            RetrievedFact(
                source_ref=retrieval.controlling.source_path,
                semantic_type="Policy",
                value=retrieval.controlling.version,
                authority="authoritative",
                controlling=True,
            )
        )
    if view.engine is not None:
        facts.append(
            RetrievedFact(
                source_ref=f"policy_engine_results.jsonl:{application_id}",
                semantic_type="PolicyEvaluation",
                value={
                    "result": view.engine.result,
                    "required_human_role": view.engine.required_human_role,
                    "triggered_rule_ids": list(view.engine.triggered_rule_ids),
                },
                authority="authoritative",
                controlling=True,
            )
        )
    return tuple(facts)


def use_semantic_as_policy(query: str) -> None:
    use_similarity_hit_as_authority(query)
    raise RetrievalAuthorityError("semantic retrieval cannot override deterministic policy")


def fuse_plan(plan: RetrievalPlan) -> RetrievalPlan:
    semantic_controlling = [
        h for h in plan.hops if h.family in {RetrievalFamily.SEMANTIC, RetrievalFamily.MEMORY} and h.controlling
    ]
    if semantic_controlling:
        raise RetrievalAuthorityError("vector/memory hop marked controlling; policy fusion forbids this")
    policy_hops = [h for h in plan.hops if h.family is RetrievalFamily.POLICY]
    if policy_hops and not any(h.controlling for h in policy_hops):
        if plan.denied is None:
            raise RetrievalAuthorityError("policy hop present but not controlling")
    return plan


def route_need(
    application_id: str,
    need: str,
    *,
    actor_tenant: str | None = None,
    as_of_time: str = WORKSHOP_RETRIEVAL_TIME,
    query: str | None = None,
) -> RetrievalHop:
    family = classify_need(need)
    app = _live_app(application_id)
    tenant = actor_tenant or app["tenant_id"]
    if tenant != app["tenant_id"]:
        return RetrievalHop(
            family=family,
            tool=TOOL_FOR_FAMILY[family],
            need=need,
            source_refs=(),
            authority="denied",
            controlling=False,
            facts=(),
        )

    if family is RetrievalFamily.STRUCTURED:
        facts = retrieve_structured_state(
            application_id, need, as_of_time=as_of_time, actor_tenant=tenant
        )
        return RetrievalHop(
            family=family,
            tool=TOOL_FOR_FAMILY[family],
            need=need,
            source_refs=tuple(f.source_ref for f in facts),
            authority="authoritative",
            controlling=False,
            facts=facts,
        )
    if family is RetrievalFamily.GRAPH:
        facts = retrieve_graph_relationships(
            application_id, need, actor_tenant=tenant, as_of_time=as_of_time
        )
        return RetrievalHop(
            family=family,
            tool=TOOL_FOR_FAMILY[family],
            need=need,
            source_refs=tuple(f.source_ref for f in facts),
            authority="authoritative",
            controlling=False,
            facts=facts,
        )
    if family is RetrievalFamily.SEMANTIC:
        facts = retrieve_narrative_evidence(
            application_id, query or need, actor_tenant=tenant
        )
        return RetrievalHop(
            family=family,
            tool=TOOL_FOR_FAMILY[family],
            need=need,
            source_refs=tuple(f.source_ref for f in facts),
            authority="non_authoritative",
            controlling=False,
            facts=facts,
        )
    if family is RetrievalFamily.MEMORY:
        facts = retrieve_prior_decisions(actor_tenant=tenant)
        return RetrievalHop(
            family=family,
            tool=TOOL_FOR_FAMILY[family],
            need=need,
            source_refs=tuple(f.source_ref for f in facts),
            authority="non_authoritative",
            controlling=False,
            facts=facts,
        )
    facts = retrieve_policy_rules(application_id, as_of_time=as_of_time)
    return RetrievalHop(
        family=family,
        tool=TOOL_FOR_FAMILY[family],
        need=need,
        source_refs=tuple(f.source_ref for f in facts),
        authority="authoritative",
        controlling=any(f.controlling for f in facts),
        facts=facts,
    )


def route_needs(
    application_id: str,
    needs: Iterable[str],
    *,
    actor_tenant: str | None = None,
    as_of_time: str = WORKSHOP_RETRIEVAL_TIME,
    query: str | None = None,
) -> RetrievalPlan:
    app = _live_app(application_id)
    tenant = actor_tenant or app["tenant_id"]
    plan = RetrievalPlan(application_id=application_id, actor_tenant=tenant)
    if tenant != app["tenant_id"]:
        plan.denied = "CROSS_TENANT"
        return plan
    for need in needs:
        plan.hops.append(
            route_need(
                application_id,
                need,
                actor_tenant=tenant,
                as_of_time=as_of_time,
                query=query,
            )
        )
    return fuse_plan(plan)


def route_underwriting(
    application_id: str,
    *,
    actor_tenant: str | None = None,
    as_of_time: str = WORKSHOP_RETRIEVAL_TIME,
) -> RetrievalPlan:
    return route_needs(application_id, UNDERWRITE_NEEDS, actor_tenant=actor_tenant, as_of_time=as_of_time)


def route_question(
    application_id: str,
    question: str,
    *,
    actor_tenant: str | None = None,
    as_of_time: str = WORKSHOP_RETRIEVAL_TIME,
) -> RetrievalPlan:
    needs = classify_question(question)
    return route_needs(
        application_id,
        needs,
        actor_tenant=actor_tenant,
        as_of_time=as_of_time,
        query=question,
    )
