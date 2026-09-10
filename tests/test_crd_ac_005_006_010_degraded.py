"""CRD-AC-005 / CRD-AC-006 / CRD-AC-010 — degraded underwriting assistance."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from credit_domain.degraded import (  # noqa: E402
    BANK_STALE_AFTER_DAYS,
    DegradedMode,
    DegradedModeError,
    assess_degraded_mode,
    continue_with_handoff,
    emit_ai_assistance,
    manual_underwriting_view,
    refuse_fabricated_bureau,
    scan_generated_degraded_claims,
    structured_facts_or_empty,
)
from credit_domain.model import ExceptionClass, RecommendationStance  # noqa: E402
from credit_domain.policy import evaluate_application  # noqa: E402


class Ac005StaleBankDegradedTests(unittest.TestCase):
    def test_sme_l005_can_continue_without_treating_bank_as_current(self):
        assessment = assess_degraded_mode("SME-L005")
        self.assertEqual(assessment.mode, DegradedMode.DECISION_CAN_CONTINUE)
        self.assertEqual(assessment.bank_freshness, "stale")
        self.assertFalse(assessment.bank_presented_as_current)
        self.assertTrue(assessment.bank_refresh_requested)
        self.assertEqual(BANK_STALE_AFTER_DAYS, 7)
        self.assertEqual(assessment.engine_result, "PASS")
        self.assertIn("DATA-FRESHNESS-BANK", assessment.controlling_rules)
        self.assertEqual(emit_ai_assistance(assessment)["effect"], "ALLOW")
        self.assertTrue(assessment.manual_underwriting_available)
        scan_generated_degraded_claims(
            "Bank inflows exist but the feed is stale; refresh requested. PASS is not current.",
            assessment,
        )
        with self.assertRaises(DegradedModeError):
            scan_generated_degraded_claims(
                "The bank feed is current and inflows are current for underwriting.",
                assessment,
            )


class Ac006BureauOutageTests(unittest.TestCase):
    def test_sme_l006_requires_evidence_and_does_not_invent_bureau(self):
        assessment = assess_degraded_mode("SME-L006")
        self.assertEqual(assessment.mode, DegradedMode.REQUIRES_ADDITIONAL_EVIDENCE)
        self.assertFalse(assessment.bureau_available)
        self.assertIsNone(assessment.bureau_value)
        self.assertEqual(assessment.engine_result, "INSUFFICIENT_EVIDENCE")
        self.assertIn("DATA-BUREAU-REQ", assessment.controlling_rules)
        self.assertEqual(assessment.exception_class, ExceptionClass.MISSING_EVIDENCE.value)
        self.assertNotEqual(assessment.mode, DegradedMode.DECISION_CAN_CONTINUE)
        exception = evaluate_application("SME-L007")
        self.assertEqual(exception.engine.result, "EXCEPTION_REVIEW")
        self.assertEqual(exception.exception_class, ExceptionClass.POLICY_EXCEPTION)
        self.assertEqual(emit_ai_assistance(assessment)["effect"], "DENY")
        with self.assertRaises(DegradedModeError):
            refuse_fabricated_bureau(assessment, "C")
        with self.assertRaises(DegradedModeError):
            scan_generated_degraded_claims(
                "Assume bureau score band C and continue underwriting.",
                assessment,
            )


class Ac010AiOutageTests(unittest.TestCase):
    def test_sme_l010_manual_path_continues_without_fabricated_assistance(self):
        assessment, rec, manual = continue_with_handoff("SME-L010")
        self.assertEqual(assessment.mode, DegradedMode.AI_ASSISTANCE_UNAVAILABLE)
        self.assertFalse(assessment.ai_assist_available)
        self.assertFalse(assessment.ai_assistance_permitted)
        self.assertEqual(emit_ai_assistance(assessment)["effect"], "DENY")
        self.assertTrue(manual.executable)
        self.assertEqual(manual.fallback_rule, "FALLBACK-001")
        self.assertEqual(manual.engine_result, "REQUIRES_CREDIT_AUTHORITY")
        self.assertEqual(manual.required_human_role, "CREDIT_AUTHORITY")
        self.assertIn("AUTH-LIMIT-01", manual.triggered_rule_ids)
        self.assertEqual(manual.policy_version, "CREDIT-POLICY-3.2")
        health = {row.source: row.state for row in manual.source_health}
        self.assertEqual(health["AI_ASSIST"], "UNAVAILABLE")
        self.assertEqual(health["BANK_DATA"], "HEALTHY")
        self.assertEqual(health["CREDIT_BUREAU"], "HEALTHY")
        self.assertEqual(health["POLICY_ENGINE"], "HEALTHY")
        self.assertEqual(rec.required_authority.role, "CREDIT_AUTHORITY")
        self.assertNotEqual(assessment.mode, DegradedMode.MANDATORY_ABSTENTION)
        with self.assertRaises(DegradedModeError):
            scan_generated_degraded_claims(
                "AI recommends approval; generated assistance memo is complete.",
                assessment,
            )


class RetrievalOutageTests(unittest.TestCase):
    def test_structured_outage_is_mandatory_abstention(self):
        assessment = assess_degraded_mode(
            "SME-L001", retrieval_outages=("structured", "semantic")
        )
        self.assertEqual(assessment.mode, DegradedMode.MANDATORY_ABSTENTION)
        self.assertEqual(assessment.as_stance(), RecommendationStance.ABSTAIN)
        self.assertEqual(structured_facts_or_empty("SME-L001", "bank_inflows", assessment=assessment), ())
        self.assertTrue(assessment.manual_underwriting_available)
        graph_only = assess_degraded_mode("SME-L001", retrieval_outages=("graph", "semantic"))
        self.assertEqual(graph_only.mode, DegradedMode.DECISION_CAN_CONTINUE)
        self.assertTrue(graph_only.bureau_available)
        with self.assertRaises(DegradedModeError):
            scan_generated_degraded_claims(
                "Invented bank inflows cover the structured outage.",
                assessment,
            )


if __name__ == "__main__":
    unittest.main()
