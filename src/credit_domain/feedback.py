"""CRD-FR-010 / CRD-DATA-016 / CRD-AC-015 governed feedback write-path.

Capture operator feedback, human decisions and later outcomes into
GOVERNED_REVIEW. Do not silently rewrite policy, ontology, prompts,
models or gold labels. Do not invent missing portfolio outcomes.
"""

from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .context import assemble_runtime_context
from .evals import UngovernedLearningWriteError, snapshot_protected_artifacts
from .model import HumanDecision, SemanticCollapseError
from .policy import ACTIVE_VERSION, evaluate_application, load_live_application

ROOT = Path(__file__).resolve().parents[2]
HISTORY = ROOT / "evidence" / "05_history_feedback"
CONSTRAINT_RULE = "FEEDBACK-001"

OPERATOR_FEEDBACK = frozenset({"AI_ACCEPTED", "AI_REJECTED", "AI_MODIFIED", "MANUAL_ONLY"})
OUTCOME_FEEDBACK = frozenset({"HUMAN_DECISION", "PORTFOLIO_OUTCOME"})
ALLOWED_FEEDBACK = OPERATOR_FEEDBACK | OUTCOME_FEEDBACK
OPERATOR_ROLES = frozenset(
    {"CREDIT_ANALYST", "SENIOR_UNDERWRITER", "CREDIT_AUTHORITY", "PORTFOLIO_ANALYST"}
)
PROTECTED_DESTINATIONS = (
    "POLICY_BUNDLE",
    "ONTOLOGY",
    "SEMANTIC_DEFINITIONS",
    "KG_SCHEMA",
    "PROMPT",
    "MODEL",
    "GOLD_LABELS",
)
WRITE_PROTECTED_PATHS = (
    "evidence/02_documents/credit_underwriting_policy_v3_2.md",
    "evidence/02_documents/superseded_credit_policy_v2_9_REFERENCE_ONLY.md",
    "specs/05_data_contracts/DOMAIN_MODEL.md",
    "evidence/03_semantic_evidence/conflicting_terms.csv",
    "evidence/06_evaluations/golden_scenarios.json",
    "evidence/06_evaluations/expected_behaviors.json",
    "google_ai_build/02_GOOGLE_AI_BUILD_MASTER_PROMPT.md",
    "evidence/04_policy_authority/decision_constraints.yaml",
)


class FeedbackGovernanceError(SemanticCollapseError):
    """Raised when feedback tries to become policy, gold, prompt or model authority."""


@dataclass(frozen=True)
class FeedbackRecord:
    application_id: str
    feedback_type: str
    actor_role: str
    tenant_id: str
    status: str
    controlling_rule: str
    policy_version: str
    auto_applied: bool
    blocked_destinations: tuple[str, ...]
    queued_for: str
    artifact_hashes: dict[str, str]
    notes: tuple[str, ...] = ()
    human_decision: HumanDecision | None = None
    portfolio_outcome: dict[str, Any] | None = None
    evaluation_flags: tuple[str, ...] = field(default_factory=tuple)

    def as_human_decision(self) -> HumanDecision:
        raise FeedbackGovernanceError("feedback capture is not a HumanDecision")

    def as_policy_update(self) -> None:
        raise FeedbackGovernanceError(
            f"{self.feedback_type} cannot rewrite CREDIT-POLICY-3.2 ({CONSTRAINT_RULE})"
        )


def snapshot_write_protected() -> dict[str, str]:
    hashes = dict(snapshot_protected_artifacts())
    for rel in WRITE_PROTECTED_PATHS:
        path = ROOT / rel
        hashes[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def _portfolio_row(application_id: str) -> dict[str, str] | None:
    path = HISTORY / "portfolio_outcomes.csv"
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row.get("application_id") == application_id:
                return row
    return None


def _restricted_eval_ids() -> set[str]:
    path = HISTORY / "restricted_fairness_eval_sample.csv"
    ids: set[str] = set()
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row.get("use_restriction") == "EVALUATION_ONLY_APPROVED_PURPOSE":
                ids.add(row["eval_case_id"])
    return ids


def apply_feedback_to_destination(record: FeedbackRecord, destination: str) -> None:
    """Automatic learning writes are denied. Review may open a change request only."""
    dest = destination.upper()
    if dest in PROTECTED_DESTINATIONS:
        raise UngovernedLearningWriteError(
            f"{record.feedback_type} cannot automatically write {dest}; "
            f"queued_for={record.queued_for} rule={CONSTRAINT_RULE}"
        )
    raise FeedbackGovernanceError(f"unknown learning destination {destination}")


def inject_restricted_eval_into_runtime(application_id: str) -> None:
    eval_ids = _restricted_eval_ids()
    graph = assemble_runtime_context(application_id)
    if any(n.node_id in eval_ids or n.label in eval_ids for n in graph.nodes):
        raise FeedbackGovernanceError("restricted fairness eval sample entered runtime context")
    raise FeedbackGovernanceError(
        "restricted fairness eval sample cannot enter runtime decision context"
    )


def capture_outcome_feedback(
    application_id: str,
    *,
    feedback_type: str,
    actor_role: str,
    human_decision: HumanDecision | None = None,
) -> FeedbackRecord:
    """CRD-TOOL-010. Capture only. Never mutate write-protected artifacts."""
    if feedback_type not in ALLOWED_FEEDBACK:
        raise FeedbackGovernanceError(f"unknown feedback type {feedback_type}")
    if actor_role == "AI_AGENT":
        raise FeedbackGovernanceError("AI_AGENT cannot file operator feedback as authority")
    if actor_role not in OPERATOR_ROLES:
        raise FeedbackGovernanceError(f"{actor_role} cannot capture governed feedback")

    before = snapshot_write_protected()
    app = load_live_application(application_id)
    view = evaluate_application(application_id)
    notes = [
        f"status={app['status']}",
        f"stage={app['current_stage']}",
        f"assigned={app['assigned_role']}",
        f"engine={None if view.engine is None else view.engine.result}",
        "AI_ACCEPTED is interaction feedback, not ground truth",
        "automatic writes to policy/ontology/prompts/models/gold labels are denied",
    ]

    outcome = None
    if feedback_type == "PORTFOLIO_OUTCOME":
        outcome = _portfolio_row(application_id)
        if outcome is None:
            notes.append(
                "no portfolio_outcomes.csv row for this application; none invented"
            )

    if feedback_type == "HUMAN_DECISION" and human_decision is None:
        raise FeedbackGovernanceError("HUMAN_DECISION capture requires an authorized HumanDecision")
    if human_decision is not None and human_decision.application_id != application_id:
        raise FeedbackGovernanceError("human decision application_id does not match")

    after = snapshot_write_protected()
    if before != after:
        raise FeedbackGovernanceError("capture mutated write-protected artifacts")

    record = FeedbackRecord(
        application_id=application_id,
        feedback_type=feedback_type,
        actor_role=actor_role,
        tenant_id=app["tenant_id"],
        status="GOVERNED_REVIEW",
        controlling_rule=CONSTRAINT_RULE,
        policy_version=view.retrieval.controlling_version or ACTIVE_VERSION,
        auto_applied=False,
        blocked_destinations=PROTECTED_DESTINATIONS,
        queued_for="GOVERNED_EVALUATION_CHANGE_CONTROL",
        artifact_hashes=after,
        notes=tuple(notes),
        human_decision=human_decision,
        portfolio_outcome=outcome,
        evaluation_flags=("CRD-AC-015", "FEEDBACK-001"),
    )
    return record
