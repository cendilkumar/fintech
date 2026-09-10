"""G-UI-01 / artefacts/RELEASE_MANAGEMENT_PLAN.md feature flags.

Isolation, authority and policy retrieve cannot be flagged off.
Memo assist cannot appear unless Human Decision, Trace and Feedback are on.
"""

from __future__ import annotations

from copy import deepcopy

LOCKED_ON = (
    "isolation.before_retrieval",
    "authority.gate",
    "policy.retrieve",
)

DEFAULT_FLAGS = {
    "isolation.before_retrieval": True,
    "authority.gate": True,
    "policy.retrieve": True,
    "ui.human_decision": True,
    "ui.decision_trace": True,
    "ui.outcome_feedback": True,
    "ui.memo_assist": True,
    "model.generation": False,
}

SCREENS = (
    "control_tower",
    "application_context",
    "evidence_reconciliation",
    "context_graph",
    "hybrid_retrieval",
    "policy_authority",
    "human_decision",
    "decision_trace",
    "outcome_feedback",
    "credit_memo",
    "fairness_eval",
    "failure_simulation",
)

# G-UI-01: these three exist before any user-visible memo.
PRE_MEMO_SCREENS = ("human_decision", "decision_trace", "outcome_feedback")


class FlagError(ValueError):
    """Raised when a caller tries to disable a hard control."""


class FeatureFlags:
    def __init__(self, initial: dict[str, bool] | None = None) -> None:
        self._flags = deepcopy(DEFAULT_FLAGS)
        if initial:
            self.apply(initial)

    def as_dict(self) -> dict[str, bool]:
        return dict(self._flags)

    def apply(self, updates: dict[str, bool]) -> dict[str, bool]:
        for key, value in updates.items():
            if key not in self._flags:
                raise FlagError(f"unknown flag {key}")
            if key in LOCKED_ON and value is False:
                raise FlagError(f"{key} cannot be flagged off")
            self._flags[key] = bool(value)
        if not self.memo_prerequisites_met():
            self._flags["ui.memo_assist"] = False
        return self.as_dict()

    def memo_prerequisites_met(self) -> bool:
        return all(
            self._flags[name]
            for name in ("ui.human_decision", "ui.decision_trace", "ui.outcome_feedback")
        )

    def memo_visible(self) -> bool:
        return self.memo_prerequisites_met() and bool(self._flags["ui.memo_assist"])

    def screen_enabled(self, screen_id: str) -> bool:
        if screen_id == "credit_memo":
            return self.memo_visible()
        if screen_id == "human_decision":
            return bool(self._flags["ui.human_decision"])
        if screen_id == "decision_trace":
            return bool(self._flags["ui.decision_trace"])
        if screen_id == "outcome_feedback":
            return bool(self._flags["ui.outcome_feedback"])
        return screen_id in SCREENS
