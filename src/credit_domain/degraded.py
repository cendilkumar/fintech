"""CRD-FR-008 / CRD-DATA-013 degraded underwriting assistance.

Four exclusive primary modes: continue, needs evidence, AI unavailable,
mandatory abstention. Stale bank stays visible and not current. Missing
bureau/bank facts are never invented. Manual underwriting survives AI outage.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Iterable

from .authority import check_access_and_authority, handoff_recommendation
from .context import assemble_runtime_context
from .evidence import assemble_application_evidence
from .model import RecommendationStance, SemanticCollapseError
from .policy import KNOWN_RULE_BINDINGS, evaluate_application
from .retrieval import retrieve_structured_state

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "evidence" / "01_enterprise_sources"
CONSTRAINTS = ROOT / "evidence" / "04_policy_authority" / "decision_constraints.yaml"

FALLBACK_RULE = "FALLBACK-001"
STALE_RULE = "STALE-001"
BANK_STALE_AFTER_DAYS = int(KNOWN_RULE_BINDINGS["DATA-FRESHNESS-BANK"]["days"])

CURRENT_BANK_RE = re.compile(
    r"\b(current\s+(?:bank|cashflow)|bank\s+feed\s+is\s+current|"
    r"fresh\s+(?:bank|inflows)|inflows\s+are\s+current)\b",
    re.I,
)
INVENTED_BUREAU_RE = re.compile(
    r"\b(score\s+band\s+[abc]|bureau\s+score|commercial\s+score|"
    r"invent(?:ed)?\s+bureau|assume(?:d)?\s+bureau)\b",
    re.I,
)
INVENTED_BANK_RE = re.compile(
    r"\b(invent(?:ed)?\s+bank|assume(?:d)?\s+(?:inflows|bank)|"
    r"fabricat(?:e|ed)\s+(?:bank|inflows))\b",
    re.I,
)
AI_ASSIST_CLAIM_RE = re.compile(
    r"\b(ai\s+(?:recommends|memo|assistance\s+(?:complete|available))|"
    r"generated\s+assistance\s+memo)\b",
    re.I,
)


class DegradedMode(str, Enum):
    DECISION_CAN_CONTINUE = "DECISION_CAN_CONTINUE"
    REQUIRES_ADDITIONAL_EVIDENCE = "REQUIRES_ADDITIONAL_EVIDENCE"
    AI_ASSISTANCE_UNAVAILABLE = "AI_ASSISTANCE_UNAVAILABLE"
    MANDATORY_ABSTENTION = "MANDATORY_ABSTENTION"


class DegradedModeError(SemanticCollapseError):
    """Raised when generated text hides degradation or invents missing facts."""


@dataclass(frozen=True)
class SourceHealth:
    source: str
    state: str
    detail: str


@dataclass(frozen=True)
class ManualUnderwritingView:
    application_id: str
    policy_version: str | None
    engine_result: str | None
    required_human_role: str | None
    triggered_rule_ids: tuple[str, ...]
    source_health: tuple[SourceHealth, ...]
    fallback_rule: str
    executable: bool


@dataclass
class DegradedAssessment:
    application_id: str
    mode: DegradedMode
    bank_freshness: str | None
    bank_presented_as_current: bool
    bank_refresh_requested: bool
    bureau_available: bool
    bureau_value: Any
    ai_assist_available: bool
    ai_assistance_permitted: bool
    manual_underwriting_available: bool
    retrieval_outages: tuple[str, ...]
    exception_class: str | None
    engine_result: str | None
    required_human_role: str | None
    policy_version: str | None
    controlling_rules: tuple[str, ...]
    notes: tuple[str, ...]

    def as_stance(self) -> RecommendationStance:
        if self.mode is DegradedMode.MANDATORY_ABSTENTION:
            return RecommendationStance.ABSTAIN
        return RecommendationStance.REFER


def _jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_fallback_rule() -> str:
    text = CONSTRAINTS.read_text(encoding="utf-8")
    if FALLBACK_RULE not in text:
        raise DegradedModeError(f"{FALLBACK_RULE} missing from decision_constraints.yaml")
    return FALLBACK_RULE


def source_health_for(application_id: str) -> tuple[SourceHealth, ...]:
    return tuple(
        SourceHealth(r["source"], r["state"], r.get("detail") or "")
        for r in _jsonl(EVIDENCE / "source_health_events.jsonl")
        if r.get("application_id") == application_id
    )


def _health(rows: Iterable[SourceHealth], source: str) -> SourceHealth | None:
    for row in rows:
        if row.source == source:
            return row
    return None


def assess_degraded_mode(
    application_id: str,
    *,
    actor_tenant: str = "TENANT-ALPHA",
    retrieval_outages: Iterable[str] = (),
) -> DegradedAssessment:
    outages = tuple(sorted({item.lower() for item in retrieval_outages}))
    structured_out = "structured" in outages
    policy_out = "policy" in outages
    view = evaluate_application(application_id)
    health = source_health_for(application_id)
    bank_health = _health(health, "BANK_DATA")
    bureau_health = _health(health, "CREDIT_BUREAU")
    ai_health = _health(health, "AI_ASSIST")

    pack = None if structured_out else assemble_application_evidence(application_id)
    graph = None if structured_out else assemble_runtime_context(
        application_id, actor_tenant=actor_tenant
    )
    bank_nodes = [] if graph is None else graph.nodes_of("BankEvidence")
    bank_freshness = bank_nodes[0].freshness_state if bank_nodes else (
        None if bank_health is None else bank_health.state.lower()
    )
    stale = bank_freshness == "stale" or (bank_health is not None and bank_health.state == "STALE")
    bank_current = bool(bank_nodes) and all(n.presented_as_current for n in bank_nodes) and not stale

    bureau_fact = None
    if pack is not None:
        bureau_facts = [f for f in pack.facts if str(f.semantic_type).startswith("BureauRecord")]
        bureau_fact = bureau_facts[0] if bureau_facts else None
    bureau_unavailable = (
        structured_out
        or (bureau_health is not None and bureau_health.state == "UNAVAILABLE")
        or (bureau_fact is not None and bureau_fact.freshness_state == "unavailable")
        or (pack is not None and bureau_fact is None)
    )
    insufficient = view.engine is not None and view.engine.result == "INSUFFICIENT_EVIDENCE"
    ai_down = ai_health is not None and ai_health.state == "UNAVAILABLE"

    if structured_out or policy_out:
        mode = DegradedMode.MANDATORY_ABSTENTION
    elif bureau_unavailable or insufficient:
        mode = DegradedMode.REQUIRES_ADDITIONAL_EVIDENCE
    elif ai_down:
        mode = DegradedMode.AI_ASSISTANCE_UNAVAILABLE
    else:
        mode = DegradedMode.DECISION_CAN_CONTINUE

    engine_result = None if view.engine is None else view.engine.result
    rules = () if view.engine is None else view.engine.triggered_rule_ids
    notes = [
        f"mode={mode.value}",
        f"engine={engine_result}",
        STALE_RULE if stale else "bank_not_stale",
        FALLBACK_RULE if ai_down else "ai_assist_available",
    ]
    if stale:
        notes.append(f"DATA-FRESHNESS-BANK stale_after_days={BANK_STALE_AFTER_DAYS}")
        notes.append("engine PASS does not present stale bank as current")
    if bureau_unavailable:
        notes.append("bureau unavailable; do not invent score or band")
    if "semantic" in outages or "graph" in outages:
        notes.append("non-authoritative retrieval degraded; structured/policy remain")

    return DegradedAssessment(
        application_id=application_id,
        mode=mode,
        bank_freshness=bank_freshness,
        bank_presented_as_current=bank_current,
        bank_refresh_requested=stale,
        bureau_available=not bureau_unavailable,
        bureau_value=None if bureau_fact is None or bureau_unavailable else bureau_fact.value,
        ai_assist_available=not ai_down,
        ai_assistance_permitted=mode is DegradedMode.DECISION_CAN_CONTINUE,
        manual_underwriting_available=True,
        retrieval_outages=outages,
        exception_class=None if view.exception_class is None else view.exception_class.value,
        engine_result=engine_result,
        required_human_role=view.required_human_role,
        policy_version=view.retrieval.controlling_version,
        controlling_rules=rules,
        notes=tuple(notes),
    )


def emit_ai_assistance(assessment: DegradedAssessment) -> dict[str, str]:
    if not assessment.ai_assistance_permitted:
        rule = FALLBACK_RULE if not assessment.ai_assist_available else STALE_RULE
        if assessment.mode is DegradedMode.REQUIRES_ADDITIONAL_EVIDENCE:
            rule = "DATA-BUREAU-REQ"
        if assessment.mode is DegradedMode.MANDATORY_ABSTENTION:
            rule = STALE_RULE
        return {
            "effect": "DENY",
            "rule": rule,
            "reason": f"AI assistance blocked in mode {assessment.mode.value}",
        }
    return {
        "effect": "ALLOW",
        "rule": STALE_RULE,
        "reason": "assistance permitted; stale/unavailable facts stay explicit",
    }


def manual_underwriting_view(application_id: str) -> ManualUnderwritingView:
    view = evaluate_application(application_id)
    return ManualUnderwritingView(
        application_id=application_id,
        policy_version=view.retrieval.controlling_version,
        engine_result=None if view.engine is None else view.engine.result,
        required_human_role=view.required_human_role,
        triggered_rule_ids=() if view.engine is None else view.engine.triggered_rule_ids,
        source_health=source_health_for(application_id),
        fallback_rule=load_fallback_rule(),
        executable=True,
    )


def check_ai_assist_action(application_id: str) -> dict[str, str]:
    assessment = assess_degraded_mode(application_id)
    emitted = emit_ai_assistance(assessment)
    if emitted["effect"] == "DENY":
        return emitted
    check = check_access_and_authority(
        application_id, actor_role="AI_AGENT", action="ASSIST"
    )
    return {
        "effect": check.effect,
        "rule": check.controlling_rule,
        "reason": check.reason,
    }


def scan_generated_degraded_claims(text: str, assessment: DegradedAssessment) -> None:
    if assessment.bank_freshness == "stale" and CURRENT_BANK_RE.search(text):
        raise DegradedModeError("generated text presents stale bank as current (CRD-AC-005)")
    if not assessment.bureau_available and INVENTED_BUREAU_RE.search(text):
        raise DegradedModeError("generated text invents unavailable bureau evidence (CRD-AC-006)")
    if not assessment.ai_assist_available and AI_ASSIST_CLAIM_RE.search(text):
        raise DegradedModeError("generated text fabricates AI assistance during outage (CRD-AC-010)")
    if assessment.mode is DegradedMode.MANDATORY_ABSTENTION and (
        INVENTED_BANK_RE.search(text) or INVENTED_BUREAU_RE.search(text)
    ):
        raise DegradedModeError("generated text invents bank/bureau during retrieval outage")


def refuse_fabricated_bureau(assessment: DegradedAssessment, value: Any) -> None:
    if not assessment.bureau_available and value is not None:
        raise DegradedModeError("cannot fill unavailable bureau value (CRD-AC-006)")


def structured_facts_or_empty(application_id: str, need: str, *, assessment: DegradedAssessment):
    if "structured" in assessment.retrieval_outages:
        return ()
    return retrieve_structured_state(application_id, need)


def continue_with_handoff(application_id: str):
    assessment = assess_degraded_mode(application_id)
    rec = handoff_recommendation(application_id)
    return assessment, rec, manual_underwriting_view(application_id)
