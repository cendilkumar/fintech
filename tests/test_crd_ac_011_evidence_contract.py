"""CRD-AC-011 / GS-11 — provenance-bearing evidence; no silent bank/tax reconcile."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from credit_domain.evidence import (  # noqa: E402
    REQUIRED_ENVELOPE_FIELDS,
    assemble_application_evidence,
)
from credit_domain.model import ExceptionClass, MeasureKind, SemanticCollapseError  # noqa: E402

SME_L011_BANK_INFLOWS = 11068375.24
SME_L011_TAX_TURNOVER = 17709400.38


class CRDAC011EvidenceContractTests(unittest.TestCase):
    def setUp(self):
        self.pack = assemble_application_evidence("SME-L011")

    def test_five_source_systems_emit_envelopes(self):
        sources = {f.source_system for f in self.pack.facts}
        self.assertEqual(sources, {"LOS", "BANK", "BUREAU", "TAX", "EXPOSURE"})

    def test_every_material_fact_has_required_provenance(self):
        self.assertGreaterEqual(len(self.pack.facts), 5)
        for fact in self.pack.facts:
            missing = fact.missing_fields()
            self.assertEqual(missing, [], msg=f"{fact.evidence_id} missing {missing}")
            payload = fact.as_dict()
            for field in REQUIRED_ENVELOPE_FIELDS:
                self.assertIn(field, payload)
            self.assertEqual(fact.retrieval_time, self.pack.retrieval_time)
            self.assertIsNone(fact.derivation_confidence)
            self.assertTrue(fact.source_record_id)
            self.assertTrue(fact.entity_ref)
            self.assertTrue(fact.period)
            self.assertTrue(fact.event_time)
            self.assertTrue(fact.version)
            self.assertTrue(fact.consent_status)
            self.assertTrue(fact.purpose)

    def test_bank_and_tax_values_are_unaltered_source_facts(self):
        bank = self.pack.fact(MeasureKind.BANK_INFLOWS_12M.value)
        tax = self.pack.fact(MeasureKind.TAX_DECLARED_TURNOVER.value)
        self.assertEqual(bank.value, SME_L011_BANK_INFLOWS)
        self.assertEqual(tax.value, SME_L011_TAX_TURNOVER)
        self.assertEqual(bank.source_system, "BANK")
        self.assertEqual(tax.source_system, "TAX")
        self.assertEqual(bank.source_record_id, "BANK-011")
        self.assertEqual(tax.source_record_id, "TAXREC-011")
        self.assertEqual(bank.authority, "authoritative")
        self.assertEqual(tax.authority, "authoritative")
        self.assertEqual(bank.purpose, "UNDERWRITING_RUNTIME")
        self.assertEqual(tax.consent_status, "CONDITIONAL")
        self.assertNotEqual(bank.semantic_type, tax.semantic_type)

    def test_conflict_is_unresolved_and_requires_human_handling(self):
        self.assertEqual(len(self.pack.conflicts), 1)
        conflict = self.pack.conflicts[0]
        self.assertEqual(conflict.conflict_state, "unresolved")
        self.assertTrue(conflict.human_reconciliation_required)
        self.assertEqual(conflict.exception_class, ExceptionClass.FINANCIAL_CONFLICT.value)
        self.assertIsNone(conflict.blended_value)
        self.assertEqual(conflict.left_source, "BANK")
        self.assertEqual(conflict.right_source, "TAX")
        self.assertEqual(
            {conflict.left_semantic_type, conflict.right_semantic_type},
            {MeasureKind.BANK_INFLOWS_12M.value, MeasureKind.TAX_DECLARED_TURNOVER.value},
        )
        bank = self.pack.fact(MeasureKind.BANK_INFLOWS_12M.value)
        tax = self.pack.fact(MeasureKind.TAX_DECLARED_TURNOVER.value)
        self.assertEqual(bank.conflict_state, "unresolved")
        self.assertEqual(tax.conflict_state, "unresolved")
        self.assertEqual(self.pack.exceptions[0].exception_class, ExceptionClass.FINANCIAL_CONFLICT)

    def test_does_not_average_or_choose_a_source(self):
        conflict = self.pack.conflicts[0]
        with self.assertRaises(SemanticCollapseError):
            conflict.average()
        with self.assertRaises(SemanticCollapseError):
            conflict.choose_one()
        with self.assertRaises(SemanticCollapseError):
            self.pack.blended_revenue()
        values = [
            f.value
            for f in self.pack.facts
            if f.semantic_type
            in {MeasureKind.BANK_INFLOWS_12M.value, MeasureKind.TAX_DECLARED_TURNOVER.value}
        ]
        blended = (SME_L011_BANK_INFLOWS + SME_L011_TAX_TURNOVER) / 2
        self.assertNotIn(blended, values)

    def test_policy_pass_does_not_clear_financial_conflict(self):
        self.assertEqual(self.pack.policy_result, "PASS")
        self.assertEqual(self.pack.policy_version, "CREDIT-POLICY-3.2")
        self.assertTrue(self.pack.conflicts)
        self.assertEqual(self.pack.conflicts[0].conflict_state, "unresolved")

    def test_los_bureau_exposure_are_not_substituted_for_bank_or_tax(self):
        los_limit = self.pack.fact("RequestedLimit")
        bureau = next(f for f in self.pack.facts if f.source_system == "BUREAU")
        exposure = self.pack.fact(MeasureKind.INTERNAL_EXISTING_EXPOSURE.value)
        self.assertEqual(los_limit.value, 1100000.0)
        self.assertEqual(los_limit.source_system, "LOS")
        self.assertEqual(bureau.semantic_type, "BureauRecord.score_band")
        self.assertEqual(bureau.value, "A")
        self.assertEqual(exposure.source_system, "EXPOSURE")
        self.assertEqual(exposure.source_record_id, "EXP-011")
        self.assertNotEqual(exposure.semantic_type, "BureauRecord")
        self.assertEqual(self.pack.tenant_id, "TENANT-ALPHA")
        self.assertEqual(los_limit.entity_ref, "ORG-011")

    def test_sme_l001_has_no_material_bank_tax_conflict(self):
        pack = assemble_application_evidence("SME-L001")
        self.assertEqual(pack.conflicts, [])
        bank = pack.fact(MeasureKind.BANK_INFLOWS_12M.value)
        tax = pack.fact(MeasureKind.TAX_DECLARED_TURNOVER.value)
        self.assertEqual(bank.conflict_state, "none")
        self.assertEqual(tax.conflict_state, "none")


if __name__ == "__main__":
    unittest.main()
