"""CRD-AC-001–015 — automated golden-scenario evaluation suite."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from credit_domain.evals import (  # noqa: E402
    GRADE_DIMENSIONS,
    INVENTED_THRESHOLD_PROBE,
    UngovernedLearningWriteError,
    attempt_ungoverned_learning_write,
    load_golden_scenarios,
    run_golden_evaluation_suite,
    snapshot_protected_artifacts,
    write_eval_report,
)
from credit_domain.policy import PolicyFidelityError, scan_generated_policy_claims  # noqa: E402


class GoldenEvalSuiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before = snapshot_protected_artifacts()
        cls.report = run_golden_evaluation_suite()
        cls.report_path = write_eval_report(cls.report)

    def test_catalog_has_twelve_dimensions_and_fifteen_scenarios(self):
        self.assertEqual(len(GRADE_DIMENSIONS), 12)
        rows = load_golden_scenarios()
        self.assertEqual(len(rows), 15)
        self.assertEqual(self.report.scenario_count, 15)
        self.assertEqual(
            [s.scenario_id for s in self.report.scenarios],
            [f"GS-{i:02d}" for i in range(1, 16)],
        )
        self.assertEqual(
            [s.application_id for s in self.report.scenarios],
            [f"SME-L{i:03d}" for i in range(1, 16)],
        )

    def test_every_scenario_grades_the_prompt_13_dimensions(self):
        for scenario in self.report.scenarios:
            names = [g.dimension for g in scenario.grades]
            self.assertEqual(names, list(GRADE_DIMENSIONS), scenario.scenario_id)
            self.assertTrue(
                any(g.status in {"PASS", "FAIL"} for g in scenario.grades),
                scenario.scenario_id,
            )

    def test_invented_threshold_is_critical_failure(self):
        with self.assertRaises(PolicyFidelityError):
            scan_generated_policy_claims(INVENTED_THRESHOLD_PROBE, application_id="SME-L014")
        gs14 = next(s for s in self.report.scenarios if s.scenario_id == "GS-14")
        threshold = next(g for g in gs14.grades if g.dimension == "hallucinated_thresholds")
        self.assertEqual(threshold.status, "PASS")
        self.assertIn("2,500,000", INVENTED_THRESHOLD_PROBE)
        self.assertFalse(self.report.critical_failure)
        self.assertEqual(self.report.hard_gates["HG-02"]["value"], 0)
        self.assertTrue(self.report.hard_gates["HG-02"]["pass"])

    def test_all_fifteen_scenarios_pass_at_contract_layer(self):
        failed = [
            (s.scenario_id, g.dimension, g.evidence)
            for s in self.report.scenarios
            for g in s.grades
            if g.status == "FAIL"
        ]
        self.assertEqual(failed, [])
        self.assertEqual(self.report.pass_count, 15)
        self.assertEqual(self.report.pass_rate_pct, 100.0)

    def test_hard_gates_and_qt01_claim_rule(self):
        for hid in ("HG-01", "HG-02", "HG-03", "HG-04", "HG-05", "HG-06", "HG-07", "HG-08"):
            self.assertTrue(self.report.hard_gates[hid]["pass"], hid)
        self.assertTrue(self.report.qt01_claimable)
        qt01 = self.report.quality_targets["QT-01"]
        self.assertTrue(qt01["claimable"])
        self.assertEqual(qt01["layer"], "contract")
        self.assertEqual(self.report.layer, "contract")
        self.assertTrue(
            any("Workbench GS screens are not claimed" in note for note in self.report.notes)
        )

    def test_gs08_tenant_and_gs09_injection_and_gs11_conflict(self):
        gs08 = next(s for s in self.report.scenarios if s.scenario_id == "GS-08")
        self.assertEqual(
            next(g for g in gs08.grades if g.dimension == "tenant_isolation").status, "PASS"
        )
        gs09 = next(s for s in self.report.scenarios if s.scenario_id == "GS-09")
        self.assertEqual(
            next(g for g in gs09.grades if g.dimension == "injection_resistance").status, "PASS"
        )
        gs11 = next(s for s in self.report.scenarios if s.scenario_id == "GS-11")
        self.assertEqual(
            next(g for g in gs11.grades if g.dimension == "conflict_preservation").status, "PASS"
        )
        gs10 = next(s for s in self.report.scenarios if s.scenario_id == "GS-10")
        self.assertEqual(
            next(g for g in gs10.grades if g.dimension == "outage_handling").status, "PASS"
        )

    def test_gs15_does_not_rewrite_policy_or_gold_labels(self):
        with self.assertRaises(UngovernedLearningWriteError):
            attempt_ungoverned_learning_write("CREDIT-POLICY-3.2", "AI_ACCEPTED")
        self.assertEqual(snapshot_protected_artifacts(), self.before)
        self.assertEqual(self.report.protected_artifact_hashes, self.before)

    def test_report_is_stored_under_evidence_sdd(self):
        self.assertTrue(self.report_path.exists())
        payload = json.loads(self.report_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["scenario_count"], 15)
        self.assertFalse(payload["critical_failure"])


if __name__ == "__main__":
    unittest.main()
