"""CRD-AC-007 / CRD-AC-012 / CRD-AC-014 — policy-as-authority contract."""

from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from credit_domain.model import (  # noqa: E402
    ExceptionClass,
    RecommendationStance,
    SemanticCollapseError,
)
from credit_domain.policy import (  # noqa: E402
    PolicyFidelityError,
    PolicyUnavailable,
    apply_bundle_as_controlling,
    bureau_available,
    evaluate_application,
    invent_delegated_authority,
    invent_exception_criteria,
    load_policy_catalog,
    rank_policy_documents,
    require_active_policy,
    retrieve_active_policy,
    scan_generated_policy_claims,
    use_similarity_hit_as_authority,
)


class ActivePolicyRetrievalTests(unittest.TestCase):
    def test_workshop_as_of_selects_credit_policy_3_2(self):
        retrieval = retrieve_active_policy("2026-09-15")
        self.assertFalse(retrieval.abstain)
        self.assertIsNotNone(retrieval.controlling)
        self.assertEqual(retrieval.controlling_version, "CREDIT-POLICY-3.2")
        self.assertEqual(retrieval.controlling.status, "ACTIVE")
        self.assertEqual(retrieval.controlling.effective_date, date(2026, 7, 1))
        self.assertTrue(retrieval.controlling.controlling)
        self.assertEqual(retrieval.controlling.known_inr_amounts, (5_000_000,))
        self.assertEqual(retrieval.controlling.known_day_limits, (7,))
        self.assertIn("AUTH-LIMIT-01", retrieval.controlling.known_rule_ids)
        historical = {b.version: b for b in retrieval.historical}
        self.assertIn("CREDIT-POLICY-2.9", historical)
        self.assertFalse(historical["CREDIT-POLICY-2.9"].controlling)
        self.assertEqual(historical["CREDIT-POLICY-2.9"].status, "SUPERSEDED")

    def test_explicit_v29_request_is_not_controlling(self):
        retrieval = retrieve_active_policy("2026-09-15", version="CREDIT-POLICY-2.9")
        self.assertEqual(retrieval.controlling_version, "CREDIT-POLICY-3.2")
        self.assertTrue(retrieval.historical[0].version == "CREDIT-POLICY-2.9")
        self.assertFalse(retrieval.historical[0].controlling)
        with self.assertRaises(PolicyFidelityError):
            apply_bundle_as_controlling(retrieval.historical[0])

    def test_before_effective_date_abstains_instead_of_applying_v29(self):
        retrieval = retrieve_active_policy("2026-06-15")
        self.assertTrue(retrieval.abstain)
        self.assertIsNone(retrieval.controlling)
        self.assertIn("do not invent", retrieval.abstain_reason)
        with self.assertRaises(PolicyUnavailable):
            require_active_policy("2026-06-15")
        view = evaluate_application("SME-L014", as_of="2026-06-15")
        self.assertEqual(view.stance, RecommendationStance.ABSTAIN)
        self.assertIsNone(view.engine)


class Ac012SupersededPolicyTrapTests(unittest.TestCase):
    def test_sme_l012_uses_active_32_and_engine_credit_authority(self):
        view = evaluate_application("SME-L012")
        engine = view.require_engine()
        self.assertEqual(view.retrieval.controlling_version, "CREDIT-POLICY-3.2")
        self.assertEqual(engine.policy_version, "CREDIT-POLICY-3.2")
        self.assertEqual(engine.result, "REQUIRES_CREDIT_AUTHORITY")
        self.assertEqual(engine.triggered_rule_ids, ("AUTH-LIMIT-01",))
        self.assertEqual(engine.required_human_role, "CREDIT_AUTHORITY")
        self.assertEqual(view.required_human_role, "CREDIT_AUTHORITY")
        self.assertEqual(view.requested_limit, 6_100_000)
        self.assertGreater(view.requested_limit, 5_000_000)
        self.assertEqual(view.los_assigned_role, "SENIOR_UNDERWRITER")
        self.assertNotEqual(view.los_assigned_role, engine.required_human_role)
        self.assertEqual(view.stance, RecommendationStance.REFER)
        catalog = load_policy_catalog()
        self.assertEqual(catalog["CREDIT-POLICY-2.9"].known_inr_amounts, ())

    def test_similarity_ranks_v29_but_cannot_select_authority(self):
        query = "former large-limit escalation boundary"
        hits = rank_policy_documents(query)
        self.assertEqual(hits[0].version, "CREDIT-POLICY-2.9")
        self.assertFalse(hits[0].controlling)
        with self.assertRaises(PolicyFidelityError) as ctx:
            use_similarity_hit_as_authority(query)
        self.assertIn("similarity cannot choose policy authority", str(ctx.exception))
        retrieval = retrieve_active_policy(
            "2026-09-15",
            context={"query": query, "application_id": "SME-L012"},
        )
        self.assertEqual(retrieval.controlling_version, "CREDIT-POLICY-3.2")


