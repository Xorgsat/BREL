#!/usr/bin/env python3
"""
CLI Script to execute repeated reliability experiments across N iterations.
Usage:
    python scripts/repeat_experiment.py --experiment EXP-01 --iterations 10
    python scripts/repeat_experiment.py --target experiments/dynamic_dom/test_exp01_dynamic_dom.py --iterations 25
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from reliability_engine.execution_runner import ExecutionRunner
from reliability_engine.report_generator import ReportGenerator

EXPERIMENT_MAP = {
    "EXP-01": "experiments/dynamic_dom/test_exp01_dynamic_dom.py::test_exp01_explicit_wait_remediation",
    "EXP-02": "experiments/synchronization/test_exp02_synchronization.py::test_exp02_explicit_wait_efficiency_contrast",
    "EXP-03": "experiments/stale_elements/test_exp03_stale_elements.py::test_exp03_staleness_synchronization_and_relocation_remedy",
    "EXP-04": "experiments/interception/test_exp04_click_interception.py::test_exp04_overlay_invisibility_synchronization_remedy",
    "EXP-05": "experiments/frames/test_exp05_nested_frames.py::test_exp05_frame_switch_and_interaction",
    "EXP-06": "experiments/shadow_dom/test_exp06_shadow_dom.py::test_exp06_w3c_shadow_root_traversal",
    "EXP-07": "experiments/dialogs/test_exp07_dialogs.py::test_exp07_javascript_alert_acceptance",
    "EXP-08": "experiments/multiple_windows/test_exp08_multiple_windows.py::test_exp08_window_handle_detection_and_switching",
    "EXP-09": "experiments/file_operations/test_exp09_file_operations.py::test_exp09_file_download_and_integrity_check",
    "EXP-10": "experiments/selectors/test_exp10_dynamic_selectors.py::test_exp10_dynamic_id_brittleness_and_semantic_remedy",
    "EXP-11": "experiments/network_delays/test_exp11_network_delays.py::test_exp11_server_side_load_delay_remediation",
    "EXP-12": "experiments/browser_state/test_exp12_browser_state.py::test_exp12_storage_persistence_across_refresh",
    "EXP-13": "experiments/race_conditions/test_exp13_race_conditions.py::test_exp13_synchronized_interaction_race_prevention",
    "EXP-14": "experiments/browser_compatibility/test_exp14_browser_compatibility.py::test_exp14_headless_rendering_integrity",
}


def main():
    parser = argparse.ArgumentParser(description="BREL Repeat Execution Runner")
    parser.add_argument(
        "--experiment",
        type=str,
        help="Experiment ID (e.g., EXP-01, EXP-02, ..., EXP-14)",
    )
    parser.add_argument(
        "--target",
        type=str,
        help="Direct pytest target path (e.g. experiments/dynamic_dom/test_exp01_dynamic_dom.py)",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=10,
        help="Number of repeated iterations (default: 10)",
    )
    parser.add_argument(
        "--browser",
        type=str,
        default="chrome",
        help="Browser engine (chrome, firefox, edge)",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Run in headed visible mode (default: headless)",
    )

    args = parser.parse_args()

    if args.experiment:
        target = EXPERIMENT_MAP.get(args.experiment.upper())
        if not target:
            print(f"Unknown experiment ID: '{args.experiment}'. Available: {list(EXPERIMENT_MAP.keys())}")
            sys.exit(1)
    elif args.target:
        target = args.target
    else:
        print("Must specify either --experiment or --target")
        sys.exit(1)

    runner = ExecutionRunner()
    manifest = runner.run_repeated_experiment(
        test_target=target,
        iterations=args.iterations,
        browser=args.browser,
        headless=not args.headed,
    )

    # Generate Markdown Report
    run_id = manifest["run_id"]
    report_path = Path("reports/reliability") / f"{run_id}_summary.md"
    ReportGenerator.generate_markdown_report(manifest, report_path)
    print(f"\n=======================================================")
    print(f"Report generated: {report_path}")
    print(f"Verdict: {manifest['analysis']['verdict']}")
    print(f"First-Attempt Pass Rate: {manifest['metrics']['first_attempt_pass_rate_pct']}%")
    print(f"Median Latency (P50): {manifest['metrics']['latency']['median_ms']} ms")
    print(f"=======================================================\n")


if __name__ == "__main__":
    main()
