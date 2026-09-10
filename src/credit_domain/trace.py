"""CRD-FR-009 / CRD-DATA-003 / CRD-TOOL-008 reconstructable underwriting trace.

Observable evidence, routes, versions, recommendation, human action and
outcome. No hidden chain-of-thought. Generated explanation is not policy.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from .authority import handoff_recommendation, record_human_decision
from .context import assemble_runtime_context
from .degraded import assess_degraded_mode
from .evidence import MATERIAL_RATIO_HIGH, MATERIAL_RATIO_LOW, assemble_application_evidence
from .identity import resolve_application_identity
from .model import HumanDecision, Recommendation, SemanticCollapseError
from .policy import ACTIVE_VERSION, evaluate_application, retrieve_active_policy
from .retrieval import RetrievalFamily, route_underwriting
from .security import evaluate_feasibility_or_safety

WORKSHOP_AS_OF = "2026-09-15T10:00:00+05:30"
SEMANTIC_MODEL_VERSION = "CRD-DATA-004"
ONTOLOGY_REF = "specs/05_data_contracts/DOMAIN_MODEL.md"
RETRIEVAL_POLICY_REF = "CRD-DATA-009"
ENGINE_SOURCE = "policy_engine_results.jsonl"
FORBIDDEN_TRACE_KEYS = frozenset(
    {
        "chain_of_thought",
        "hidden_chain_of_thought",
        "cot",
        "hidden_reasoning",
        "private_thoughts",
        "model_thoughts",
        "scratchpad",
    }
)
REQUIRED_TRACE_FIELDS = (
    "source_evidence",
    "versions",
    "consent_purpose",
    "retrieval_route",
    "financial_calculations",
    "policy_version",
    "exceptions",
    "recommendation",
    "authority_required",
    "human_action",
    "final_outcome",
)
_INVENTED_POLICY_RE = re.compile(
    r"(exception\s+(?:applies|criteria)|approve\s+(?:below|under|if)|"
    r"threshold|cut[- ]?off|policy\s+says)",
    re.I,
)


class TraceIntegrityError(SemanticCollapseError):
    """Raised when a trace hides CoT, invents policy, or treats a recommendation as a decision."""


@dataclass(frozen=True)
class EvidenceRef:
    evidence_id: str
    source: str
    record_ref: str
    version: str
    freshness_state: str
    authority: str
    consent_status: str
    purpose: str
    semantic_type: str
    value: Any


@dataclass(frozen=True)
class FinancialCalculation:
    name: str
    value: Any
    source_refs: tuple[str, ...]
    derivation: str
    is_policy_threshold: bool = False


@dataclass
class UnderwritingTrace:
    trace_id: str
    application_id: str
    task: str
    actor_role: str
    actor_tenant: str
    context_snapshot_id: str
    as_of_time: str
    source_evidence: list[EvidenceRef]
    versions: dict[str, str]
    consent_purpose: list[dict[str, str]]
    retrieval_route: list[dict[str, Any]]
    financial_calculations: list[FinancialCalculation]
    policy_version: str
    policy_evidence: list[dict[str, str]]
    policy_checks: list[dict[str, str]]
    exceptions: list[dict[str, str]]
    recommendation: dict[str, Any]
    authority_required: str
    human_action: dict[str, Any]
    final_outcome: dict[str, Any]
    concise_rationale: str
    tool_calls: list[dict[str, str]]
    uncertainty_or_abstention: str
    denied: str | None = None
    evaluation_flags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "trace_id": self.trace_id,
            "application_id": self.application_id,
            "task": self.task,
            "actor": {"role": self.actor_role, "tenant": self.actor_tenant},
            "context_snapshot": {
                "context_id": self.context_snapshot_id,
                "as_of_time": self.as_of_time,
            },
            "source_evidence": [item.__dict__ for item in self.source_evidence],
            "versions": dict(self.versions),
            "consent_purpose": list(self.consent_purpose),
            "retrieval_route": list(self.retrieval_route),
            "financial_calculations": [item.__dict__ for item in self.financial_calculations],
            "policy_version": self.policy_version,
            "policy_evidence": list(self.policy_evidence),
            "policy_checks": list(self.policy_checks),
            "exceptions": list(self.exceptions),
            "recommendation": dict(self.recommendation),
            "authority_required": self.authority_required,
            "human_action": dict(self.human_action),
            "final_outcome": dict(self.final_outcome),
            "concise_rationale": self.concise_rationale,
            "tool_calls": list(self.tool_calls),
            "uncertainty_or_abstention": self.uncertainty_or_abstention,
            "denied": self.denied,
            "evaluation_flags": list(self.evaluation_flags),
        }
        _reject_hidden_cot(payload)
        return payload

    def as_human_decision(self) -> HumanDecision:
        raise TraceIntegrityError("underwriting trace is not a HumanDecision")

    def use_generated_explanation_as_policy(self, text: str) -> None:
        """AT-16 / CRD-AC-014: generated text cannot become policy evidence."""
        raise TraceIntegrityError(
            "generated explanation cannot substitute for actual policy evidence: "
            f"{text[:80]}"
        )


def _reject_hidden_cot(payload: MappingLike | dict[str, Any]) -> None:
    stack: list[Any] = [payload]
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            for key, value in item.items():
                if key.lower() in FORBIDDEN_TRACE_KEYS:
                    raise TraceIntegrityError(
                        f"hidden chain-of-thought field {key!r} is not permitted (AT-17)"
                    )
                stack.append(value)
        elif isinstance(item, (list, tuple)):
            stack.extend(item)


# MappingLike used only as a type hint alias for the recursive walker.
MappingLike = dict


def _fact(pack, semantic_type: str):
    matches = [f for f in pack.facts if f.semantic_type == semantic_type]
    return matches[0] if matches else None


def _financials(pack) -> list[FinancialCalculation]:
    rows: list[FinancialCalculation] = []
    limit = _fact(pack, "RequestedLimit")
    bank = _fact(pack, "BANK_INFLOWS_12M")
    tax = _fact(pack, "TAX_DECLARED_TURNOVER")
    exposure = _fact(pack, "INTERNAL_EXISTING_EXPOSURE")
    if limit is not None:
        rows.append(
            FinancialCalculation(
                "requested_limit",
                limit.value,
                (limit.evidence_id,),
                "source_fact",
            )
        )
    if bank is not None:
        rows.append(
            FinancialCalculation(
                "bank_inflows_12m",
                bank.value,
                (bank.evidence_id,),
                "source_fact",
            )
        )
    if tax is not None:
        rows.append(
            FinancialCalculation(
                "tax_declared_turnover",
                tax.value,
                (tax.evidence_id,),
                "source_fact",
            )
        )
    if exposure is not None:
        rows.append(
            FinancialCalculation(
                "existing_exposure",
                exposure.value,
                (exposure.evidence_id,),
                "source_fact",
            )
        )
    if bank is not None and tax is not None and float(tax.value) != 0:
        ratio = float(bank.value) / float(tax.value)
        rows.append(
            FinancialCalculation(
                "bank_to_tax_visibility_ratio",
                ratio,
                (bank.evidence_id, tax.evidence_id),
                (
                    "workshop_visibility_ratio "
                    f"outside_[{MATERIAL_RATIO_LOW},{MATERIAL_RATIO_HIGH}]_is_conflict; "
                    "not_a_credit_threshold"
                ),
                is_policy_threshold=False,
            )
        )
    try:
        pack.blended_revenue()
        raise TraceIntegrityError("trace must not emit blended revenue")
    except SemanticCollapseError:
        pass
    return rows


def _policy_evidence(view) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    controlling = view.retrieval.controlling
    if controlling is not None:
        items.append(
            {
                "kind": "POLICY_BUNDLE",
                "version": controlling.version,
                "source_ref": controlling.source_path,
                "authority": "authoritative",
            }
        )
    if view.engine is not None:
        items.append(
            {
                "kind": "POLICY_ENGINE",
                "version": view.engine.policy_version,
                "source_ref": f"{ENGINE_SOURCE}:{view.application_id}",
                "authority": "authoritative",
            }
        )
    return items


def validate_trace(trace: UnderwritingTrace) -> None:
    payload = trace.to_dict()
    missing = [name for name in REQUIRED_TRACE_FIELDS if name not in payload]
    if missing:
        raise TraceIntegrityError(f"trace missing required fields: {missing}")
    if not trace.policy_evidence:
        raise TraceIntegrityError("trace has no actual policy evidence")
    kinds = {item["kind"] for item in trace.policy_evidence}
    if "POLICY_BUNDLE" not in kinds and trace.denied is None:
        raise TraceIntegrityError("controlling policy bundle is absent from policy_evidence")
    if _INVENTED_POLICY_RE.search(trace.concise_rationale) and "POL-EXC-07" in trace.concise_rationale:
        # Observable citation of the engine rule id is allowed; invented criteria are not.
        if re.search(r"POL-EXC-07.{0,80}(?:when|if|criteria)", trace.concise_rationale, re.I):
            raise TraceIntegrityError("rationale invents POL-EXC-07 criteria")
    if trace.recommendation.get("trust_class") != "ASSISTANCE":
        raise TraceIntegrityError("trace recommendation must remain ASSISTANCE")
    if trace.human_action.get("actor_role") == "AI_AGENT":
        raise TraceIntegrityError("AI_AGENT cannot occupy human_action")
    if any(calc.is_policy_threshold for calc in trace.financial_calculations):
        raise TraceIntegrityError("financial calculations must not invent policy thresholds")
    if trace.versions.get("policy_bundle") not in {ACTIVE_VERSION, "NONE"} and trace.denied is None:
        raise TraceIntegrityError("trace policy_bundle version is not the active catalog")


def record_decision_trace(
    application_id: str,
    *,
    actor_role: str = "CREDIT_ANALYST",
    actor_tenant: str = "TENANT-ALPHA",
    human_decision: HumanDecision | None = None,
    task: str = "UNDERWRITE_APPLICATION",
) -> UnderwritingTrace:
    """CRD-TOOL-008. Reconstructable, observable, no hidden CoT."""
    if isinstance(human_decision, Recommendation):
        raise TraceIntegrityError("Recommendation cannot be recorded as human_action")
    if actor_role == "AI_AGENT" and human_decision is not None:
        raise TraceIntegrityError("AI_AGENT cannot record a HumanDecision onto the trace")

    safety = evaluate_feasibility_or_safety(
        application_id, actor_tenant=actor_tenant, action="RETRIEVE"
    )
    if safety.effect == "DENY":
        trace = UnderwritingTrace(
            trace_id=f"TRACE:{application_id}",
            application_id=application_id,
            task=task,
            actor_role=actor_role,
            actor_tenant=actor_tenant,
            context_snapshot_id="",
            as_of_time=WORKSHOP_AS_OF,
            source_evidence=[],
            versions={
                "model": "NONE",
                "prompt": "NONE",
                "retrieval_policy": RETRIEVAL_POLICY_REF,
                "semantic_model": SEMANTIC_MODEL_VERSION,
                "ontology": ONTOLOGY_REF,
                "policy_bundle": ACTIVE_VERSION,
            },
            consent_purpose=[],
            retrieval_route=[],
            financial_calculations=[],
            policy_version=ACTIVE_VERSION,
            policy_evidence=[
                {
                    "kind": "POLICY_BUNDLE",
                    "version": ACTIVE_VERSION,
                    "source_ref": "evidence/02_documents/credit_underwriting_policy_v3_2.md",
                    "authority": "authoritative",
                }
            ],
            policy_checks=[
                {
                    "rule_id": safety.controlling_rule,
                    "result": "DENY",
                    "policy_version": ACTIVE_VERSION,
                }
            ],
            exceptions=[],
            recommendation={"stance": "ABSTAIN", "trust_class": "ASSISTANCE", "required_authority": None},
            authority_required="NONE",
            human_action={"status": "NOT_APPLICABLE", "reason": "cross-tenant retrieve denied"},
            final_outcome={"status": "UNKNOWN", "reason": "no application content retrieved"},
            concise_rationale="Tenant isolation denied retrieval before context assembly.",
            tool_calls=[{"tool": "CRD-TOOL-006", "result": "DENY"}],
            uncertainty_or_abstention="MANDATORY_ABSTENTION",
            denied="CROSS_TENANT",
            evaluation_flags=["AT-16", "AT-17"],
        )
        validate_trace(trace)
        return trace

    graph = assemble_runtime_context(application_id, actor_role=actor_role, actor_tenant=actor_tenant)
    pack = assemble_application_evidence(application_id)
    identity = resolve_application_identity(application_id)
    view = evaluate_application(application_id)
    plan = route_underwriting(application_id, actor_tenant=actor_tenant)
    rec = handoff_recommendation(application_id)
    degraded = assess_degraded_mode(application_id, actor_tenant=actor_tenant)
    retrieval = retrieve_active_policy()

    evidence = [
        EvidenceRef(
            evidence_id=fact.evidence_id,
            source=fact.source_system,
            record_ref=fact.source_record_id,
            version=fact.version,
            freshness_state=fact.freshness_state,
            authority=fact.authority,
            consent_status=fact.consent_status,
            purpose=fact.purpose,
            semantic_type=fact.semantic_type,
            value=fact.value,
        )
        for fact in pack.facts
    ]
    consent_purpose = [
        {
            "evidence_id": fact.evidence_id,
            "consent_status": fact.consent_status,
            "purpose": fact.purpose,
        }
        for fact in pack.facts
    ]
    route = [hop.as_trace_row() for hop in plan.hops]
    policy_hops = [hop for hop in plan.hops if hop.family is RetrievalFamily.POLICY and hop.controlling]
    if retrieval.controlling is None or not policy_hops:
        raise TraceIntegrityError("policy retrieval hop missing; generated text cannot fill it")

    engine_result = None if view.engine is None else view.engine.result
    rules = () if view.engine is None else view.engine.triggered_rule_ids
    checks = [
        {
            "rule_id": "CREDIT-POLICY-3.2",
            "result": engine_result or "ABSTAIN",
            "policy_version": view.retrieval.controlling_version or ACTIVE_VERSION,
        }
    ]
    for rule_id in rules:
        checks.append(
            {
                "rule_id": rule_id,
                "result": engine_result or "REQUIRES_HUMAN",
                "policy_version": view.retrieval.controlling_version or ACTIVE_VERSION,
            }
        )
    exceptions: list[dict[str, str]] = []
    if view.exception_class is not None:
        exceptions.append(
            {
                "exception_class": view.exception_class.value,
                "engine_result": engine_result or "",
                "triggered_rule_ids": ",".join(rules),
                "source_ref": f"{ENGINE_SOURCE}:{application_id}",
            }
        )

    if human_decision is None:
        human_action = {
            "status": "PENDING",
            "required_role": view.required_human_role,
            "actor_role": None,
            "reason": "final credit outcome requires an authorized HumanDecision",
        }
        outcome = {
            "status": "UNKNOWN",
            "reason": "HumanDecision not yet recorded",
        }
    else:
        if human_decision.application_id != application_id:
            raise TraceIntegrityError("human decision application_id does not match the trace")
        human_action = {
            "status": "RECORDED",
            "required_role": view.required_human_role,
            "actor_role": human_decision.actor_role,
            "reason": f"authorized HumanDecision {human_decision.outcome.value}",
            "outcome": human_decision.outcome.value,
            "policy_version": human_decision.policy_version,
        }
        outcome = {
            "status": human_decision.outcome.value,
            "actor_role": human_decision.actor_role,
            "policy_version": human_decision.policy_version,
        }

    rationale = (
        f"Identity {identity.state.value}; engine {engine_result} on {view.retrieval.controlling_version}; "
        f"required authority {view.required_human_role}; degraded {degraded.mode.value}. "
        "This rationale is observable assistance, not policy evidence."
    )
    trace = UnderwritingTrace(
        trace_id=f"TRACE:{application_id}",
        application_id=application_id,
        task=task,
        actor_role=actor_role,
        actor_tenant=actor_tenant,
        context_snapshot_id=graph.snapshot_id,
        as_of_time=graph.request.as_of_time,
        source_evidence=evidence,
        versions={
            "model": "NONE",
            "prompt": "NONE",
            "retrieval_policy": RETRIEVAL_POLICY_REF,
            "semantic_model": SEMANTIC_MODEL_VERSION,
            "ontology": ONTOLOGY_REF,
            "policy_bundle": view.retrieval.controlling_version or "NONE",
        },
        consent_purpose=consent_purpose,
        retrieval_route=route,
        financial_calculations=_financials(pack),
        policy_version=view.retrieval.controlling_version or "NONE",
        policy_evidence=_policy_evidence(view),
        policy_checks=checks,
        exceptions=exceptions,
        recommendation={
            "stance": rec.stance.value,
            "trust_class": "ASSISTANCE",
            "required_authority": rec.required_authority.role,
            "application_id": rec.application_id,
        },
        authority_required=rec.required_authority.role,
        human_action=human_action,
        final_outcome=outcome,
        concise_rationale=rationale,
        tool_calls=[
            {"tool": hop.tool, "result": hop.family.value}
            for hop in plan.hops
        ]
        + [{"tool": "CRD-TOOL-005", "result": "ASSIST"}, {"tool": "CRD-TOOL-007", "result": rec.stance.value}],
        uncertainty_or_abstention=degraded.mode.value,
        denied=None,
        evaluation_flags=["AT-16", "AT-17"],
    )
    validate_trace(trace)
    return trace


def attach_human_action(
    application_id: str,
    *,
    actor_role: str,
    outcome: str,
    actor_tenant: str = "TENANT-ALPHA",
) -> UnderwritingTrace:
    """Record an authorized human action onto a reconstructable trace."""
    decision = record_human_decision(application_id, actor_role=actor_role, outcome=outcome)
    return record_decision_trace(
        application_id,
        actor_role=actor_role,
        actor_tenant=actor_tenant,
        human_decision=decision,
    )
