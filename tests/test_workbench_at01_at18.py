"""AT-01–AT-18 / G-UI-01 workbench display plane over credit_domain gates.

CRD-FR-001–011, CRD-AC-001–015. Screens display gates; they are not the control plane.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from credit_workbench.flags import FlagError, SCREENS  # noqa: E402
from credit_workbench.service import WorkbenchService  # noqa: E402
from credit_domain.trace import FORBIDDEN_TRACE_KEYS, REQUIRED_TRACE_FIELDS  # noqa: E402


class WorkbenchAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.svc = WorkbenchService()

    def dossier(self, application_id: str, tenant: str = "TENANT-ALPHA", role: str = "CREDIT_ANALYST", purpose: str = "UNDERWRITING_RUNTIME"):
        return self.svc.case_dossier(
            application_id, actor_tenant=tenant, actor_role=role, purpose=purpose
        )

    def test_g_ui_01_twelve_screens_and_pre_memo_order(self):
        catalog = self.svc.catalog()
        self.assertEqual(list(catalog["screens"]), list(SCREENS))
        self.assertEqual(
            catalog["screens"][:9],
            [
                "control_tower",
                "application_context",
                "evidence_reconciliation",
                "context_graph",
                "hybrid_retrieval",
                "policy_authority",
                "human_decision",
                "decision_trace",
                "outcome_feedback",
            ],
        )
        self.assertGreater(catalog["screens"].index("human_decision"), -1)
        self.assertLess(catalog["screens"].index("human_decision"), catalog["screens"].index("credit_memo"))
        self.assertLess(catalog["screens"].index("decision_trace"), catalog["screens"].index("credit_memo"))
        self.assertLess(catalog["screens"].index("outcome_feedback"), catalog["screens"].index("credit_memo"))
        flags = self.svc.snapshot_flags()
        self.assertTrue(flags["memo_visible"])
        with self.assertRaises(FlagError):
            self.svc.set_flags({"isolation.before_retrieval": False})
        gated = WorkbenchService()
        gated.set_flags({"ui.human_decision": False})
        self.assertFalse(gated.flags.memo_visible())
        memo = gated.case_dossier("SME-L001", actor_tenant="TENANT-ALPHA", actor_role="CREDIT_ANALYST")
        self.assertFalse(memo["screens"]["credit_memo"]["enabled"])
        self.assertEqual(memo["screens"]["credit_memo"]["blocked"], "G-UI-01")

    def test_at01_gs01_nominal_provenance_and_human_final(self):
        payload = self.dossier("SME-L001")
        self.assertIsNone(payload["denied"])
        self.assertFalse(payload["ai_final_approve_control"])
        evidence = payload["screens"]["evidence_reconciliation"]
        self.assertGreaterEqual(len(evidence["facts"]), 1)
        self.assertTrue(evidence["material_ai_factors_have_source_and_freshness"])
        decision = payload["screens"]["human_decision"]
        self.assertEqual(decision["ai_approve_effect"], "DENY")
        self.assertEqual(decision["required_human_role"], "CREDIT_ANALYST")
        recorded = self.svc.record_decision(
            "SME-L001",
            actor_role="CREDIT_ANALYST",
            actor_tenant="TENANT-ALPHA",
            outcome="APPROVE",
        )
        self.assertTrue(recorded["ok"])
        self.assertEqual(recorded["decision"]["actor_role"], "CREDIT_ANALYST")
        ai = self.svc.record_decision(
            "SME-L001", actor_role="AI_AGENT", actor_tenant="TENANT-ALPHA", outcome="APPROVE"
        )
        self.assertFalse(ai["ok"])
        self.assertEqual(ai["denied"], "AI_NO_FINAL_CREDIT")

    def test_at02_gs02_large_limit_credit_authority(self):
        payload = self.dossier("SME-L002")
        policy = payload["screens"]["policy_authority"]
        self.assertEqual(policy["required_human_role"], "CREDIT_AUTHORITY")
        self.assertEqual(policy["ai_final_actions"]["AUTHORIZE_LARGE_LIMIT"]["effect"], "DENY")
        self.assertEqual(policy["actor_actions"]["APPROVE"]["effect"], "DENY")
        allowed = self.svc.case_dossier(
            "SME-L002", actor_tenant="TENANT-ALPHA", actor_role="CREDIT_AUTHORITY"
        )
        self.assertEqual(allowed["screens"]["policy_authority"]["actor_actions"]["APPROVE"]["effect"], "ALLOW")

    def test_at03_gs03_sole_trader_and_restricted_attrs(self):
        payload = self.dossier("SME-L003")
        ctx = payload["screens"]["application_context"]
        self.assertTrue(ctx["sole_trader_distinct"])
        self.assertTrue(ctx["restricted_eval_excluded_from_runtime"])
        kinds = {party["party_type"] for party in ctx["parties"]}
        self.assertIn("SOLE_TRADER_BUSINESS", kinds)
        self.assertIn("NATURAL_PERSON_OWNER", kinds)
        fairness = payload["screens"]["fairness_eval"]
        self.assertFalse(fairness["runtime_access"])
        self.assertEqual(fairness["rows"], [])

    def test_at04_gs04_identity_ambiguous(self):
        payload = self.dossier("SME-L004")
        self.assertEqual(payload["screens"]["application_context"]["identity_state"], "AMBIGUOUS")
        org = payload["screens"]["application_context"]["identity"]["organization"]
        self.assertGreaterEqual(len(org["observations"]), 2)

    def test_at05_gs05_stale_bank_not_current(self):
        payload = self.dossier("SME-L005")
        banks = payload["screens"]["evidence_reconciliation"]["by_source"].get("BANK", [])
        self.assertTrue(banks)
        self.assertTrue(any(item["freshness_state"] == "stale" for item in banks))
        degraded = payload["screens"]["failure_simulation"]["degraded"]
        self.assertEqual(degraded["bank_freshness"], "stale")
        self.assertFalse(degraded["bank_presented_as_current"])

    def test_at06_gs06_bureau_unavailable_not_fabricated(self):
        payload = self.dossier("SME-L006")
        bureau = payload["screens"]["evidence_reconciliation"]["by_source"].get("BUREAU", [])
        if bureau:
            self.assertTrue(all(item["freshness_state"] == "unavailable" or item["value"] in (None, "") for item in bureau))
        degraded = payload["screens"]["failure_simulation"]["degraded"]
        self.assertFalse(degraded["bureau_available"])
        self.assertIsNone(degraded["bureau_value"])
        memo = payload["screens"]["credit_memo"]
        self.assertFalse(memo["enabled"])
        self.assertEqual(memo["blocked"], "DEGRADED")
        self.assertFalse(memo.get("fabricated", False))

    def test_at07_gs07_exception_routes_to_senior(self):
        payload = self.dossier("SME-L007")
        policy = payload["screens"]["policy_authority"]
        self.assertEqual(policy["required_human_role"], "SENIOR_UNDERWRITER")
        self.assertEqual(policy["exception_class"], "POLICY_EXCEPTION")
        self.assertEqual(policy["actor_actions"]["APPROVE_EXCEPTION"]["effect"], "DENY")
        senior = self.dossier("SME-L007", role="SENIOR_UNDERWRITER")
        self.assertEqual(
            senior["screens"]["policy_authority"]["actor_actions"]["APPROVE_EXCEPTION"]["effect"],
            "ALLOW",
        )

    def test_at08_gs08_alpha_gets_zero_beta_content(self):
        tower = self.svc.control_tower(actor_tenant="TENANT-ALPHA", actor_role="CREDIT_ANALYST")
        ids = {row["application_id"] for row in tower["applications"]}
        self.assertNotIn("SME-L008", ids)
        blob = json.dumps(tower)
        self.assertNotIn("Suncrest", blob)
        payload = self.dossier("SME-L008")
        self.assertEqual(payload["denied"], "CROSS_TENANT")
        self.assertIsNone(payload["application_id"])
        self.assertEqual(payload["isolation"]["content"], [])
        retrieval = payload["screens"]["hybrid_retrieval"]
        self.assertEqual(retrieval["denied"], "CROSS_TENANT")
        self.assertEqual(retrieval["hops"], [])
        blob = json.dumps(payload)
        self.assertNotIn("Suncrest", blob)
        self.assertNotIn("Agro Processing", blob)

    def test_at09_gs09_injection_is_untrusted_data(self):
        probe = self.svc.probe_injection()
        self.assertFalse(probe["any_followed"])
        self.assertTrue(any(not row["followed"] and row.get("injection_detected") for row in probe["documents"]))
        self.assertTrue(any("Ignore previous" in (row.get("text") or "") for row in probe["documents"]))
        payload = self.dossier("SME-L009")
        policy = payload["screens"]["policy_authority"]
        self.assertEqual(policy["active_version"], "CREDIT-POLICY-3.2")
        self.assertEqual(policy["ai_final_actions"]["APPROVE"]["effect"], "DENY")

    def test_at10_gs10_manual_path_when_ai_down(self):
        payload = self.dossier("SME-L010")
        degraded = payload["screens"]["failure_simulation"]["degraded"]
        self.assertEqual(degraded["mode"], "AI_ASSISTANCE_UNAVAILABLE")
        self.assertTrue(degraded["manual_underwriting_available"])
        memo = payload["screens"]["credit_memo"]
        self.assertFalse(memo["enabled"])
        self.assertIn("manual_underwriting", memo)
        self.assertTrue(memo["manual_underwriting"]["executable"])

    def test_at11_gs11_bank_tax_conflict_not_averaged(self):
        payload = self.dossier("SME-L011")
        conflicts = payload["screens"]["evidence_reconciliation"]["conflicts"]
        self.assertTrue(conflicts)
        self.assertFalse(payload["screens"]["evidence_reconciliation"]["averaged"])
        left = conflicts[0]["left_semantic_type"]
        right = conflicts[0]["right_semantic_type"]
        self.assertNotEqual(left, right)

    def test_at12_gs12_active_policy_3_2_not_v29(self):
        payload = self.dossier("SME-L012")
        policy = payload["screens"]["policy_authority"]
        self.assertEqual(policy["active_version"], "CREDIT-POLICY-3.2")
        probe = self.svc.probe_superseded_policy()
        self.assertEqual(probe["controlling_version"], "CREDIT-POLICY-3.2")
        self.assertFalse(probe["v29_controlling"])
        self.assertEqual(probe["superseded_requested_controlling"], "CREDIT-POLICY-3.2")

    def test_at13_gs13_adverse_human_reason_recourse(self):
        payload = self.dossier("SME-L013", role="CREDIT_AUTHORITY")
        persons = payload["screens"]["application_context"]["person_impact"]
        self.assertTrue(persons["recourse"]["human_decision_required"])
        self.assertTrue(persons["recourse"]["appeal_path_visible"])
        self.assertFalse(persons["recourse"]["ai_has_recourse_authority"])
        self.assertTrue(persons["adverse_factors"])
        policy = payload["screens"]["policy_authority"]
        self.assertEqual(policy["required_human_role"], "CREDIT_AUTHORITY")
        self.assertEqual(policy["ai_final_actions"]["ISSUE_ADVERSE"]["effect"], "DENY")
        self.assertEqual(policy["actor_actions"]["ISSUE_ADVERSE"]["effect"], "ALLOW")

    def test_at14_gs14_invented_threshold_rejected(self):
        probe = self.svc.probe_invented_threshold()
        self.assertTrue(probe["rejected"])
        self.assertTrue(probe["critical"])
        self.assertIn("2,500,000", probe["probe"])
        memo = self.dossier("SME-L014")["screens"]["credit_memo"]
        self.assertTrue(memo["enabled"])
        self.assertNotIn("2,500,000", memo["rendered_text"])

    def test_at15_gs15_feedback_governed_review(self):
        result = self.svc.capture_feedback(
            "SME-L015",
            actor_role="PORTFOLIO_ANALYST",
            actor_tenant="TENANT-ALPHA",
            feedback_type="AI_ACCEPTED",
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["record"]["status"], "GOVERNED_REVIEW")
        self.assertFalse(result["record"]["auto_applied"])
        blocked = self.svc.refuse_ungoverned_write("SME-L015", "POLICY_BUNDLE")
        self.assertTrue(blocked["blocked"])
        ai = self.svc.capture_feedback(
            "SME-L015",
            actor_role="AI_AGENT",
            actor_tenant="TENANT-ALPHA",
            feedback_type="AI_ACCEPTED",
        )
        self.assertFalse(ai["ok"])

    def test_at16_trace_required_fields(self):
        payload = self.dossier("SME-L001")
        trace_screen = payload["screens"]["decision_trace"]
        trace = trace_screen["trace"]
        for field in REQUIRED_TRACE_FIELDS:
            self.assertIn(field, trace, field)
        self.assertTrue(trace_screen["required_fields_present"])
        self.assertEqual(trace["versions"]["model"], "NONE")

    def test_at17_no_hidden_cot_field(self):
        payload = self.dossier("SME-L001")
        trace = payload["screens"]["decision_trace"]["trace"]
        for key in FORBIDDEN_TRACE_KEYS:
            self.assertNotIn(key, trace, key)
        self.assertTrue(payload["screens"]["decision_trace"]["forbidden_cot_keys_absent"])
        self.assertTrue(payload["screens"]["decision_trace"]["cot_denylist_enforced"])

    def test_at18_material_factors_show_source_and_freshness(self):
        payload = self.dossier("SME-L001")
        facts = payload["screens"]["evidence_reconciliation"]["facts"]
        self.assertTrue(facts)
        for fact in facts:
            self.assertTrue(fact["source_system"], fact)
            self.assertTrue(fact["freshness_state"], fact)
            self.assertTrue(fact["provenance"], fact)
        memo = payload["screens"]["credit_memo"]
        material = [row for row in memo["statements"] if row["kind"] == "FACT"]
        self.assertTrue(material)
        self.assertTrue(all(row["evidence_ids"] for row in material))

    def test_fairness_eval_only_with_eval_role(self):
        payload = self.dossier(
            "SME-L001",
            role="RISK_COMPLIANCE_EVAL",
            purpose="RISK_COMPLIANCE_EVAL",
        )
        fairness = payload["screens"]["fairness_eval"]
        self.assertTrue(fairness["runtime_access"])
        self.assertGreater(len(fairness["rows"]), 0)
        self.assertFalse(fairness["legal_cutoff_invented"])
        ctx = payload["screens"]["application_context"]
        self.assertTrue(ctx["restricted_eval_excluded_from_runtime"])

    def test_five_retrieval_families_labelled(self):
        hops = self.dossier("SME-L001")["screens"]["hybrid_retrieval"]
        families = set(hops["families"])
        self.assertEqual(families, {"structured", "graph", "semantic", "policy", "memory"})
        used = {hop["family"] for hop in hops["hops"]}
        self.assertTrue({"structured", "graph", "semantic", "policy"} <= used)
        self.assertTrue(hops["vector_is_not_policy"])


if __name__ == "__main__":
    unittest.main()
