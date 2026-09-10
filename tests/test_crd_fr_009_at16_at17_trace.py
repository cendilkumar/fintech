"""CRD-FR-009 / AT-16 / AT-17 — reconstructable underwriting trace."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from credit_domain.authority import handoff_recommendation  # noqa: E402
from credit_domain.model import DecisionOutcome, SemanticCollapseError  # noqa: E402
from credit_domain.trace import (  # noqa: E402
    FORBIDDEN_TRACE_KEYS,
    REQUIRED_TRACE_FIELDS,
    TraceIntegrityError,
    attach_human_action,
    record_decision_trace,
    validate_trace,
)


class At16ReconstructableTraceTests(unittest.TestCase):
    def test_gs01_records_required_fields_and_source_financials(self):
        trace = record_decision_trace("SME-L001")
        payload = trace.to_dict()
        for field in REQUIRED_TRACE_FIELDS:
            self.assertIn(field, payload, field)
        self.assertEqual(trace.policy_version, "CREDIT-POLICY-3.2")
        self.assertEqual(trace.authority_required, "CREDIT_ANALYST")
        self.assertEqual(trace.recommendation["stance"], "REFER")
        self.assertEqual(trace.recommendation["trust_class"], "ASSISTANCE")
        self.assertEqual(trace.human_action["status"], "PENDING")
        self.assertEqual(trace.final_outcome["status"], "UNKNOWN")
        calcs = {item.name: item for item in trace.financial_calculations}
        self.assertEqual(calcs["requested_limit"].value, 1200000.0)
        self.assertEqual(calcs["bank_inflows_12m"].value, 9126438.87)
        self.assertEqual(calcs["tax_declared_turnover"].value, 9407915.21)
        self.assertEqual(calcs["existing_exposure"].value, 584194.1)
        self.assertFalse(calcs["bank_to_tax_visibility_ratio"].is_policy_threshold)
        self.assertIn("not_a_credit_threshold", calcs["bank_to_tax_visibility_ratio"].derivation)
        sources = {item.source for item in trace.source_evidence}
        self.assertTrue({"LOS", "BANK", "TAX", "EXPOSURE", "BUREAU"} <= sources)
        self.assertTrue(all(item.purpose for item in trace.source_evidence))
        self.assertTrue(any(hop["family"] == "policy" and hop["controlling"] for hop in trace.retrieval_route))
        bundle = next(item for item in trace.policy_evidence if item["kind"] == "POLICY_BUNDLE")
        self.assertIn("credit_underwriting_policy_v3_2.md", bundle["source_ref"])
        engine = next(item for item in trace.policy_evidence if item["kind"] == "POLICY_ENGINE")
        self.assertEqual(engine["source_ref"], "policy_engine_results.jsonl:SME-L001")
        self.assertNotIn("chain_of_thought", json.dumps(payload))
        with self.assertRaises(TraceIntegrityError):
            trace.as_human_decision()

    def test_gs07_exception_uses_engine_policy_not_generated_criteria(self):
        trace = record_decision_trace("SME-L007")
        self.assertEqual(trace.authority_required, "SENIOR_UNDERWRITER")
        self.assertEqual(trace.exceptions[0]["exception_class"], "POLICY_EXCEPTION")
        self.assertIn("POL-EXC-07", trace.exceptions[0]["triggered_rule_ids"])
        self.assertEqual(trace.exceptions[0]["source_ref"], "policy_engine_results.jsonl:SME-L007")
        self.assertIn("not policy evidence", trace.concise_rationale)
        with self.assertRaises(TraceIntegrityError):
            trace.use_generated_explanation_as_policy(
                "POL-EXC-07 applies when seasonal turnover exceeds the documented variance."
            )
        rec = handoff_recommendation("SME-L007")
        with self.assertRaises(TraceIntegrityError):
            record_decision_trace("SME-L007", human_decision=rec)  # type: ignore[arg-type]

    def test_gs13_adverse_keeps_human_authority_and_source_evidence(self):
        trace = record_decision_trace("SME-L013")
        self.assertEqual(trace.authority_required, "CREDIT_AUTHORITY")
        self.assertEqual(trace.exceptions[0]["exception_class"], "ADVERSE")
        self.assertIn("POL-ARREARS-02", trace.exceptions[0]["triggered_rule_ids"])
        past_due = next(item for item in trace.source_evidence if item.semantic_type == "INTERNAL_PAST_DUE")
        self.assertEqual(past_due.value, 185000.0)
        self.assertEqual(trace.human_action["status"], "PENDING")
        self.assertEqual(trace.versions["model"], "NONE")
        self.assertEqual(trace.versions["prompt"], "NONE")
        self.assertEqual(trace.versions["policy_bundle"], "CREDIT-POLICY-3.2")


class At17NoHiddenCotTests(unittest.TestCase):
    def test_serialized_trace_has_no_hidden_reasoning_fields(self):
        for application_id in ("SME-L001", "SME-L007", "SME-L013"):
            payload = record_decision_trace(application_id).to_dict()
            keys = set()

            def walk(node):
                if isinstance(node, dict):
                    keys.update(k.lower() for k in node)
                    for value in node.values():
                        walk(value)
                elif isinstance(node, list):
                    for value in node:
                        walk(value)

            walk(payload)
            self.assertTrue(FORBIDDEN_TRACE_KEYS.isdisjoint(keys), application_id)

    def test_human_refer_can_be_attached_without_becoming_ai_authority(self):
        trace = attach_human_action(
            "SME-L001",
            actor_role="CREDIT_ANALYST",
            outcome=DecisionOutcome.REFER.value,
        )
        self.assertEqual(trace.human_action["status"], "RECORDED")
        self.assertEqual(trace.human_action["actor_role"], "CREDIT_ANALYST")
        self.assertEqual(trace.final_outcome["status"], "REFER")
        validate_trace(trace)
        with self.assertRaises(SemanticCollapseError):
            attach_human_action("SME-L001", actor_role="AI_AGENT", outcome="APPROVE")


if __name__ == "__main__":
    unittest.main()
