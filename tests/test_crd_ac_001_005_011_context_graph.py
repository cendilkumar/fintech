"""CRD-AC-001 / CRD-AC-005 / CRD-AC-011 — task-specific runtime context graph."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from credit_domain.context import (  # noqa: E402
    CORE_KINDS,
    ContextAuthorityError,
    ContextScopeError,
    assemble_runtime_context,
    historical_memo_as_policy,
    load_historical_memos,
    refuse_repository_dump,
    traverse_connected_context,
)
from credit_domain.model import PartyKind, ResolutionState  # noqa: E402


class Ac001TaskSpecificSliceTests(unittest.TestCase):
    def test_sme_l001_includes_required_kinds_and_exclusion_reasons(self):
        graph = assemble_runtime_context("SME-L001")
        self.assertEqual(graph.request.task, "UNDERWRITE_APPLICATION")
        self.assertEqual(graph.request.application_id, "SME-L001")
        self.assertEqual(graph.request.actor_tenant, "TENANT-ALPHA")
        self.assertEqual(graph.request.as_of_time, "2026-09-15T10:00:00+05:30")
        self.assertTrue(set(CORE_KINDS) <= graph.kinds_present())
        self.assertEqual(len(graph.nodes_of("Application")), 1)
        self.assertEqual(len(graph.nodes_of("Guarantor")), 0)
        self.assertEqual(graph.policy_version, "CREDIT-POLICY-3.2")
        policy = graph.nodes_of("Policy")[0]
        self.assertTrue(policy.presented_as_current)
        self.assertEqual(policy.attributes["engine_result"], "PASS")
        decision = graph.nodes_of("Decision")[0]
        self.assertEqual(decision.attributes["status"], "PENDING")
        self.assertIsNone(decision.value)
        with self.assertRaises(ContextAuthorityError):
            decision.as_human_decision()
        entity = graph.nodes_of("Entity")[0]
        self.assertEqual(entity.attributes["identity_state"], ResolutionState.MATCHED.value)
        self.assertEqual(entity.attributes["canonical_party_id"], "ORG-001")
        self.assertEqual(graph.application_ids_in_nodes(), {"SME-L001"})
        codes = graph.exclusion_codes()
        self.assertIn("OTHER_APPLICATION", codes)
        self.assertIn("CROSS_TENANT", codes)
        self.assertIn("HISTORICAL_MEMO_NOT_POLICY", codes)
        self.assertIn("SUPERSEDED_POLICY", codes)
        self.assertIn("RESTRICTED_ATTRIBUTE", codes)
        self.assertIn("IRRELEVANT_TO_TASK", codes)
        self.assertTrue(any(item.ref == "SME-L008" and item.reason_code == "CROSS_TENANT" for item in graph.excluded))
        self.assertTrue(any(item.ref == "SME-L002" and item.reason_code == "OTHER_APPLICATION" for item in graph.excluded))
        neighbors = traverse_connected_context(graph, "APP:SME-L001", "HAS_APPLICANT_ROLE")
        self.assertEqual(len(neighbors), 1)
        self.assertEqual(neighbors[0][1].kind, "Applicant")

    def test_repository_dump_and_cross_tenant_are_blocked(self):
        with self.assertRaises(ContextScopeError):
            refuse_repository_dump()
        with self.assertRaises(ContextScopeError):
            assemble_runtime_context(None)
        denied = assemble_runtime_context("SME-L008", actor_tenant="TENANT-ALPHA")
        self.assertEqual(denied.nodes, [])
        self.assertIn("CROSS_TENANT", denied.exclusion_codes())
        self.assertNotIn("SME-L008", {n.label for n in denied.nodes})

    def test_historical_memos_are_not_policy_or_truth(self):
        memos = load_historical_memos()
        self.assertTrue(memos)
        self.assertTrue(all(m.authoritative_for_current_policy is False for m in memos))
        with self.assertRaises(ContextAuthorityError):
            historical_memo_as_policy(memos[0])
        with self.assertRaises(ContextAuthorityError):
            memos[0].as_objective_truth()
        graph = assemble_runtime_context("SME-L001")
        self.assertFalse(any(n.kind == "Policy" and "2.9" in n.label for n in graph.nodes))
        self.assertFalse(any(n.node_id.startswith("NARR-") for n in graph.nodes))
        self.assertNotIn("HIST-", "".join(graph.application_ids_in_nodes()))


class Ac005StaleBankTests(unittest.TestCase):
    def test_sme_l005_bank_is_stale_and_not_current(self):
        graph = assemble_runtime_context("SME-L005")
        banks = graph.nodes_of("BankEvidence")
        self.assertTrue(banks)
        self.assertTrue(all(n.freshness_state == "stale" for n in banks))
        self.assertTrue(all(n.presented_as_current is False for n in banks))
        health = {row["source"]: row["state"] for row in graph.source_health}
        self.assertEqual(health.get("BANK_DATA"), "STALE")
        policy = graph.nodes_of("Policy")[0]
        self.assertEqual(policy.attributes["engine_result"], "PASS")
        self.assertIn("DATA-FRESHNESS-BANK", policy.attributes["triggered_rule_ids"])
        freshness = [n for n in graph.nodes_of("Exception") if n.label == "FRESHNESS"]
        self.assertTrue(freshness)
        self.assertFalse(any(n.kind == "BankEvidence" and n.presented_as_current for n in graph.nodes))


class Ac011ConflictOnGraphTests(unittest.TestCase):
    def test_sme_l011_bank_and_tax_conflict_edge(self):
        graph = assemble_runtime_context("SME-L011")
        banks = graph.nodes_of("BankEvidence")
        taxes = graph.nodes_of("TaxEvidence")
        inflows = [n for n in banks if n.attributes.get("semantic_type") == "BANK_INFLOWS_12M"]
        turnovers = [n for n in taxes if n.attributes.get("semantic_type") == "TAX_DECLARED_TURNOVER"]
        self.assertEqual(len(inflows), 1)
        self.assertEqual(len(turnovers), 1)
        self.assertEqual(inflows[0].conflict_state, "unresolved")
        self.assertEqual(turnovers[0].conflict_state, "unresolved")
        self.assertNotEqual(inflows[0].value, turnovers[0].value)
        conflict_edges = [e for e in graph.edges if e.relationship == "CONFLICTS_WITH"]
        self.assertTrue(conflict_edges)
        self.assertTrue(graph.unresolved_conflicts)
        self.assertTrue(any(n.label == "FINANCIAL_CONFLICT" for n in graph.nodes_of("Exception")))
        policy = graph.nodes_of("Policy")[0]
        self.assertEqual(policy.attributes["engine_result"], "PASS")


class RoleAndIdentityOnGraphTests(unittest.TestCase):
    def test_sme_l013_guarantor_is_separate_entity(self):
        graph = assemble_runtime_context("SME-L013")
        guarantors = graph.nodes_of("Guarantor")
        self.assertEqual(len(guarantors), 1)
        played = traverse_connected_context(graph, guarantors[0].node_id, "PLAYED_BY")
        self.assertEqual(len(played), 1)
        self.assertEqual(played[0][1].kind, "Entity")
        self.assertEqual(played[0][1].attributes["party_kind"], PartyKind.NATURAL_PERSON.value)
        org_kinds = {
            n.attributes.get("party_kind")
            for n in graph.nodes_of("Entity")
            if n.attributes.get("party_kind") == PartyKind.LEGAL_ENTITY.value
        }
        self.assertIn(PartyKind.LEGAL_ENTITY.value, org_kinds)
        self.assertNotEqual(played[0][1].node_id, next(n.node_id for n in graph.nodes_of("Entity") if n.attributes.get("party_kind") == PartyKind.LEGAL_ENTITY.value))

    def test_sme_l004_identity_stays_ambiguous(self):
        graph = assemble_runtime_context("SME-L004")
        entities = [
            n
            for n in graph.nodes_of("Entity")
            if n.attributes.get("party_kind") == PartyKind.LEGAL_ENTITY.value
        ]
        self.assertTrue(entities)
        self.assertEqual(entities[0].attributes["identity_state"], ResolutionState.AMBIGUOUS.value)
        self.assertIsNone(entities[0].attributes["canonical_party_id"])
        self.assertTrue(any(n.label == "IDENTITY" for n in graph.nodes_of("Exception")))


if __name__ == "__main__":
    unittest.main()
