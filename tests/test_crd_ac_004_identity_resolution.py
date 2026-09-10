"""CRD-AC-004 / CRD-FR-003 — identity states; no silent LOS/bureau/tax merge."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from credit_domain.evidence import assemble_application_evidence  # noqa: E402
from credit_domain.identity import (  # noqa: E402
    SourceIdentityObservation,
    UnsafeIdentityUse,
    normalize_legal_name,
    resolve_application_identity,
    resolve_from_observations,
)
from credit_domain.model import ExceptionClass, ResolutionState  # noqa: E402


def _obs(application_id: str, source: str, source_id: str, name: str, tax: str) -> SourceIdentityObservation:
    return SourceIdentityObservation(
        application_id=application_id,
        source=source,
        source_id=source_id,
        observed_name=name,
        tax_token=tax,
        canonical_candidate="ORG-HYPOTHESIS",
    )


class LegalEntityResolutionTests(unittest.TestCase):
    def test_sme_l004_is_ambiguous_and_not_merged(self):
        resolution = resolve_application_identity("SME-L004")
        self.assertEqual(resolution.state, ResolutionState.AMBIGUOUS)
        names = {o.observed_name for o in resolution.organization.observations}
        tokens = {o.tax_token for o in resolution.organization.observations}
        self.assertIn("Blueharbor Textiles Pvt Ltd", names)
        self.assertIn("Blue Harbour Textiles Private Limited", names)
        self.assertIn("Blueharbour Textile Industries Pvt Ltd", names)
        self.assertIn("TAX-***44", tokens)
        self.assertIn("TAX-***XX", tokens)
        self.assertEqual(resolution.organization.hypothesized_candidate, "ORG-004")
        self.assertIsNone(resolution.organization.canonical_party_id)
        self.assertEqual(resolution.safe_entity_ref(), "AMBIGUOUS:SME-L004")
        with self.assertRaises(UnsafeIdentityUse):
            resolution.require_matched_party_id()
        with self.assertRaises(UnsafeIdentityUse):
            resolution.organization.merge_observations()
        self.assertEqual(resolution.exceptions[0].exception_class, ExceptionClass.IDENTITY)
        pack = assemble_application_evidence("SME-L004")
        self.assertEqual(pack.identity.state, ResolutionState.AMBIGUOUS)
        self.assertTrue(all(f.entity_ref == "AMBIGUOUS:SME-L004" for f in pack.facts))
        self.assertNotIn("ORG-004", {f.entity_ref for f in pack.facts})

    def test_aligned_legal_entity_is_matched(self):
        resolution = resolve_application_identity("SME-L001")
        self.assertEqual(resolution.state, ResolutionState.MATCHED)
        self.assertEqual(resolution.require_matched_party_id(), "ORG-001")
        names = {o.normalized_name for o in resolution.organization.observations}
        self.assertEqual(len(names), 1)
        self.assertEqual({o.tax_token for o in resolution.organization.observations}, {"TAX-***41"})
        pack = assemble_application_evidence("SME-L001")
        self.assertEqual(pack.identity.safe_entity_ref(), "ORG-001")

    def test_legal_name_suffix_variation_can_match_when_tax_agrees(self):
        cluster = resolve_from_observations(
            "SYN-SUFFIX",
            [
                _obs("SYN-SUFFIX", "LOS", "LOS-1", "Rivermint Foods Pvt Ltd", "TAX-***41"),
                _obs("SYN-SUFFIX", "BUREAU", "BUR-1", "Rivermint Foods Private Limited", "TAX-***41"),
                _obs("SYN-SUFFIX", "TAX", "TAX-1", "Rivermint Foods Pvt. Ltd.", "TAX-***41"),
            ],
            hypothesized_candidate="ORG-IGNORED",
        )
        self.assertEqual(cluster.state, ResolutionState.MATCHED)
        self.assertEqual(
            {normalize_legal_name(o.observed_name) for o in cluster.observations},
            {"rivermint foods pvt ltd"},
        )
        self.assertEqual(cluster.hypothesized_candidate, "ORG-IGNORED")

    def test_tax_identifier_mismatch_is_ambiguous(self):
        cluster = resolve_from_observations(
            "SYN-TAX",
            [
                _obs("SYN-TAX", "LOS", "LOS-1", "Same Name Pvt Ltd", "TAX-***44"),
                _obs("SYN-TAX", "BUREAU", "BUR-1", "Same Name Pvt Ltd", "TAX-***99"),
                _obs("SYN-TAX", "TAX", "TAX-1", "Same Name Pvt Ltd", "TAX-***44"),
            ],
        )
        self.assertEqual(cluster.state, ResolutionState.AMBIGUOUS)
        with self.assertRaises(UnsafeIdentityUse):
            cluster.require_matched_party_id()

    def test_placeholder_bureau_tax_token_is_ambiguous(self):
        cluster = resolve_from_observations(
            "SYN-XX",
            [
                _obs("SYN-XX", "LOS", "LOS-1", "Blueharbor Textiles Pvt Ltd", "TAX-***44"),
                _obs("SYN-XX", "BUREAU", "BUR-1", "Blueharbor Textiles Pvt Ltd", "TAX-***XX"),
                _obs("SYN-XX", "TAX", "TAX-1", "Blueharbor Textiles Pvt Ltd", "TAX-***44"),
            ],
        )
        self.assertEqual(cluster.state, ResolutionState.AMBIGUOUS)

    def test_missing_bureau_is_unresolved(self):
        resolution = resolve_application_identity("SME-L006")
        self.assertEqual(resolution.state, ResolutionState.UNRESOLVED)
        self.assertNotIn("BUREAU", {o.source for o in resolution.organization.observations})
        with self.assertRaises(UnsafeIdentityUse):
            resolution.require_matched_party_id()
        pack = assemble_application_evidence("SME-L006")
        self.assertEqual(pack.identity.safe_entity_ref(), "UNRESOLVED:SME-L006")
        self.assertTrue(any(e.exception_class == ExceptionClass.IDENTITY for e in pack.exceptions))

    def test_sole_trader_business_is_not_the_owner(self):
        resolution = resolve_application_identity("SME-L003")
        self.assertEqual(resolution.state, ResolutionState.MATCHED)
        self.assertEqual(resolution.require_matched_party_id(), "ORG-003")
        self.assertEqual(len(resolution.natural_persons), 1)
        owner = resolution.natural_persons[0]
        self.assertEqual(owner.cluster_kind, "NATURAL_PERSON_OWNER")
        self.assertEqual(owner.observations[0].tax_token, "PAN-***73")
        self.assertTrue(resolution.person_not_merged_with_organization())
        self.assertNotEqual(owner.observations[0].source_id, "LOS-CUST-1003")

    def test_guarantor_is_not_merged_into_applicant_entity(self):
        for app_id, guarantor_id, org_state in (
            ("SME-L004", "LOS-NP-2004", ResolutionState.AMBIGUOUS),
            ("SME-L013", "LOS-NP-2013", ResolutionState.MATCHED),
        ):
            resolution = resolve_application_identity(app_id)
            self.assertEqual(resolution.state, org_state, app_id)
            kinds = {c.cluster_kind for c in resolution.natural_persons}
            self.assertIn("NATURAL_PERSON_GUARANTOR", kinds, app_id)
            self.assertTrue(resolution.person_not_merged_with_organization(), app_id)
            person_ids = {o.source_id for c in resolution.natural_persons for o in c.observations}
            self.assertIn(guarantor_id, person_ids, app_id)
            org_ids = {o.source_id for o in resolution.organization.observations}
            self.assertNotIn(guarantor_id, org_ids, app_id)

    def test_crosswalk_candidate_never_implies_matched(self):
        resolution = resolve_application_identity("SME-L004")
        self.assertEqual(resolution.organization.hypothesized_candidate, "ORG-004")
        self.assertNotEqual(resolution.state, ResolutionState.MATCHED)
        self.assertIsNone(resolution.organization.canonical_party_id)


if __name__ == "__main__":
    unittest.main()
