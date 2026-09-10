"""CRD-FR-007 / CRD-FR-011 — authority gate for CRD-AC-002 and CRD-AC-007."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from credit_domain.authority import (  # noqa: E402
    AuthorityDenied,
    check_access_and_authority,
    draft_recommendation,
    handoff_recommendation,
    record_human_decision,
    refuse_ai_final_action,
    required_authority,
)
from credit_domain.model import (  # noqa: E402
    DecisionOutcome,
    RecommendationStance,
    SemanticCollapseError,
)
from credit_domain.policy import evaluate_application  # noqa: E402


class Ac002LargeLimitAuthorityTests(unittest.TestCase):
    def test_sme_l002_requires_credit_authority_not_los_assignment(self):
        view = evaluate_application("SME-L002")
        self.assertEqual(view.required_human_role, "CREDIT_AUTHORITY")
        self.assertEqual(view.los_assigned_role, "SENIOR_UNDERWRITER")
        self.assertNotEqual(view.los_assigned_role, view.required_human_role)
        auth = required_authority("SME-L002")
        self.assertEqual(auth.role, "CREDIT_AUTHORITY")
        self.assertEqual(auth.final_credit_decision, "YES")

        rec = handoff_recommendation("SME-L002", actor_role="AI_AGENT")
        self.assertEqual(rec.stance, RecommendationStance.REFER)
        self.assertEqual(rec.required_authority.role, "CREDIT_AUTHORITY")
        with self.assertRaises(SemanticCollapseError):
            rec.as_human_decision()

        deny_ai = refuse_ai_final_action("SME-L002", "AUTHORIZE_LARGE_LIMIT")
        self.assertEqual(deny_ai.effect, "DENY")
        self.assertEqual(deny_ai.controlling_rule, "CREDIT-AUTH-001")
        self.assertEqual(refuse_ai_final_action("SME-L002", "APPROVE").effect, "DENY")

        deny_senior = check_access_and_authority(
            "SME-L002", actor_role="SENIOR_UNDERWRITER", action="APPROVE"
        )
        self.assertEqual(deny_senior.effect, "DENY")
        self.assertEqual(deny_senior.required_human_role, "CREDIT_AUTHORITY")
        self.assertIn("AUTH-LIMIT-01", deny_senior.controlling_rule)
        with self.assertRaises(AuthorityDenied):
            record_human_decision(
                "SME-L002", actor_role="SENIOR_UNDERWRITER", outcome=DecisionOutcome.APPROVE
            )

        allow = check_access_and_authority(
            "SME-L002", actor_role="CREDIT_AUTHORITY", action="AUTHORIZE_LARGE_LIMIT"
        )
        self.assertEqual(allow.effect, "ALLOW")
        decision = record_human_decision(
            "SME-L002", actor_role="CREDIT_AUTHORITY", outcome=DecisionOutcome.ESCALATE
        )
        self.assertEqual(decision.actor_role, "CREDIT_AUTHORITY")
        self.assertNotEqual(decision.actor_role, "AI_AGENT")


class Ac007ExceptionAuthorityTests(unittest.TestCase):
    def test_sme_l007_routes_to_senior_and_ai_cannot_approve_exception(self):
        view = evaluate_application("SME-L007")
        self.assertEqual(view.engine.result, "EXCEPTION_REVIEW")
        self.assertEqual(view.required_human_role, "SENIOR_UNDERWRITER")
        missing = evaluate_application("SME-L006")
        self.assertEqual(missing.engine.result, "INSUFFICIENT_EVIDENCE")
        self.assertNotEqual(view.engine.result, missing.engine.result)

        rec = handoff_recommendation("SME-L007")
        self.assertEqual(rec.required_authority.role, "SENIOR_UNDERWRITER")
        self.assertEqual(rec.stance, RecommendationStance.REFER)

        deny_ai = refuse_ai_final_action("SME-L007", "APPROVE_EXCEPTION")
        self.assertEqual(deny_ai.effect, "DENY")
        deny_analyst = check_access_and_authority(
            "SME-L007", actor_role="CREDIT_ANALYST", action="APPROVE_EXCEPTION"
        )
        self.assertEqual(deny_analyst.effect, "DENY")
        allow_senior = check_access_and_authority(
            "SME-L007", actor_role="SENIOR_UNDERWRITER", action="APPROVE_EXCEPTION"
        )
        self.assertEqual(allow_senior.effect, "ALLOW")
        self.assertEqual(allow_senior.controlling_rule, "POL-EXC-07")


class RecommendationAuthorityFieldTests(unittest.TestCase):
    def test_every_recommendation_states_required_authority(self):
        for application_id, role in (
            ("SME-L001", "CREDIT_ANALYST"),
            ("SME-L002", "CREDIT_AUTHORITY"),
            ("SME-L007", "SENIOR_UNDERWRITER"),
            ("SME-L012", "CREDIT_AUTHORITY"),
            ("SME-L013", "CREDIT_AUTHORITY"),
        ):
            rec = draft_recommendation(application_id)
            self.assertEqual(rec.required_authority.role, role)
            self.assertNotEqual(rec.required_authority.role, "AI_AGENT")
            self.assertEqual(
                check_access_and_authority(
                    application_id, actor_role="AI_AGENT", action="ASSIST"
                ).effect,
                "ALLOW",
            )

    def test_ai_cannot_issue_adverse_or_price_change(self):
        self.assertEqual(refuse_ai_final_action("SME-L013", "ISSUE_ADVERSE").effect, "DENY")
        self.assertEqual(refuse_ai_final_action("SME-L013", "DECLINE").effect, "DENY")
        self.assertEqual(refuse_ai_final_action("SME-L001", "PRICE").effect, "DENY")
        self.assertEqual(refuse_ai_final_action("SME-L001", "CHANGE_FACILITY").effect, "DENY")
        with self.assertRaises(SemanticCollapseError):
            record_human_decision(
                "SME-L001", actor_role="AI_AGENT", outcome=DecisionOutcome.APPROVE
            )


if __name__ == "__main__":
    unittest.main()
