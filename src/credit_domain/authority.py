"""CRD-FR-007 / CRD-FR-011 / CRD-DATA-010 credit authority gate.

AI may assist. It cannot approve, decline, condition, price, change a facility,
authorize large limits, approve exceptions or issue adverse determinations.
Required authority is the Policy Engine role, not the LOS assignment.
"""

from __future__ import annotations

from dataclasses import dataclass

from .model import (
    Authority,
    DecisionOutcome,
    HumanDecision,
    Recommendation,
    RecommendationStance,
    SemanticCollapseError,
)
from .policy import evaluate_application

CREDIT_AUTH_RULE = "CREDIT-AUTH-001"
ASSIST_ACTIONS = frozenset({"ASSIST", "SUMMARIZE", "REFER", "DRAFT_RECOMMENDATION"})
FINAL_ACTIONS = frozenset(
    {
        "APPROVE",
        "DECLINE",
        "CONDITION",
        "PRICE",
        "CHANGE_FACILITY",
        "AUTHORIZE_LARGE_LIMIT",
        "APPROVE_EXCEPTION",
        "ISSUE_ADVERSE",
    }
)
ROLE_RANK = {
    "AI_AGENT": 0,
    "RELATIONSHIP_MANAGER": 1,
    "CREDIT_ANALYST": 2,
    "PORTFOLIO_ANALYST": 2,
    "SENIOR_UNDERWRITER": 3,
    "CREDIT_AUTHORITY": 4,
}
SUFFICIENT_ROLES = {
    "CREDIT_ANALYST": frozenset({"CREDIT_ANALYST", "SENIOR_UNDERWRITER", "CREDIT_AUTHORITY"}),
    "SENIOR_UNDERWRITER": frozenset({"SENIOR_UNDERWRITER", "CREDIT_AUTHORITY"}),
    "CREDIT_AUTHORITY": frozenset({"CREDIT_AUTHORITY"}),
}


class AuthorityDenied(SemanticCollapseError):
    """Raised when an actor cannot exercise the requested credit authority."""


@dataclass(frozen=True)
class AuthorityCheck:
    effect: str
    application_id: str
    actor_role: str
    action: str
    required_human_role: str | None
    los_assigned_role: str | None
    controlling_rule: str
    policy_version: str | None
    engine_result: str | None
    reason: str

    @property
    def allowed(self) -> bool:
        return self.effect == "ALLOW"


def required_authority(application_id: str) -> Authority:
    view = evaluate_application(application_id)
    role = view.required_human_role or "CREDIT_ANALYST"
    if role == "AI_AGENT":
        raise AuthorityDenied("engine cannot require AI_AGENT as final credit authority")
    return Authority(role=role, final_credit_decision="YES")


def draft_recommendation(
    application_id: str,
    *,
    actor_role: str = "AI_AGENT",
    stance: RecommendationStance | None = None,
) -> Recommendation:
    """Advisory output. Always names the engine-required human role."""
    view = evaluate_application(application_id)
    authority = required_authority(application_id)
    resolved_stance = stance or view.stance or RecommendationStance.REFER
    if actor_role == "AI_AGENT" and resolved_stance in {
        RecommendationStance.PROPOSE_APPROVE,
        RecommendationStance.PROPOSE_DECLINE,
        RecommendationStance.PROPOSE_CONDITION,
    }:
        # Assistance may propose, but the stance is still advisory and must refer.
        resolved_stance = RecommendationStance.REFER
    rec = Recommendation(
        stance=resolved_stance,
        required_authority=authority,
        application_id=application_id,
    )
    if rec.required_authority.role == "AI_AGENT":
        raise AuthorityDenied("recommendation required_authority cannot be AI_AGENT")
    return rec


def role_is_sufficient(actor_role: str, required_role: str | None) -> bool:
    if not required_role:
        return actor_role != "AI_AGENT"
    allowed = SUFFICIENT_ROLES.get(required_role, frozenset({required_role}))
    return actor_role in allowed


def _action_rule(view, action: str) -> str:
    rules = () if view.engine is None else view.engine.triggered_rule_ids
    if action == "AUTHORIZE_LARGE_LIMIT" or "AUTH-LIMIT-01" in rules:
        if action in FINAL_ACTIONS:
            return "AUTH-LIMIT-01"
    if action == "APPROVE_EXCEPTION" or "POL-EXC-07" in rules:
        if action in {"APPROVE_EXCEPTION", "APPROVE"}:
            return "POL-EXC-07"
    if action == "ISSUE_ADVERSE" or (view.engine and view.engine.result == "ADVERSE_FACTORS_REVIEW"):
        if action in {"ISSUE_ADVERSE", "DECLINE"}:
            return "AUTH-ADVERSE-01"
    return CREDIT_AUTH_RULE


