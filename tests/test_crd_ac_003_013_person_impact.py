"""CRD-AC-003 / CRD-AC-013 — sole trader, guarantor and adverse-factor grounding."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from credit_domain.model import PartyKind, RecommendationStance  # noqa: E402
from credit_domain.persons import (  # noqa: E402
    PersonImpactError,
    analyze_and_handoff,
    analyze_person_impact,
    refuse_entity_person_collapse,
    scan_generated_person_claims,
)


class Ac003SoleTraderTests(unittest.TestCase):
    def test_sme_l003_business_is_not_the_owner(self):
        analysis = analyze_person_impact("SME-L003")
        refuse_entity_person_collapse(analysis)
        kinds = {p.party_kind for p in analysis.affected_persons}
        self.assertEqual(
            kinds,
            {PartyKind.SOLE_TRADER_BUSINESS.value, PartyKind.NATURAL_PERSON.value},
        )
        self.assertIn("ORG-003", analysis.business_party_ids)
        self.assertIn("NP-003", analysis.natural_person_ids)
        owner = next(p for p in analysis.affected_persons if p.role == "OWNER")
        business = next(
            p for p in analysis.affected_persons if p.party_kind == PartyKind.SOLE_TRADER_BUSINESS.value
        )
        self.assertEqual(owner.decision_feature_eligible, "CONDITIONAL")
        self.assertTrue(owner.restricted_attrs_excluded)
        self.assertNotEqual(owner.party_id, business.party_id)
        self.assertTrue(analysis.restricted_eval_excluded)
        self.assertTrue(set(analysis.purposes) <= {"UNDERWRITING_RUNTIME", "UNDERWRITING_VERIFIED"})
        self.assertEqual(analysis.required_human_role, "CREDIT_ANALYST")
        self.assertEqual(analysis.adverse_factors, ())
        self.assertTrue(analysis.recourse.human_decision_required)
        self.assertFalse(analysis.recourse.ai_has_recourse_authority)

        analysis_out, rec, decline, adverse = analyze_and_handoff("SME-L003")
        self.assertEqual(rec.required_authority.role, "CREDIT_ANALYST")
        self.assertEqual(decline.effect, "DENY")
        self.assertEqual(adverse.effect, "DENY")
        scan_generated_person_claims(
            "Sole-trader business ORG-003 is distinct from owner NP-003. "
            "Owner features are CONDITIONAL. Restricted eval attributes excluded.",
            analysis_out,
        )
        with self.assertRaises(PersonImpactError):
            scan_generated_person_claims(
                "The owner is age 42 and that personal attribute supports approval.",
                analysis,
            )


class Ac013AdverseGuarantorTests(unittest.TestCase):
    def test_sme_l013_grounds_arrears_and_keeps_guarantor_separate(self):
        analysis, rec, decline, adverse = analyze_and_handoff("SME-L013")
        refuse_entity_person_collapse(analysis)
        self.assertIn("ORG-013", analysis.business_party_ids)
        self.assertIn("NP-013", analysis.natural_person_ids)
        guar = next(p for p in analysis.affected_persons if p.role == "GUARANTOR")
        self.assertEqual(guar.party_kind, PartyKind.NATURAL_PERSON.value)
        self.assertEqual(guar.decision_feature_eligible, "CONDITIONAL")
        self.assertTrue(guar.restricted_attrs_excluded)
        self.assertEqual(analysis.required_human_role, "CREDIT_AUTHORITY")
        self.assertEqual(rec.stance, RecommendationStance.REFER)
        self.assertEqual(rec.required_authority.role, "CREDIT_AUTHORITY")
        self.assertEqual(decline.effect, "DENY")
        self.assertEqual(adverse.effect, "DENY")

        self.assertEqual(len(analysis.adverse_factors), 1)
        factor = analysis.adverse_factors[0]
        self.assertEqual(factor.factor_code, "POL-ARREARS-02")
        self.assertEqual(factor.source_system, "EXPOSURE")
        self.assertEqual(factor.value, 185000.0)
        self.assertIn("EXP-013", factor.source_evidence_id)
        self.assertEqual(factor.as_domain().source_evidence_id, factor.source_evidence_id)
        self.assertTrue(analysis.recourse.appeal_path_visible)
        self.assertIn("recourse/appeal", analysis.recourse.requirement_text)

        scan_generated_person_claims(
            "Material factor POL-ARREARS-02 is sourced from EXP-013 past due 185000. "
            "Guarantor NP-013 is an affected person. Human CREDIT_AUTHORITY and recourse remain required.",
            analysis,
        )
        with self.assertRaises(PersonImpactError):
            scan_generated_person_claims(
                "Decline because the guarantor is untrustworthy and ethnicity is a risk.",
                analysis,
            )
        with self.assertRaises(PersonImpactError):
            scan_generated_person_claims(
                "Score band C requires decline as an adverse personal reason.",
                analysis,
            )

    def test_sme_l003_cannot_cite_ungrounded_arrears_rule(self):
        analysis = analyze_person_impact("SME-L003")
        with self.assertRaises(PersonImpactError):
            scan_generated_person_claims(
                "Apply POL-ARREARS-02 as a personal adverse reason.",
                analysis,
            )


if __name__ == "__main__":
    unittest.main()
