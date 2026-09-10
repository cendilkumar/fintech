"""CRD-FR-004 routing tests for CRD-AC-002 / 005 / 011 / 012."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from credit_domain.model import SemanticCollapseError  # noqa: E402
from credit_domain.retrieval import (  # noqa: E402
    RetrievalFamily,
    UnknownRetrievalNeed,
    classify_need,
    classify_question,
    route_need,
    route_needs,
    route_question,
    route_underwriting,
    use_semantic_as_policy,
)


class RoutingTableTests(unittest.TestCase):
    def test_need_catalog_maps_four_primary_families(self):
        self.assertEqual(classify_need("requested_limit"), RetrievalFamily.STRUCTURED)
        self.assertEqual(classify_need("guarantor"), RetrievalFamily.GRAPH)
        self.assertEqual(classify_need("supporting_narrative"), RetrievalFamily.SEMANTIC)
        self.assertEqual(classify_need("active_policy"), RetrievalFamily.POLICY)
        with self.assertRaises(UnknownRetrievalNeed):
            classify_need("invent_a_threshold")

    def test_policy_keywords_keep_policy_need_on_narrative_trap(self):
        needs = classify_question("former large-limit escalation boundary which policy applies")
        self.assertIn("active_policy", needs)


class Ac002StructuredAndPolicyTests(unittest.TestCase):
    def test_sme_l002_limit_is_structured_and_authority_is_policy(self):
        plan = route_needs("SME-L002", ["requested_limit", "authority_route"])
        structured = plan.hops_for(RetrievalFamily.STRUCTURED)[0]
        policy = plan.hops_for(RetrievalFamily.POLICY)[0]
        self.assertEqual(structured.tool, "CRD-TOOL-001")
        self.assertEqual(structured.facts[0].value, 8_500_000)
        self.assertFalse(structured.controlling)
        self.assertEqual(policy.tool, "CRD-TOOL-004")
        self.assertTrue(policy.controlling)
        engine = next(f for f in policy.facts if f.semantic_type == "PolicyEvaluation")
        self.assertEqual(engine.value["result"], "REQUIRES_CREDIT_AUTHORITY")
        self.assertEqual(engine.value["required_human_role"], "CREDIT_AUTHORITY")
        self.assertIn("AUTH-LIMIT-01", engine.value["triggered_rule_ids"])
        policy_docs = [f.value for f in policy.facts if f.semantic_type == "Policy"]
        self.assertEqual(policy_docs, ["CREDIT-POLICY-3.2"])
        self.assertTrue(plan.controlling_policy_sources())
        self.assertTrue(plan.trace())
        self.assertEqual({row["need"] for row in plan.trace()}, {"requested_limit", "authority_route"})


class Ac005StaleStructuredTests(unittest.TestCase):
    def test_sme_l005_bank_and_health_are_structured_and_stale(self):
        plan = route_needs("SME-L005", ["bank_inflows", "source_health"])
        bank = plan.hops_for(RetrievalFamily.STRUCTURED)[0]
        self.assertEqual(bank.tool, "CRD-TOOL-001")
        self.assertEqual(bank.facts[0].freshness_state, "stale")
        health = plan.hops_for(RetrievalFamily.STRUCTURED)[1]
        bank_health = [f for f in health.facts if f.semantic_type.endswith("BANK_DATA")]
        self.assertTrue(bank_health)
        self.assertEqual(bank_health[0].value, "STALE")
        self.assertTrue(any("BANK-005" in ref or "bank_financial" in ref for ref in bank.source_refs))


class Ac011BothFinancialSourcesTests(unittest.TestCase):
    def test_sme_l011_structured_returns_bank_and_tax_without_blend(self):
        plan = route_needs("SME-L011", ["bank_inflows", "tax_turnover"])
        bank = plan.hops_for(RetrievalFamily.STRUCTURED)[0].facts[0]
        tax = plan.hops_for(RetrievalFamily.STRUCTURED)[1].facts[0]
        self.assertEqual(bank.semantic_type, "BANK_INFLOWS_12M")
        self.assertEqual(tax.semantic_type, "TAX_DECLARED_TURNOVER")
        self.assertEqual(bank.conflict_state, "unresolved")
        self.assertEqual(tax.conflict_state, "unresolved")
        self.assertNotEqual(bank.value, tax.value)
        self.assertNotIn("structured", [h.family.value for h in plan.hops if h.controlling])


class Ac012VectorCannotOverridePolicyTests(unittest.TestCase):
    def test_sme_l012_policy_route_ignores_similarity_trap(self):
        question = "former large-limit escalation boundary which policy applies"
        plan = route_question("SME-L012", question)
        policy = plan.hops_for(RetrievalFamily.POLICY)
        self.assertTrue(policy)
        self.assertTrue(policy[0].controlling)
        self.assertEqual(policy[0].tool, "CRD-TOOL-004")
        versions = [f.value for f in policy[0].facts if f.semantic_type == "Policy"]
        self.assertEqual(versions, ["CREDIT-POLICY-3.2"])
        engine = next(f for f in policy[0].facts if f.semantic_type == "PolicyEvaluation")
        self.assertEqual(engine.value["required_human_role"], "CREDIT_AUTHORITY")
        semantic = plan.hops_for(RetrievalFamily.SEMANTIC)
        self.assertTrue(all(not h.controlling for h in semantic))
        with self.assertRaises(SemanticCollapseError):
            use_semantic_as_policy(question)
        self.assertTrue(any(row["tool"] == "CRD-TOOL-004" and row["controlling"] for row in plan.trace()))


class GraphAndSemanticTraceTests(unittest.TestCase):
    def test_sme_l013_graph_returns_guarantor_relationship(self):
        hop = route_need("SME-L013", "guarantor")
        self.assertEqual(hop.family, RetrievalFamily.GRAPH)
        self.assertEqual(hop.tool, "CRD-TOOL-002")
        kinds = {f.semantic_type for f in hop.facts}
        self.assertTrue(any("Guarantor" in k for k in kinds))
        self.assertTrue(any("PLAYED_BY" in k for k in kinds))
        self.assertFalse(hop.controlling)

    def test_semantic_hits_are_untrusted_and_traced(self):
        hop = route_need("SME-L001", "supporting_narrative", query="historical memo stale bank")
        self.assertEqual(hop.tool, "CRD-TOOL-003")
        self.assertFalse(hop.controlling)
        self.assertTrue(hop.facts)
        self.assertTrue(all(f.untrusted and not f.controlling for f in hop.facts))
        self.assertTrue(hop.source_refs)

    def test_underwriting_plan_traces_selected_sources(self):
        plan = route_underwriting("SME-L001")
        families = {h.family for h in plan.hops}
        self.assertIn(RetrievalFamily.STRUCTURED, families)
        self.assertIn(RetrievalFamily.GRAPH, families)
        self.assertIn(RetrievalFamily.SEMANTIC, families)
        self.assertIn(RetrievalFamily.POLICY, families)
        self.assertTrue(all(h.source_refs or h.need == "guarantor" for h in plan.hops))
        self.assertTrue(plan.trace())

    def test_cross_tenant_returns_denied_plan(self):
        plan = route_underwriting("SME-L008", actor_tenant="TENANT-ALPHA")
        self.assertEqual(plan.denied, "CROSS_TENANT")
        self.assertEqual(plan.hops, [])


if __name__ == "__main__":
    unittest.main()
