"""CRD-AC-016 / CRD-FR-002 — semantic non-collapse against live fixtures."""

from __future__ import annotations

import csv
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from credit_domain.model import (  # noqa: E402
    Applicant,
    Authority,
    BureauRecord,
    CreditMemo,
    DecisionOutcome,
    Evidence,
    ExceptionClass,
    ExceptionRecord,
    Exposure,
    FinancialMetric,
    Guarantor,
    HumanDecision,
    IdentityObservation,
    LegalEntity,
    MeasureKind,
    NaturalPerson,
    PartyKind,
    PolicyEvaluation,
    Recommendation,
    RecommendationStance,
    ResolutionState,
    SemanticCollapseError,
    SoleTraderBusiness,
    map_source_field,
    party_from_fixture,
    refuse_average,
    refuse_policy_pass_as_approve,
)


def _csv(name: str):
    with (ROOT / "evidence/01_enterprise_sources" / name).open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _jsonl(name: str):
    path = ROOT / "evidence/01_enterprise_sources" / name
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _crosswalk():
    with (ROOT / "evidence/03_semantic_evidence/identifier_crosswalk.csv").open(
        newline="", encoding="utf-8"
    ) as fh:
        return list(csv.DictReader(fh))


class SemanticNonCollapseTests(unittest.TestCase):
    def test_required_types_importable(self):
        from credit_domain import (  # noqa: F401
            Applicant,
            Application,
            Authority,
            BankTransaction,
            BureauRecord,
            Consent,
            CreditMemo,
            Evidence,
            ExceptionRecord,
            Exposure,
            Facility,
            FinancialMetric,
            Guarantor,
            HumanDecision,
            LegalEntity,
            NaturalPerson,
            Policy,
            PolicyEvaluation,
            PolicyRule,
            Recommendation,
            RequestedLimit,
            SoleTraderBusiness,
            TaxFiling,
        )

    def test_legal_entity_is_not_natural_person(self):
        org = LegalEntity("ORG-001", "Rivermint Foods Pvt Ltd", "LOS-CUST-1001")
        person = NaturalPerson("NP-003", "Owner 3", "LOS-NP-2003")
        self.assertIsNot(type(org), type(person))
        self.assertNotEqual(org.kind, person.kind)
        with self.assertRaises(SemanticCollapseError):
            LegalEntity("X", "Y", "Z", kind=PartyKind.NATURAL_PERSON)

    def test_sme_l003_sole_trader_parties_stay_split(self):
        rows = [r for r in _csv("application_parties.csv") if r["application_id"] == "SME-L003"]
        parties = [party_from_fixture(r) for r in rows]
        kinds = {type(p) for p in parties}
        self.assertIn(SoleTraderBusiness, kinds)
        self.assertIn(NaturalPerson, kinds)
        self.assertNotIn(LegalEntity, kinds)
        business = next(p for p in parties if isinstance(p, SoleTraderBusiness))
        owner = next(p for p in parties if isinstance(p, NaturalPerson))
        self.assertNotEqual(business.party_id, owner.party_id)
        Applicant("SME-L003", business, is_primary=True)
        Applicant("SME-L003", owner, is_primary=True)

    def test_guarantor_is_role_not_borrower_entity(self):
        np = NaturalPerson("NP-013", "Guarantor 13", "LOS-NP-2013")
        org = LegalEntity("ORG-013", "Saffron Hill Services Pvt Ltd", "LOS-CUST-1013")
        Guarantor("SME-L013", np)
        with self.assertRaises(SemanticCollapseError):
            Guarantor("SME-L013", org)

    def test_generic_revenue_kind_rejected(self):
        with self.assertRaises(SemanticCollapseError):
            FinancialMetric(measure_kind="revenue", value=1.0, source_system="BANK")
        with self.assertRaises(SemanticCollapseError):
            map_source_field("BANK", "revenue", 100)

    def test_sme_l011_bank_and_tax_remain_distinct(self):
        bank = next(x for x in _jsonl("bank_financial_summaries.jsonl") if x["application_id"] == "SME-L011")
        tax = next(x for x in _jsonl("tax_gst_records.jsonl") if x["application_id"] == "SME-L011")
        inflow = map_source_field(
            "BANK", "twelve_month_inflows", bank["twelve_month_inflows"], source_record_id=bank["bank_summary_id"]
        )
        turnover = map_source_field(
            "TAX",
            "declared_turnover",
            tax["declared_turnover"],
            source_record_id=tax["tax_record_id"],
            period=tax["filing_period"],
        )
        self.assertIsInstance(inflow, FinancialMetric)
        self.assertIsInstance(turnover, FinancialMetric)
        self.assertEqual(inflow.measure_kind, MeasureKind.BANK_INFLOWS_12M)
        self.assertEqual(turnover.measure_kind, MeasureKind.TAX_DECLARED_TURNOVER)
        self.assertNotAlmostEqual(inflow.value, turnover.value)
        with self.assertRaises(SemanticCollapseError):
            refuse_average(inflow, turnover)
        with self.assertRaises(SemanticCollapseError):
            FinancialMetric(
                measure_kind=MeasureKind.TAX_DECLARED_TURNOVER,
                value=inflow.value,
                source_system="BANK",
            )

    def test_bureau_record_is_not_exposure(self):
        bur = next(x for x in _jsonl("bureau_reports.jsonl") if x["application_id"] == "SME-L001")
        bureau = map_source_field(
            "BUREAU",
            "commercial_score_band",
            bur["commercial_score_band"],
            source_record_id=bur["bureau_report_id"],
            reported_name=bur["reported_name"],
        )
        self.assertIsInstance(bureau, BureauRecord)
        exp_row = next(r for r in _csv("exposure_records.csv") if r["application_id"] == "SME-L001")
        exposure = Exposure(
            existing_exposure=float(exp_row["existing_exposure"]),
            approved_limit=float(exp_row["approved_limit_current"]),
            past_due=float(exp_row["past_due_amount"]),
            source_update_time=exp_row["source_update_time"],
        )
        self.assertIsInstance(exposure, Exposure)
        self.assertNotEqual(type(bureau), type(exposure))
        with self.assertRaises(SemanticCollapseError):
            FinancialMetric(
                measure_kind=MeasureKind.INTERNAL_EXISTING_EXPOSURE,
                value=1.0,
                source_system="BUREAU",
            )

    def test_recommendation_is_not_human_decision(self):
        rec = Recommendation(
            stance=RecommendationStance.PROPOSE_APPROVE,
            required_authority=Authority(role="CREDIT_ANALYST", final_credit_decision="LIMITED_IF_POLICY_ALLOWS"),
            application_id="SME-L001",
        )
        with self.assertRaises(SemanticCollapseError):
            rec.as_human_decision()
        memo = CreditMemo("MEMO-001", "SME-L001", recommendation=rec)
        with self.assertRaises(SemanticCollapseError):
            memo.as_human_decision()
        with self.assertRaises(SemanticCollapseError):
            HumanDecision(
                outcome=DecisionOutcome.APPROVE,
                actor_role="AI_AGENT",
                policy_version="CREDIT-POLICY-3.2",
                application_id="SME-L001",
            )
        with self.assertRaises(SemanticCollapseError):
            Authority(role="AI_AGENT", final_credit_decision="YES")

    def test_policy_pass_is_not_approve(self):
        evaluation = map_source_field(
            "POLICY",
            "result",
            "PASS",
            policy_version="CREDIT-POLICY-3.2",
            required_human_role="CREDIT_ANALYST",
        )
        self.assertIsInstance(evaluation, PolicyEvaluation)
        self.assertFalse(evaluation.is_human_approval)
        with self.assertRaises(SemanticCollapseError):
            refuse_policy_pass_as_approve(evaluation)

    def test_sme_l004_crosswalk_candidate_is_not_matched(self):
        rows = [r for r in _crosswalk() if r["application_id"] == "SME-L004"]
        self.assertEqual(len(rows), 3)
        names = {r["observed_name"] for r in rows}
        tokens = {r["tax_token"] for r in rows}
        self.assertGreater(len(names), 1)
        self.assertGreater(len(tokens), 1)
        observations = [
            IdentityObservation(
                application_id="SME-L004",
                source=r["source"],
                observed_name=r["observed_name"],
                tax_token=r["tax_token"],
                source_id=r["source_id"],
                canonical_candidate=r["canonical_candidate"],
                resolution_state=ResolutionState.AMBIGUOUS,
            )
            for r in rows
        ]
        self.assertTrue(all(o.resolution_state is ResolutionState.AMBIGUOUS for o in observations))
        with self.assertRaises(SemanticCollapseError):
            IdentityObservation(
                application_id="SME-L004",
                source="LOS",
                observed_name=rows[0]["observed_name"],
                tax_token=rows[0]["tax_token"],
                source_id=rows[0]["source_id"],
                canonical_candidate=rows[0]["canonical_candidate"],
                resolution_state=ResolutionState.MATCHED,
            )

    def test_ocr_confidence_is_not_creditworthiness(self):
        ev = Evidence(
            evidence_id="DOC-001-FIN",
            source_system="DOCS",
            semantic_type="Evidence",
            source_record_id="DOC-001-FIN",
            extraction_confidence=0.945,
        )
        with self.assertRaises(SemanticCollapseError):
            ev.as_creditworthiness_confidence()

    def test_exception_classes_remain_split(self):
        missing = ExceptionRecord(ExceptionClass.MISSING_EVIDENCE, "SME-L006")
        policy_exc = ExceptionRecord(ExceptionClass.POLICY_EXCEPTION, "SME-L007")
        self.assertNotEqual(missing.exception_class, policy_exc.exception_class)


if __name__ == "__main__":
    unittest.main()
