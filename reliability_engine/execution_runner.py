"""
Repeat Execution Runner for BREL Reliability Engine.
Executes repeated trial iterations (10, 25, 50, 100) to measure empirical stability
and detect non-deterministic intermittent flakiness.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import subprocess
import time
from typing import Any, Dict, List, Optional
import uuid

from .failure_classifier import FailureClassifier
from .flaky_detector import FlakyDetector, TestFlakinessAnalysis
from .metrics_calculator import MetricsCalculator, ReliabilityMetrics

logger = logging.getLogger(__name__)


class ExecutionRunner:
    """Orchestrates repeatable test execution runs and accumulates reliability data."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path("reports/reliability")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_repeated_experiment(
        self,
        test_target: str,
        iterations: int = 10,
        browser: str = "chrome",
        headless: bool = True,
        random_seed: int = 42,
    ) -> Dict[str, Any]:
        """
        Execute test_target N times consecutively and capture empirical outcome distribution.
        """
        run_id = f"run_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        logger.info(f"Starting repeated experiment {run_id}: target={test_target}, iterations={iterations}")

        run_records: List[Dict[str, Any]] = []

        for i in range(1, iterations + 1):
            cmd = [
                ".venv/bin/pytest",
                test_target,
                f"--browser={browser}",
                "-q",
                "--tb=short",
            ]
            if headless:
                cmd.append("--headless")

            start_t = time.perf_counter()
            proc = subprocess.run(cmd, capture_output=True, text=True)
            elapsed_ms = (time.perf_counter() - start_t) * 1000

            passed = (proc.returncode == 0)
            failure_category = None
            error_message = None

            if not passed:
                error_message = proc.stdout + "\n" + proc.stderr
                cat = FailureClassifier.classify(error_message=error_message)
                failure_category = cat.value

            record = {
                "iteration": i,
                "passed": passed,
                "duration_ms": round(elapsed_ms, 2),
                "return_code": proc.returncode,
                "failure_category": failure_category,
                "error_snippet": error_message[:300] if error_message else None,
            }
            run_records.append(record)
            logger.info(f"Iteration {i}/{iterations}: {'PASS' if passed else 'FAIL'} ({elapsed_ms:.1f}ms)")

        # Analyze flakiness across the repeated runs
        flakiness_analysis = FlakyDetector.analyze_multi_run_dataset(
            test_id=test_target,
            run_results=run_records,
        )

        # Calculate metrics
        durations = [r["duration_ms"] for r in run_records]
        metrics = MetricsCalculator.calculate_suite_metrics(
            test_analyses=[flakiness_analysis.model_dump()],
            all_durations_ms=durations,
        )

        manifest = {
            "run_id": run_id,
            "test_target": test_target,
            "browser": browser,
            "iterations": iterations,
            "random_seed": random_seed,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "analysis": flakiness_analysis.model_dump(),
            "metrics": metrics.model_dump(),
            "iterations_data": run_records,
        }

        # Persist results
        result_file = self.output_dir / f"{run_id}_results.json"
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        logger.info(f"Repeatability experiment complete. Persisted: {result_file}")
        return manifest
