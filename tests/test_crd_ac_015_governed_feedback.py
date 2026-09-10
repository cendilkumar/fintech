"""CRD-AC-015 / CRD-FR-010 — governed feedback; no silent policy/gold rewrite."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from credit_domain.evals import UngovernedLearningWriteError  # noqa: E402
from credit_domain.feedback import (  # noqa: E402
    FeedbackGovernanceError,
    apply_feedback_to_destination,
    capture_outcome_feedback,
    inject_restricted_eval_into_runtime,
    snapshot_write_protected,
)
from credit_domain.policy import evaluate_application  # noqa: E402


class Ac015LearningLoopTests(unittest.TestCase):
    def test_sme_l015_ai_accepted_does_not_mutate_policy_or_gold(self):
        before = snapshot_write_protected()
        record = capture_outcome_feedback(
            "SME-L015",
            feedback_type="AI_ACCEPTED",
            actor_role="PORTFOLIO_ANALYST",
        )
        after = snapshot_write_protected()
        self.assertEqual(record.status, "GOVERNED_REVIEW")
        self.assertFalse(record.auto_applied)
        self.assertEqual(record.controlling_rule, "FEEDBACK-001")
        self.assertEqual(record.policy_version, "CREDIT-POLICY-3.2")
        self.assertIn("POLICY_BUNDLE", record.blocked_destinations)
        self.assertIn("GOLD_LABELS", record.blocked_destinations)
        self.assertIn("PROMPT", record.blocked_destinations)
        self.assertIn("MODEL", record.blocked_destinations)
        self.assertEqual(before, after)
        self.assertEqual(record.artifact_hashes, after)
        view = evaluate_application("SME-L015")
        self.assertEqual(view.engine.result, "PASS")
        self.assertEqual(view.engine.policy_version, "CREDIT-POLICY-3.2")
        with self.assertRaises(FeedbackGovernanceError):
            record.as_policy_update()
        with self.assertRaises(FeedbackGovernanceError):
            record.as_human_decision()
        for destination in ("POLICY_BUNDLE", "GOLD_LABELS", "PROMPT", "MODEL", "ONTOLOGY"):
            with self.assertRaises(UngovernedLearningWriteError):
                apply_feedback_to_destination(record, destination)

    def test_missing_portfolio_outcome_is_not_invented(self):
        record = capture_outcome_feedback(
            "SME-L015",
            feedback_type="PORTFOLIO_OUTCOME",
            actor_role="PORTFOLIO_ANALYST",
        )
        self.assertIsNone(record.portfolio_outcome)
        self.assertTrue(
            any("none invented" in note for note in record.notes)
        )

    def test_ai_agent_cannot_file_operator_feedback(self):
        with self.assertRaises(FeedbackGovernanceError):
            capture_outcome_feedback(
                "SME-L015",
                feedback_type="AI_ACCEPTED",
                actor_role="AI_AGENT",
            )

    def test_restricted_eval_cannot_enter_runtime_via_feedback(self):
        with self.assertRaises(FeedbackGovernanceError):
            inject_restricted_eval_into_runtime("SME-L015")


if __name__ == "__main__":
    unittest.main()
