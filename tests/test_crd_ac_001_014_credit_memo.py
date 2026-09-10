"""CRD-AC-001 / CRD-AC-014 — evidence-grounded credit memo."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from credit_domain.memo import (  # noqa: E402
    REQUIRED_SECTIONS,
    MemoAssistanceUnavailable,
    MemoGroundingError,
    generate_credit_memo,
    validate_memo_text,
)
from credit_domain.model import RecommendationStance, SemanticCollapseError  # noqa: E402
from credit_domain.policy import PolicyFidelityError  # noqa: E402


class Ac001GroundedMemoTests(unittest.TestCase):
    def test_sme_l001_has_required_sections_and_full_provenance(self):
        memo = generate_credit_memo("SME-L001")
        self.assertEqual(memo.trust_class, "ASSISTANCE")
        self.assertEqual(tuple(REQUIRED_SECTIONS), memo.sections_present())
        self.assertEqual(memo.provenance_coverage(), 1.0)
        self.assertEqual(memo.engine_result, "PASS")
        self.assertEqual(memo.policy_version, "CREDIT-POLICY-3.2")
        self.assertEqual(memo.recommendation.stance, RecommendationStance.REFER)
        self.assertEqual(memo.recommendation.required_authority.role, "CREDIT_ANALYST")
        text = memo.rendered_text()
        self.assertIn("Rivermint Foods Pvt Ltd", text)
        self.assertIn("9126438.87", text)
        self.assertIn("9407915.21", text)
        self.assertNotIn("averaged revenue", text.lower())
        self.assertIn("[INFERENCE]", text)
        self.assertIn("not the final credit decision", text.lower())
        with self.assertRaises(SemanticCollapseError):
            memo.as_human_decision()
        domain = memo.as_domain()
        with self.assertRaises(SemanticCollapseError):
            domain.as_human_decision()
        with self.assertRaises(MemoGroundingError):
            validate_memo_text(
                "This is the final credit decision. The application is approved.",
                "SME-L001",
            )


class Ac014MemoThresholdTests(unittest.TestCase):
    def test_sme_l014_memo_rejects_invented_threshold(self):
        memo = generate_credit_memo("SME-L014")
        self.assertEqual(memo.engine_result, "PASS")
        self.assertIn("1950000", memo.rendered_text())
        self.assertEqual(memo.recommendation.required_authority.role, "CREDIT_ANALYST")
        with self.assertRaises(PolicyFidelityError):
            validate_memo_text(
                "Approve working-capital facilities below INR 2,500,000 per policy.",
                "SME-L014",
            )


class ConflictAndOutageMemoTests(unittest.TestCase):
    def test_sme_l011_keeps_bank_and_tax_unblended(self):
        memo = generate_credit_memo("SME-L011")
        conflict = " ".join(s.text for s in memo.statements_for("CONFLICTS"))
        self.assertIn("11068375.24", conflict)
        self.assertIn("17709400.38", conflict)
        self.assertIn("not averaged", conflict)

    def test_sme_l010_does_not_fabricate_memo_during_ai_outage(self):
        with self.assertRaises(MemoAssistanceUnavailable):
            generate_credit_memo("SME-L010")


if __name__ == "__main__":
    unittest.main()
