"""Run the CRD golden-scenario evaluation suite and write the JSON report."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from credit_domain.evals import run_golden_evaluation_suite, write_eval_report  # noqa: E402


def main() -> int:
    report = run_golden_evaluation_suite()
    path = write_eval_report(report)
    print(
        f"EVAL SUITE: scenarios={report.scenario_count} "
        f"pass={report.pass_count} rate={report.pass_rate_pct:.1f}% "
        f"critical={report.critical_failure} qt01_claimable={report.qt01_claimable}"
    )
    print(f"REPORT: {path}")
    return 0 if report.pass_count == report.scenario_count and not report.critical_failure else 1


if __name__ == "__main__":
    sys.exit(main())
