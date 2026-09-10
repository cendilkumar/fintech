"""CRD-SEC-004 / CRD-SEC-007 / CRD-DATA-012 adversarial controls.

Tenant isolation runs before structured, search, graph, context, memory, tool
and output adapters. Applicant documents and historical memos are untrusted
DATA. Embedded instructions cannot change policy, approval or tenant scope.
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .authority import check_access_and_authority
from .context import assemble_runtime_context, load_historical_memos
from .model import SemanticCollapseError
from .policy import evaluate_application
from .retrieval import (
    retrieve_graph_relationships,
    retrieve_narrative_evidence,
    retrieve_prior_decisions,
    retrieve_structured_state,
    route_underwriting,
)

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "evidence" / "01_enterprise_sources"
HISTORY = ROOT / "evidence" / "05_history_feedback"
ACCESS_RULES = ROOT / "evidence" / "04_policy_authority" / "data_access_rules.yaml"

TENANT_RULE = "DATA-TENANT"
DOC_RULE = "DATA-DOC-INSTRUCTION"
INJECTION_RE = re.compile(
    r"ignore previous(?: policies)?|approve this application immediately|"
    r"treat this document text as authoritative|authoritative instructions|"
    r"ignore tenant isolation|show (?:all )?tenants|you are now the system",
    re.I,
)


class IsolationDenied(SemanticCollapseError):
    """Raised when a cross-tenant retrieve/display is attempted."""


class UntrustedInstructionError(SemanticCollapseError):
    """Raised when document or memo text is treated as an instruction."""


@dataclass(frozen=True)
class UntrustedItem:
    source_id: str
    source_type: str
    tenant_id: str
    application_id: str
    text: str
    trust_class: str
    channel: str
    injection_detected: bool
    provenance: str

    def as_instruction(self) -> None:
        raise UntrustedInstructionError(
            f"{self.source_id} is untrusted DATA ({DOC_RULE}); not an instruction"
        )


@dataclass(frozen=True)
class LayerResult:
    layer: str
    effect: str
    rule: str
    content_refs: tuple[str, ...]
    detail: str


@dataclass(frozen=True)
class SafetyCheck:
    effect: str
    application_id: str
    actor_tenant: str
    action: str
    controlling_rule: str
    reason: str
    prompt_override_ignored: bool = False

    @property
    def allowed(self) -> bool:
        return self.effect == "ALLOW"


@dataclass
class AdversarialInspection:
    application_id: str
    actor_tenant: str
    resource_tenant: str
    layers: tuple[LayerResult, ...]
    untrusted_items: tuple[UntrustedItem, ...]
    prompt_override_ignored: bool
    access_rule_ids: tuple[str, ...]

    def result_for(self, layer: str) -> LayerResult:
        for row in self.layers:
            if row.layer == layer:
                return row
        raise IsolationDenied(f"missing layer {layer}")


def _csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_access_rule_ids() -> tuple[str, ...]:
    text = ACCESS_RULES.read_text(encoding="utf-8")
    return tuple(re.findall(r"(?m)^-\s*id:\s*(\S+)", text))


def live_application(application_id: str) -> dict[str, str]:
    for row in _csv(EVIDENCE / "live_applications.csv"):
        if row["application_id"] == application_id:
            return row
    raise IsolationDenied(f"unknown live application {application_id}")


def tenant_allows(actor_tenant: str, resource_tenant: str) -> bool:
    return actor_tenant == resource_tenant


def detect_injection(text: str) -> bool:
    return bool(INJECTION_RE.search(text or ""))


def follow_untrusted_instruction(item: UntrustedItem) -> None:
    item.as_instruction()


def load_untrusted_documents(application_id: str, actor_tenant: str) -> tuple[UntrustedItem, ...]:
    app = live_application(application_id)
    if not tenant_allows(actor_tenant, app["tenant_id"]):
        return ()
    items: list[UntrustedItem] = []
    for row in _jsonl(EVIDENCE / "documents_received.jsonl"):
        if row.get("application_id") != application_id:
            continue
        if row.get("tenant_id") != actor_tenant:
            continue
        text = str(row.get("text_excerpt") or "")
        items.append(
            UntrustedItem(
                source_id=row["document_id"],
                source_type="APPLICANT_DOCUMENT",
                tenant_id=row["tenant_id"],
                application_id=application_id,
                text=text,
                trust_class=row.get("trust_class") or "UNTRUSTED_CONTENT",
                channel="DATA",
                injection_detected=detect_injection(text),
                provenance=f"documents_received.jsonl:{row['document_id']}",
            )
        )
    return tuple(items)


def load_untrusted_memos(actor_tenant: str) -> tuple[UntrustedItem, ...]:
    items: list[UntrustedItem] = []
    for memo in load_historical_memos():
        if memo.tenant_id != actor_tenant:
            continue
        items.append(
            UntrustedItem(
                source_id=memo.narrative_id,
                source_type="HISTORICAL_MEMO",
                tenant_id=memo.tenant_id,
                application_id=memo.application_id,
                text=memo.text,
                trust_class="UNTRUSTED_CONTENT",
                channel="DATA",
                injection_detected=detect_injection(memo.text),
                provenance=f"historical_case_narratives.jsonl:{memo.narrative_id}",
            )
        )
    return tuple(items)


def assemble_data_payload(application_id: str, actor_tenant: str) -> tuple[UntrustedItem, ...]:
    """Prompt-assembly channel: documents and memos are DATA only."""
    return load_untrusted_documents(application_id, actor_tenant) + load_untrusted_memos(actor_tenant)


def foreign_tenant_markers(actor_tenant: str) -> frozenset[str]:
    markers: set[str] = set()
    for row in _csv(EVIDENCE / "live_applications.csv"):
        if row["tenant_id"] == actor_tenant:
            continue
        markers.add(row["application_id"])
        markers.add(row["applicant_name"])
    for row in _csv(EVIDENCE / "application_parties.csv"):
        if row["tenant_id"] == actor_tenant:
            continue
        markers.add(row["party_id"])
        markers.add(row["display_name"])
    for row in _jsonl(EVIDENCE / "documents_received.jsonl"):
        if row.get("tenant_id") == actor_tenant:
            continue
        markers.add(str(row["document_id"]))
    for row in _jsonl(EVIDENCE / "bank_financial_summaries.jsonl"):
        if row.get("tenant_id") == actor_tenant:
            continue
        markers.add(str(row["bank_summary_id"]))
    for row in _jsonl(EVIDENCE / "bureau_reports.jsonl"):
        if row.get("tenant_id") == actor_tenant:
            continue
        markers.add(str(row["bureau_report_id"]))
    for row in _jsonl(EVIDENCE / "tax_gst_records.jsonl"):
        if row.get("tenant_id") == actor_tenant:
            continue
        markers.add(str(row["tax_record_id"]))
    for row in _csv(EVIDENCE / "exposure_records.csv"):
        if row["tenant_id"] == actor_tenant:
            continue
        markers.add(row["exposure_id"])
    for memo in load_historical_memos():
        if memo.tenant_id == actor_tenant:
            continue
        markers.add(memo.narrative_id)
        markers.add(memo.application_id)
    for row in _jsonl(HISTORY / "historical_decisions.jsonl"):
        if row.get("tenant_id") == actor_tenant:
            continue
        markers.add(str(row["decision_id"]))
        markers.add(str(row["application_id"]))
    return frozenset(m for m in markers if m)


def scan_output_for_cross_tenant(text: str, actor_tenant: str) -> tuple[str, ...]:
    found: list[str] = []
    body = text or ""
    for marker in sorted(foreign_tenant_markers(actor_tenant), key=len, reverse=True):
        if marker and marker in body:
            found.append(marker)
    return tuple(found)


def evaluate_feasibility_or_safety(
    application_id: str,
    *,
    actor_tenant: str,
    action: str,
    prompt_override: str | None = None,
) -> SafetyCheck:
    """CRD-TOOL-006. Deterministic; prompt text cannot change the effect."""
    app = live_application(application_id)
    ignored = bool(prompt_override)
    if action == "FOLLOW_DOCUMENT_INSTRUCTION":
        return SafetyCheck(
            effect="DENY",
            application_id=application_id,
            actor_tenant=actor_tenant,
            action=action,
            controlling_rule=DOC_RULE,
            reason="applicant documents and historical memos are DATA, not instructions",
            prompt_override_ignored=ignored,
        )
    if not tenant_allows(actor_tenant, app["tenant_id"]):
        return SafetyCheck(
            effect="DENY",
            application_id=application_id,
            actor_tenant=actor_tenant,
            action=action,
            controlling_rule=TENANT_RULE,
            reason=f"{actor_tenant} cannot access {app['tenant_id']} resource {application_id}",
            prompt_override_ignored=ignored,
        )
    if action in {"RETRIEVE", "DISPLAY", "ASSEMBLE_CONTEXT", "SEARCH"}:
        return SafetyCheck(
            effect="ALLOW",
            application_id=application_id,
            actor_tenant=actor_tenant,
            action=action,
            controlling_rule=TENANT_RULE,
            reason="same-tenant retrieve/display permitted after DATA-TENANT filter",
            prompt_override_ignored=ignored,
        )
    raise IsolationDenied(f"unknown safety action {action}")


def inspect_retrieval_layers(
    application_id: str,
    actor_tenant: str,
    *,
    prompt_override: str | None = None,
) -> AdversarialInspection:
    """Run tenant/injection filters before every adapter. Prompt text is ignored."""
    app = live_application(application_id)
    denied = not tenant_allows(actor_tenant, app["tenant_id"])
    tool = evaluate_feasibility_or_safety(
        application_id,
        actor_tenant=actor_tenant,
        action="RETRIEVE",
        prompt_override=prompt_override,
    )

    structured = retrieve_structured_state(
        application_id, "numeric_current_facts", actor_tenant=actor_tenant
    )
    search = retrieve_narrative_evidence(
        application_id, prompt_override or "supporting narrative", actor_tenant=actor_tenant
    )
    graph = retrieve_graph_relationships(
        application_id, "ownership", actor_tenant=actor_tenant
    )
    context = assemble_runtime_context(application_id, actor_tenant=actor_tenant)
    memory = retrieve_prior_decisions(actor_tenant=actor_tenant)
    plan = route_underwriting(application_id, actor_tenant=actor_tenant)

    structured_refs = tuple(f.source_ref for f in structured)
    search_refs = tuple(f.source_ref for f in search)
    graph_refs = tuple(f.source_ref for f in graph)
    context_refs = tuple(n.node_id for n in context.nodes)
    memory_refs = tuple(
        f.source_ref
        for f in memory
        if not scan_output_for_cross_tenant(f.source_ref, actor_tenant)
    )
    if denied:
        if structured or graph or context.nodes or plan.hops:
            raise IsolationDenied("adapter returned foreign-tenant content before DATA-TENANT")
        if plan.denied != "CROSS_TENANT":
            raise IsolationDenied("cross-tenant plan must deny before hops")
        structured_refs = graph_refs = context_refs = search_refs = ()
        for fact in search:
            leaked = scan_output_for_cross_tenant(str(fact.value), actor_tenant)
            leaked += scan_output_for_cross_tenant(fact.source_ref, actor_tenant)
            if leaked:
                raise IsolationDenied(f"search leaked {leaked}")

    leak_probe = (
        f"{app['applicant_name']} {application_id} requested underwriting package"
        if denied
        else ""
    )
    output_hits = scan_output_for_cross_tenant(leak_probe, actor_tenant) if denied else ()

    layers = (
        LayerResult("structured", "DENY" if denied else "ALLOW", TENANT_RULE, structured_refs, "pre-retrieval DATA-TENANT filter"),
        LayerResult("search", "DENY" if denied else "ALLOW", TENANT_RULE, search_refs, "semantic/vector hits filtered by tenant before ranking"),
        LayerResult("graph", "DENY" if denied else "ALLOW", TENANT_RULE, graph_refs, "graph walk blocked before relationship hops"),
        LayerResult("context", "DENY" if denied else "ALLOW", TENANT_RULE, context_refs, "runtime context assembled only after tenant check"),
        LayerResult("memory", "ALLOW", TENANT_RULE, memory_refs, "historical decisions filtered by actor tenant"),
        LayerResult("tool", tool.effect, tool.controlling_rule, (), tool.reason),
        LayerResult("output", "DENY" if (denied or output_hits) else "ALLOW", TENANT_RULE, output_hits, "display scanned for foreign-tenant markers"),
    )
    return AdversarialInspection(
        application_id=application_id,
        actor_tenant=actor_tenant,
        resource_tenant=app["tenant_id"],
        layers=layers,
        untrusted_items=() if denied else assemble_data_payload(application_id, actor_tenant),
        prompt_override_ignored=bool(prompt_override),
        access_rule_ids=load_access_rule_ids(),
    )


def display_payload(application_id: str, actor_tenant: str) -> dict[str, Any]:
    check = evaluate_feasibility_or_safety(
        application_id, actor_tenant=actor_tenant, action="DISPLAY"
    )
    if check.effect == "DENY":
        return {
            "denied": "CROSS_TENANT",
            "rule": TENANT_RULE,
            "content": [],
            "application_id": None,
        }
    graph = assemble_runtime_context(application_id, actor_tenant=actor_tenant)
    return {
        "denied": None,
        "rule": TENANT_RULE,
        "content": [n.node_id for n in graph.nodes],
        "application_id": application_id,
    }


def policy_unaffected_by_document(application_id: str, actor_tenant: str) -> dict[str, Any]:
    docs = load_untrusted_documents(application_id, actor_tenant)
    view = evaluate_application(application_id)
    approve = check_access_and_authority(
        application_id, actor_role="AI_AGENT", action="APPROVE"
    )
    return {
        "engine_result": None if view.engine is None else view.engine.result,
        "policy_version": view.retrieval.controlling_version,
        "required_human_role": view.required_human_role,
        "ai_approve": approve.effect,
        "untrusted_document_ids": tuple(d.source_id for d in docs),
        "injection_document_ids": tuple(d.source_id for d in docs if d.injection_detected),
    }