def check_access_and_authority(
    application_id: str,
    *,
    actor_role: str,
    action: str,
) -> AuthorityCheck:
    """CRD-TOOL-005. Deterministic; not prompt-text."""
    view = evaluate_application(application_id)
    required = view.required_human_role
    version = view.retrieval.controlling_version
    result = None if view.engine is None else view.engine.result
    rule = _action_rule(view, action)

    if action in ASSIST_ACTIONS:
        if actor_role == "AI_AGENT" or role_is_sufficient(actor_role, required) or actor_role in {
            "CREDIT_ANALYST",
            "SENIOR_UNDERWRITER",
            "CREDIT_AUTHORITY",
        }:
            return AuthorityCheck(
                effect="ALLOW",
                application_id=application_id,
                actor_role=actor_role,
                action=action,
                required_human_role=required,
                los_assigned_role=view.los_assigned_role,
                controlling_rule=CREDIT_AUTH_RULE,
                policy_version=version,
                engine_result=result,
                reason="assistance/refer/draft is permitted; not a final credit action",
            )
        return AuthorityCheck(
            effect="DENY",
            application_id=application_id,
            actor_role=actor_role,
            action=action,
            required_human_role=required,
            los_assigned_role=view.los_assigned_role,
            controlling_rule=CREDIT_AUTH_RULE,
            policy_version=version,
            engine_result=result,
            reason=f"{actor_role} cannot assist this application",
        )

    if action not in FINAL_ACTIONS:
        raise AuthorityDenied(f"unknown authority action {action!r}")

    if actor_role == "AI_AGENT":
        return AuthorityCheck(
            effect="DENY",
            application_id=application_id,
            actor_role=actor_role,
            action=action,
            required_human_role=required,
            los_assigned_role=view.los_assigned_role,
            controlling_rule=CREDIT_AUTH_RULE,
            policy_version=version,
            engine_result=result,
            reason="AI_AGENT cannot exercise final credit, exception, large-limit or adverse authority",
        )

    if not role_is_sufficient(actor_role, required):
        return AuthorityCheck(
            effect="DENY",
            application_id=application_id,
            actor_role=actor_role,
            action=action,
            required_human_role=required,
            los_assigned_role=view.los_assigned_role,
            controlling_rule=rule,
            policy_version=version,
            engine_result=result,
            reason=(
                f"{actor_role} is below required {required} "
                f"(LOS assigned {view.los_assigned_role} is not controlling)"
            ),
        )

    return AuthorityCheck(
        effect="ALLOW",
        application_id=application_id,
        actor_role=actor_role,
        action=action,
        required_human_role=required,
        los_assigned_role=view.los_assigned_role,
        controlling_rule=rule,
        policy_version=version,
        engine_result=result,
        reason=f"{actor_role} meets required {required}",
    )


def handoff_recommendation(
    application_id: str,
    *,
    actor_role: str = "AI_AGENT",
) -> Recommendation:
    """CRD-TOOL-007. Writes a recommendation only; never a HumanDecision."""
    check = check_access_and_authority(
        application_id, actor_role=actor_role, action="DRAFT_RECOMMENDATION"
    )
    if not check.allowed:
        raise AuthorityDenied(check.reason)
    return draft_recommendation(application_id, actor_role=actor_role)


def _outcome(value: DecisionOutcome | str) -> DecisionOutcome:
    if isinstance(value, DecisionOutcome):
        return value
    return DecisionOutcome(value)


def record_human_decision(
    application_id: str,
    *,
    actor_role: str,
    outcome: DecisionOutcome | str,
) -> HumanDecision:
    decided = _outcome(outcome)
    action = "ASSIST" if decided is DecisionOutcome.REFER else decided.value
    if decided is DecisionOutcome.ESCALATE:
        action = "ASSIST"
    check = check_access_and_authority(
        application_id, actor_role=actor_role, action=action
    )
    if not check.allowed:
        raise AuthorityDenied(check.reason)
    return HumanDecision(
        outcome=decided,
        actor_role=actor_role,
        policy_version=check.policy_version or "CREDIT-POLICY-3.2",
        application_id=application_id,
    )


def refuse_ai_final_action(application_id: str, action: str) -> AuthorityCheck:
    check = check_access_and_authority(application_id, actor_role="AI_AGENT", action=action)
    if check.allowed:
        raise AuthorityDenied(f"AI_AGENT must not be allowed to {action}")
    return check