class Ac007TrueExceptionTests(unittest.TestCase):
    def test_sme_l007_is_policy_exception_not_missing_data(self):
        view = evaluate_application("SME-L007")
        engine = view.require_engine()
        self.assertEqual(view.retrieval.controlling_version, "CREDIT-POLICY-3.2")
        self.assertEqual(engine.result, "EXCEPTION_REVIEW")
        self.assertEqual(engine.triggered_rule_ids, ("POL-EXC-07",))
        self.assertEqual(engine.required_human_role, "SENIOR_UNDERWRITER")
        self.assertEqual(view.required_human_role, "SENIOR_UNDERWRITER")
        self.assertEqual(view.exception_class, ExceptionClass.POLICY_EXCEPTION)
        self.assertNotEqual(view.exception_class, ExceptionClass.MISSING_EVIDENCE)
        self.assertEqual(view.requested_limit, 3_600_000)
        self.assertLess(view.requested_limit, 5_000_000)
        self.assertTrue(bureau_available("SME-L007"))

        missing = evaluate_application("SME-L006")
        missing_engine = missing.require_engine()
        self.assertEqual(missing_engine.result, "INSUFFICIENT_EVIDENCE")
        self.assertEqual(missing_engine.triggered_rule_ids, ("DATA-BUREAU-REQ",))
        self.assertEqual(missing.exception_class, ExceptionClass.MISSING_EVIDENCE)
        self.assertFalse(bureau_available("SME-L006"))
        self.assertNotEqual(engine.result, missing_engine.result)

    def test_pol_exc_07_criterion_cannot_be_invented(self):
        with self.assertRaises(PolicyFidelityError):
            invent_exception_criteria("POL-EXC-07")
        with self.assertRaises(PolicyFidelityError):
            scan_generated_policy_claims(
                "POL-EXC-07 fires when cashflow volatility exceeds 0.25."
            )


class Ac014InventedThresholdTests(unittest.TestCase):
    def test_sme_l014_engine_pass_is_not_approval(self):
        view = evaluate_application("SME-L014")
        engine = view.require_engine()
        self.assertEqual(engine.result, "PASS")
        self.assertEqual(engine.triggered_rule_ids, ())
        self.assertEqual(engine.required_human_role, "CREDIT_ANALYST")
        self.assertEqual(view.requested_limit, 1_950_000)
        self.assertEqual(view.stance, RecommendationStance.REFER)
        with self.assertRaises(SemanticCollapseError):
            view.refuse_pass_as_approve()
        scan_generated_policy_claims(
            "Engine result PASS under CREDIT-POLICY-3.2. "
            "Requested limit is INR 1,950,000 and is not above the documented "
            "INR 5,000,000 CREDIT_AUTHORITY boundary. No approval is issued.",
            application_id="SME-L014",
        )

    def test_invented_approval_threshold_is_rejected(self):
        with self.assertRaises(PolicyFidelityError) as ctx:
            scan_generated_policy_claims(
                "Approve working-capital facilities below INR 2,500,000 per policy.",
                application_id="SME-L014",
            )
        self.assertIn("invented credit threshold", str(ctx.exception))
        with self.assertRaises(PolicyFidelityError):
            scan_generated_policy_claims(
                "Delegated analyst authority is INR 3,000,000.",
                application_id="SME-L014",
            )
        with self.assertRaises(PolicyFidelityError):
            invent_delegated_authority(3_000_000)
        with self.assertRaises(PolicyFidelityError):
            scan_generated_policy_claims(
                "Policy requires decline when commercial score is C."
            )
        with self.assertRaises(PolicyFidelityError):
            scan_generated_policy_claims(
                "CREDIT-POLICY-2.9 threshold of INR 4,000,000 still applies."
            )

    def test_scan_abstains_when_active_policy_unavailable(self):
        with self.assertRaises(PolicyUnavailable):
            scan_generated_policy_claims(
                "Approve if requested limit is below INR 5,000,000.",
                as_of="2026-06-01",
            )


if __name__ == "__main__":
    unittest.main()
