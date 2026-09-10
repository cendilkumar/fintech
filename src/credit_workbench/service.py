"""Workbench display plane for CRD-FR-001–011 / CRD-AC-001–015 / G-UI-01.

Screens display deterministic gates. They do not replace check_access_and_authority,
retrieve_active_policy, or tenant isolation.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from credit_domain.authority import (
    FINAL_ACTIONS,
    AuthorityDenied,
    check_access_and_authority,
    handoff_recommendation,
    record_human_decision,
)
from credit_domain.context import assemble_runtime_context
from credit_domain.degraded import assess_degraded_mode, manual_underwriting_view, source_health_for
from credit_domain.evals import INVENTED_THRESHOLD_PROBE
from credit_domain.evidence import assemble_application_evidence
from credit_domain.feedback import (
    FeedbackGovernanceError,
    PROTECTED_DESTINATIONS,
    apply_feedback_to_destination,
    capture_outcome_feedback,
)
from credit_domain.identity import resolve_application_identity
from credit_domain.memo import MemoAssistanceUnavailable, generate_credit_memo
from credit_domain.model import DecisionOutcome, HumanDecision, SemanticCollapseError
from credit_domain.persons import analyze_person_impact
from credit_domain.policy import (
    ACTIVE_VERSION,
    SUPERSEDED_VERSION,
    PolicyFidelityError,
    evaluate_application,
    load_live_application,
    retrieve_active_policy,
    scan_generated_policy_claims,
)
from credit_domain.retrieval import RetrievalFamily, route_underwriting
from credit_domain.security import (
    UntrustedInstructionError,
    display_payload,
    follow_untrusted_instruction,
    inspect_retrieval_layers,
    load_untrusted_documents,
    policy_unaffected_by_document,
)
from credit_domain.trace import (
    FORBIDDEN_TRACE_KEYS,
    REQUIRED_TRACE_FIELDS,
    attach_human_action,
    record_decision_trace,
)

from .flags import LOCKED_ON, PRE_MEMO_SCREENS, SCREENS, FeatureFlags
from .serialize import jsonable

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "evidence" / "01_enterprise_sources"
HISTORY = ROOT / "evidence" / "05_history_feedback"
GOLDEN_PATH = ROOT / "evidence" / "06_evaluations" / "golden_scenarios.json"

OPERATOR_CAVEATS = (
    "This is assistance, not a credit decision.",
    "CREDIT-POLICY-3.2 is the only active workshop policy. CREDIT-POLICY-2.9 is historical.",
    "Workshop fixture TAT is not the 30-minute business target.",
    "Contract GS-01–GS-15 PASS is not production PASS.",
    "Restricted fairness-eval attributes are not runtime decision features.",
)

MEMO_ROLES = frozenset({"CREDIT_ANALYST", "SENIOR_UNDERWRITER", "CREDIT_AUTHORITY"})
DECISION_ROLES = frozenset({"CREDIT_ANALYST", "SENIOR_UNDERWRITER", "CREDIT_AUTHORITY"})
FAIRNESS_ROLE = "RISK_COMPLIANCE_EVAL"
FAIRNESS_PURPOSE = "RISK_COMPLIANCE_EVAL"
RUNTIME_PURPOSE = "UNDERWRITING_RUNTIME"


def _csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_golden_scenarios() -> list[dict[str, Any]]:
    return json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))


def _err(exc: BaseException) -> dict[str, str]:
    return {"type": type(exc).__name__, "message": str(exc)}


class WorkbenchService:
    """Session-scoped display plane. Gates stay in credit_domain."""

    def __init__(self) -> None:
        self.flags = FeatureFlags()
        self.decisions: dict[str, dict[str, Any]] = {}
        self.feedback: dict[str, list[dict[str, Any]]] = {}
        self.traces: dict[str, dict[str, Any]] = {}

    def snapshot_flags(self) -> dict[str, Any]:
        return {
            "flags": self.flags.as_dict(),
            "locked_on": list(LOCKED_ON),
            "memo_visible": self.flags.memo_visible(),
            "pre_memo_screens": list(PRE_MEMO_SCREENS),
            "screens": list(SCREENS),
            "model": "NONE",
            "caveats": list(OPERATOR_CAVEATS),
        }

    def set_flags(self, updates: dict[str, bool]) -> dict[str, Any]:
        self.flags.apply(updates)
        return self.snapshot_flags()

    def catalog(self) -> dict[str, Any]:
        return {
            "organization": "NexLend SME Finance",
            "product": "SME Credit Underwriting Intelligence Workbench",
            "active_policy": ACTIVE_VERSION,
            "superseded_policy": SUPERSEDED_VERSION,
            "screens": list(SCREENS),
            "golden_scenarios": load_golden_scenarios(),
            "roles": [
                "RELATIONSHIP_MANAGER",
                "CREDIT_ANALYST",
                "SENIOR_UNDERWRITER",
                "CREDIT_AUTHORITY",
                "RISK_COMPLIANCE_EVAL",
                "PORTFOLIO_ANALYST",
            ],
            "tenants": ["TENANT-ALPHA", "TENANT-BETA"],
            "caveats": list(OPERATOR_CAVEATS),
            "flags": self.snapshot_flags(),
        }

    def control_tower(self, *, actor_tenant: str, actor_role: str) -> dict[str, Any]:
        rows = []
        for app in _csv(EVIDENCE / "live_applications.csv"):
            if app["tenant_id"] != actor_tenant:
                continue
            health = [
                {"source": item.source, "state": item.state, "detail": item.detail}
                for item in source_health_for(app["application_id"])
            ]
            view = evaluate_application(app["application_id"])
            rows.append(
                {
                    "application_id": app["application_id"],
                    "tenant_id": app["tenant_id"],
                    "visible": True,
                    "denied": None,
                    "scenario_hint": app.get("scenario_hint"),
                    "applicant_name": app["applicant_name"],
                    "applicant_type": app["applicant_type"],
                    "product": app["product"],
                    "requested_limit": int(app["requested_limit"]),
                    "status": app["status"],
                    "current_stage": app["current_stage"],
                    "assigned_role": app["assigned_role"],
                    "source_health": health,
                    "engine_result": None if view.engine is None else view.engine.result,
                    "required_human_role": view.required_human_role,
                    "exception_class": None
                    if view.exception_class is None
                    else view.exception_class.value,
                    "policy_version": view.retrieval.controlling_version,
                }
            )
        return {
            "screen": "control_tower",
            "actor_tenant": actor_tenant,
            "actor_role": actor_role,
            "applications": rows,
            "visible_count": sum(1 for row in rows if row["visible"]),
        }

    def case_dossier(
        self,
        application_id: str,
        *,
        actor_tenant: str,
        actor_role: str,
        purpose: str = RUNTIME_PURPOSE,
    ) -> dict[str, Any]:
        isolation = display_payload(application_id, actor_tenant)
        goldens = {row["application_id"]: row for row in load_golden_scenarios()}
        payload: dict[str, Any] = {
            "application_id": None if isolation.get("denied") else application_id,
            "actor_tenant": actor_tenant,
            "actor_role": actor_role,
            "purpose": purpose,
            "denied": isolation.get("denied"),
            "isolation": isolation,
            "scenario": goldens.get(application_id),
            "screens": {name: {"enabled": self.flags.screen_enabled(name)} for name in SCREENS},
            "flags": self.snapshot_flags(),
            "ai_final_approve_control": False,
            "model": "NONE",
        }
        if isolation.get("denied"):
            payload["screens"]["failure_simulation"] = self._failure_simulation(
                application_id, actor_tenant=actor_tenant, actor_role=actor_role, denied=True
            )
            payload["screens"]["hybrid_retrieval"] = self._retrieval_denied(
                application_id, actor_tenant
            )
            payload["screens"]["decision_trace"] = self._trace_payload(
                application_id, actor_role=actor_role, actor_tenant=actor_tenant
            )
            return payload

        app = load_live_application(application_id)
        payload["application"] = dict(app)
        payload["screens"]["application_context"] = self._application_context(
            application_id, actor_role=actor_role, actor_tenant=actor_tenant, purpose=purpose
        )
        payload["screens"]["evidence_reconciliation"] = self._evidence(application_id)
        payload["screens"]["context_graph"] = self._graph(
            application_id, actor_role=actor_role, actor_tenant=actor_tenant
        )
        payload["screens"]["hybrid_retrieval"] = self._retrieval(application_id, actor_tenant)
        payload["screens"]["policy_authority"] = self._policy(application_id, actor_role)
        payload["screens"]["human_decision"] = self._human_decision(application_id, actor_role)
        payload["screens"]["decision_trace"] = self._trace_payload(
            application_id, actor_role=actor_role, actor_tenant=actor_tenant
        )
        payload["screens"]["outcome_feedback"] = self._feedback_view(
            application_id, actor_role=actor_role, actor_tenant=actor_tenant
        )
        payload["screens"]["credit_memo"] = self._memo(application_id, actor_role=actor_role)
        payload["screens"]["fairness_eval"] = self._fairness(purpose=purpose, actor_role=actor_role)
        payload["screens"]["failure_simulation"] = self._failure_simulation(
            application_id, actor_tenant=actor_tenant, actor_role=actor_role, denied=False
        )
        return payload

    def _application_context(
        self,
        application_id: str,
        *,
        actor_role: str,
        actor_tenant: str,
        purpose: str,
    ) -> dict[str, Any]:
        app = load_live_application(application_id)
        parties = [
            row
            for row in _csv(EVIDENCE / "application_parties.csv")
            if row["application_id"] == application_id
        ]
        identity = resolve_application_identity(application_id)
        persons = analyze_person_impact(application_id)
        graph = assemble_runtime_context(
            application_id, actor_role=actor_role, actor_tenant=actor_tenant
        )
        restricted_in_runtime = any(item.reason_code == "RESTRICTED_ATTRIBUTE" for item in graph.excluded)
        return {
            "enabled": True,
            "application": app,
            "parties": parties,
            "identity": jsonable(identity),
            "identity_state": identity.state.value,
            "person_impact": jsonable(persons),
            "task": graph.request.task,
            "source_summary": graph.source_health,
            "excluded": jsonable(graph.excluded),
            "restricted_eval_excluded_from_runtime": restricted_in_runtime
            and persons.restricted_eval_excluded,
            "purpose": purpose,
            "sole_trader_distinct": any(p.get("party_type") == "SOLE_TRADER_BUSINESS" for p in parties),
        }

    def _evidence(self, application_id: str) -> dict[str, Any]:
        pack = assemble_application_evidence(application_id)
        facts = [jsonable(fact) for fact in pack.facts]
        by_source: dict[str, list[dict[str, Any]]] = {}
        for fact in facts:
            by_source.setdefault(str(fact["source_system"]), []).append(fact)
        return {
            "enabled": True,
            "facts": facts,
            "by_source": by_source,
            "conflicts": jsonable(pack.conflicts),
            "exceptions": jsonable(pack.exceptions),
            "averaged": False,
            "material_ai_factors_have_source_and_freshness": all(
                fact.get("source_system") and fact.get("freshness_state") for fact in facts
            ),
        }

    def _graph(self, application_id: str, *, actor_role: str, actor_tenant: str) -> dict[str, Any]:
        graph = assemble_runtime_context(
            application_id, actor_role=actor_role, actor_tenant=actor_tenant
        )
        return {
            "enabled": True,
            "snapshot_id": graph.snapshot_id,
            "nodes": jsonable(graph.nodes),
            "edges": jsonable(graph.edges),
            "excluded": jsonable(graph.excluded),
            "source_health": graph.source_health,
            "unresolved_conflicts": graph.unresolved_conflicts,
            "policy_version": graph.policy_version,
            "kinds": sorted({node.kind for node in graph.nodes}),
        }

    def _retrieval(self, application_id: str, actor_tenant: str) -> dict[str, Any]:
        plan = route_underwriting(application_id, actor_tenant=actor_tenant)
        labelled = []
        for hop in plan.hops:
            labelled.append(
                {
                    **hop.as_trace_row(),
                    "family_label": hop.family.name,
                    "filters": {
                        "tenant": actor_tenant,
                        "application_id": application_id,
                        "active_policy": hop.family is RetrievalFamily.POLICY,
                    },
                    "facts": jsonable(hop.facts),
                }
            )
        return {
            "enabled": True,
            "denied": plan.denied,
            "families": [family.value for family in RetrievalFamily],
            "hops": labelled,
            "vector_is_not_policy": all(
                not (hop.family is RetrievalFamily.SEMANTIC and hop.controlling) for hop in plan.hops
            ),
            "controlling_policy_sources": plan.controlling_policy_sources(),
        }

    def _sanitize_denied_layers(self, layers: list[dict[str, Any]]) -> list[dict[str, Any]]:
        cleaned = []
        for layer in layers:
            row = dict(layer)
            if row.get("effect") == "DENY" or row.get("layer") == "output":
                row["content_refs"] = []
            cleaned.append(row)
        return cleaned

    def _retrieval_denied(self, application_id: str, actor_tenant: str) -> dict[str, Any]:
        inspection = inspect_retrieval_layers(application_id, actor_tenant)
        layers = self._sanitize_denied_layers(jsonable(inspection.layers))
        return {
            "enabled": True,
            "denied": "CROSS_TENANT",
            "families": [family.value for family in RetrievalFamily],
            "hops": [],
            "layers": layers,
            "content_refs_empty": all(
                len(layer.get("content_refs") or []) == 0
                for layer in layers
                if layer.get("layer") != "memory"
            ),
        }

    def _policy(self, application_id: str, actor_role: str) -> dict[str, Any]:
        view = evaluate_application(application_id)
        retrieval = retrieve_active_policy()
        historical = [
            {"version": bundle.version, "status": bundle.status, "controlling": bundle.controlling}
            for bundle in retrieval.historical
        ]
        ai_actions = {
            action: jsonable(
                check_access_and_authority(application_id, actor_role="AI_AGENT", action=action)
            )
            for action in sorted(FINAL_ACTIONS)
        }
        actor_probe = (
            "DRAFT_RECOMMENDATION",
            "APPROVE",
            "DECLINE",
            "APPROVE_EXCEPTION",
            "ISSUE_ADVERSE",
            "AUTHORIZE_LARGE_LIMIT",
        )
        actor_actions = {
            action: jsonable(
                check_access_and_authority(application_id, actor_role=actor_role, action=action)
            )
            for action in actor_probe
        }
        return {
            "enabled": True,
            "active_version": retrieval.controlling_version,
            "active_status": None if retrieval.controlling is None else retrieval.controlling.status,
            "superseded_version": SUPERSEDED_VERSION,
            "historical": historical,
            "engine": jsonable(view.engine),
            "required_human_role": view.required_human_role,
            "los_assigned_role": view.los_assigned_role,
            "exception_class": None if view.exception_class is None else view.exception_class.value,
            "stance": view.stance.value,
            "notes": list(view.notes),
            "policy_pass_is_not_approve": True,
            "ai_final_actions": ai_actions,
            "actor_actions": actor_actions,
        }

    def _memo(self, application_id: str, *, actor_role: str) -> dict[str, Any]:
        if not self.flags.memo_visible():
            return {
                "enabled": False,
                "blocked": "G-UI-01",
                "reason": "Human Decision, Decision Trace and Outcome & Feedback must be on before memo assist",
                "is_final_decision": False,
            }
        if actor_role not in MEMO_ROLES:
            return {
                "enabled": False,
                "blocked": "ROLE",
                "reason": f"{actor_role} cannot prepare a memo",
                "is_final_decision": False,
            }
        try:
            memo = generate_credit_memo(application_id)
        except MemoAssistanceUnavailable as exc:
            return {
                "enabled": False,
                "blocked": "DEGRADED",
                "reason": str(exc),
                "is_final_decision": False,
                "manual_underwriting": jsonable(manual_underwriting_view(application_id)),
                "fabricated": False,
            }
        rec = None if memo.recommendation is None else jsonable(memo.recommendation)
        return {
            "enabled": True,
            "blocked": None,
            "memo_id": memo.memo_id,
            "trust_class": memo.trust_class,
            "is_final_decision": False,
            "policy_version": memo.policy_version,
            "engine_result": memo.engine_result,
            "sections": list(memo.sections_present()),
            "statements": jsonable(memo.statements),
            "rendered_text": memo.rendered_text(),
            "recommendation": rec,
            "provenance_coverage": memo.provenance_coverage(),
            "model": "NONE",
        }

    def _human_decision(self, application_id: str, actor_role: str) -> dict[str, Any]:
        view = evaluate_application(application_id)
        try:
            rec = jsonable(handoff_recommendation(application_id))
        except (AuthorityDenied, SemanticCollapseError) as exc:
            rec = {"error": _err(exc)}
        actions = {}
        for action in (
            "APPROVE",
            "DECLINE",
            "CONDITION",
            "APPROVE_EXCEPTION",
            "ISSUE_ADVERSE",
            "AUTHORIZE_LARGE_LIMIT",
        ):
            actions[action] = jsonable(
                check_access_and_authority(application_id, actor_role=actor_role, action=action)
            )
        ai_approve = check_access_and_authority(
            application_id, actor_role="AI_AGENT", action="APPROVE"
        )
        return {
            "enabled": self.flags.screen_enabled("human_decision"),
            "required_human_role": view.required_human_role,
            "actor_role": actor_role,
            "ai_agent_final_credit": False,
            "ai_approve_effect": ai_approve.effect,
            "recommendation": rec,
            "actions": actions,
            "recorded": self.decisions.get(application_id),
            "policy_pass_is_not_approve": True,
        }

    def _trace_payload(
        self,
        application_id: str,
        *,
        actor_role: str,
        actor_tenant: str,
    ) -> dict[str, Any]:
        if not self.flags.screen_enabled("decision_trace"):
            return {"enabled": False, "blocked": "ui.decision_trace"}
        cache_key = f"{application_id}:{actor_tenant}:{actor_role}"
        cached = self.traces.get(cache_key)
        if cached is None:
            trace = record_decision_trace(
                application_id, actor_role=actor_role, actor_tenant=actor_tenant
            )
            cached = trace.to_dict()
            self.traces[cache_key] = cached
        keys = set(cached.keys())
        present = set(cached) | set(cached.get("versions", {}))
        return {
            "enabled": True,
            "trace": cached,
            "required_fields_present": all(field in cached for field in REQUIRED_TRACE_FIELDS),
            "required_fields": list(REQUIRED_TRACE_FIELDS),
            "forbidden_cot_keys_absent": not any(key in keys for key in FORBIDDEN_TRACE_KEYS),
            "cot_denylist_enforced": True,
            "generated_explanation_is_not_policy": True,
            "fields_seen": sorted(present),
        }

    def _feedback_view(
        self,
        application_id: str,
        *,
        actor_role: str,
        actor_tenant: str,
    ) -> dict[str, Any]:
        return {
            "enabled": self.flags.screen_enabled("outcome_feedback"),
            "actor_role": actor_role,
            "actor_tenant": actor_tenant,
            "queued": self.feedback.get(application_id, []),
            "auto_applied": False,
            "blocked_destinations": list(PROTECTED_DESTINATIONS),
            "ai_accepted_is_not_gold": True,
        }

    def _fairness(self, *, purpose: str, actor_role: str) -> dict[str, Any]:
        allowed = purpose == FAIRNESS_PURPOSE and actor_role == FAIRNESS_ROLE
        if not allowed:
            return {
                "enabled": True,
                "separated_from_runtime": True,
                "runtime_access": False,
                "reason": "Fairness/impact evaluation requires purpose RISK_COMPLIANCE_EVAL and role RISK_COMPLIANCE_EVAL",
                "rows": [],
                "legal_cutoff_invented": False,
            }
        rows = _csv(HISTORY / "restricted_fairness_eval_sample.csv")
        return {
            "enabled": True,
            "separated_from_runtime": True,
            "runtime_access": True,
            "purpose": FAIRNESS_PURPOSE,
            "use_restriction": "EVALUATION_ONLY_APPROVED_PURPOSE",
            "rows": rows,
            "legal_cutoff_invented": False,
            "note": "Cohort diagnostics only. No legal fairness threshold is invented.",
        }

    def _failure_simulation(
        self,
        application_id: str,
        *,
        actor_tenant: str,
        actor_role: str,
        denied: bool,
    ) -> dict[str, Any]:
        del actor_role
        degraded = None
        untrusted: list[dict[str, Any]] = []
        policy_check = None
        manual = None
        if not denied:
            degraded = jsonable(assess_degraded_mode(application_id, actor_tenant=actor_tenant))
            untrusted = jsonable(load_untrusted_documents(application_id, actor_tenant))
            policy_check = policy_unaffected_by_document(application_id, actor_tenant)
            manual = jsonable(manual_underwriting_view(application_id))
        inspection = jsonable(inspect_retrieval_layers(application_id, actor_tenant))
        if denied:
            inspection["layers"] = self._sanitize_denied_layers(inspection.get("layers") or [])
            inspection["untrusted_items"] = []
        return {
            "enabled": True,
            "application_id": None if denied else application_id,
            "denied": "CROSS_TENANT" if denied else None,
            "degraded": degraded,
            "untrusted_documents": untrusted,
            "injection_treated_as_data": True,
            "policy_unaffected_by_document": policy_check,
            "inspection": inspection,
            "manual_underwriting": manual,
            "probes": {
                "stale_bank": "SME-L005",
                "bureau_unavailable": "SME-L006",
                "cross_tenant": "SME-L008",
                "injection": "SME-L009",
                "ai_outage": "SME-L010",
                "financial_conflict": "SME-L011",
                "superseded_policy": "SME-L012",
                "invented_threshold": "SME-L014",
            },
        }

    def record_decision(
        self,
        application_id: str,
        *,
        actor_role: str,
        actor_tenant: str,
        outcome: str,
    ) -> dict[str, Any]:
        isolation = display_payload(application_id, actor_tenant)
        if isolation.get("denied"):
            return {"ok": False, "denied": "CROSS_TENANT", "decision": None}
        if actor_role == "AI_AGENT":
            check = check_access_and_authority(
                application_id, actor_role="AI_AGENT", action="APPROVE"
            )
            return {"ok": False, "denied": "AI_NO_FINAL_CREDIT", "check": jsonable(check)}
        if actor_role not in DECISION_ROLES:
            return {
                "ok": False,
                "denied": "ROLE",
                "reason": f"{actor_role} cannot record a human decision",
            }
        try:
            decision = record_human_decision(
                application_id, actor_role=actor_role, outcome=outcome
            )
            trace = attach_human_action(
                application_id,
                actor_role=actor_role,
                outcome=outcome,
                actor_tenant=actor_tenant,
            )
        except (AuthorityDenied, SemanticCollapseError) as exc:
            return {"ok": False, "denied": type(exc).__name__, "reason": str(exc)}
        recorded = jsonable(decision)
        recorded["is_recommendation"] = False
        self.decisions[application_id] = recorded
        self.traces[f"{application_id}:{actor_tenant}:{actor_role}"] = trace.to_dict()
        return {"ok": True, "denied": None, "decision": recorded, "trace": trace.to_dict()}

    def capture_feedback(
        self,
        application_id: str,
        *,
        actor_role: str,
        actor_tenant: str,
        feedback_type: str,
    ) -> dict[str, Any]:
        isolation = display_payload(application_id, actor_tenant)
        if isolation.get("denied"):
            return {"ok": False, "denied": "CROSS_TENANT"}
        human = None
        recorded = self.decisions.get(application_id)
        if feedback_type == "HUMAN_DECISION":
            if recorded is None:
                return {
                    "ok": False,
                    "denied": "NO_HUMAN_DECISION",
                    "reason": "record an authorized human decision first",
                }
            human = HumanDecision(
                outcome=DecisionOutcome(recorded["outcome"]),
                actor_role=recorded["actor_role"],
                policy_version=recorded["policy_version"],
                application_id=application_id,
            )
        try:
            record = capture_outcome_feedback(
                application_id,
                feedback_type=feedback_type,
                actor_role=actor_role,
                human_decision=human,
            )
        except (FeedbackGovernanceError, SemanticCollapseError) as exc:
            return {"ok": False, "denied": type(exc).__name__, "reason": str(exc)}
        payload = jsonable(record)
        self.feedback.setdefault(application_id, []).append(payload)
        return {"ok": True, "record": payload}

    def refuse_ungoverned_write(self, application_id: str, destination: str) -> dict[str, Any]:
        from credit_domain.evals import UngovernedLearningWriteError

        record = capture_outcome_feedback(
            application_id, feedback_type="AI_ACCEPTED", actor_role="PORTFOLIO_ANALYST"
        )
        try:
            apply_feedback_to_destination(record, destination)
            return {"ok": False, "reason": "write was not blocked"}
        except (UngovernedLearningWriteError, FeedbackGovernanceError) as exc:
            return {
                "ok": True,
                "blocked": True,
                "destination": destination,
                "error": _err(exc),
                "protected": list(PROTECTED_DESTINATIONS),
            }

    def probe_invented_threshold(self, application_id: str = "SME-L014") -> dict[str, Any]:
        try:
            scan_generated_policy_claims(INVENTED_THRESHOLD_PROBE, application_id=application_id)
            return {"ok": False, "rejected": False, "probe": INVENTED_THRESHOLD_PROBE}
        except PolicyFidelityError as exc:
            return {
                "ok": True,
                "rejected": True,
                "critical": True,
                "probe": INVENTED_THRESHOLD_PROBE,
                "error": _err(exc),
                "active_policy": ACTIVE_VERSION,
            }

    def probe_injection(
        self, application_id: str = "SME-L009", actor_tenant: str = "TENANT-ALPHA"
    ) -> dict[str, Any]:
        docs = load_untrusted_documents(application_id, actor_tenant)
        followed = []
        for item in docs:
            try:
                follow_untrusted_instruction(item)
                followed.append({"source_id": item.source_id, "followed": True})
            except UntrustedInstructionError as exc:
                followed.append(
                    {
                        "source_id": item.source_id,
                        "followed": False,
                        "trust_class": item.trust_class,
                        "injection_detected": item.injection_detected,
                        "text": item.text,
                        "error": str(exc),
                    }
                )
        return {
            "documents": followed,
            "any_followed": any(row.get("followed") for row in followed),
            "policy": policy_unaffected_by_document(application_id, actor_tenant),
        }

    def probe_superseded_policy(self) -> dict[str, Any]:
        active = retrieve_active_policy()
        superseded = retrieve_active_policy(version=SUPERSEDED_VERSION)
        return {
            "controlling_version": active.controlling_version,
            "controlling_is_active": active.controlling is not None
            and active.controlling.status == "ACTIVE",
            "superseded_requested_controlling": None
            if superseded.controlling is None
            else superseded.controlling.version,
            "v29_controlling": any(
                bundle.version == SUPERSEDED_VERSION and bundle.controlling
                for bundle in superseded.historical
            ),
            "v29_historical": [
                {"version": bundle.version, "status": bundle.status, "controlling": bundle.controlling}
                for bundle in superseded.historical
            ],
        }
