"""
Unit & Integration Tests for BREL Flaky Test Detection Engine.
Verifies failure classification, retry history auditing, non-concealment of flakiness,
and statistical metrics calculation per ADR-004, ADR-005, and ADR-007.
"""

from __future__ import annotations

import pytest
from reliability_engine.failure_classifier import FailureCategory, FailureClassifier
from reliability_engine.flaky_detector import (
    ExecutionAttempt,
    FlakyDetector,
    TestVerdict,
)
from reliability_engine.metrics_calculator import MetricsCalculator


def test_failure_classifier_taxonomy():
    """Verify accurate mapping of exception strings to 11 taxonomy categories."""
    assert FailureClassifier.classify("StaleElementReferenceException") == FailureCategory.DOM_LIFECYCLE
    assert FailureClassifier.classify("ElementClickInterceptedException") == FailureCategory.ACTIONABILITY
    assert FailureClassifier.classify("TimeoutException", "timed out waiting for element") == FailureCategory.SYNCHRONIZATION
    assert FailureClassifier.classify("NoSuchElementException") == FailureCategory.LOCATOR
    assert FailureClassifier.classify(error_message="ERR_CONNECTION_REFUSED") == FailureCategory.NETWORK
    assert FailureClassifier.classify("AssertionError") == FailureCategory.APPLICATION_DEFECT


def test_retry_pass_is_strictly_classified_as_flaky():
    """
    CRITICAL QUALITY GATE (ADR-005):
    A test that fails on attempt 1 and passes on attempt 2 MUST be classified as
    PASSED_AFTER_RETRY (FLAKY). It must NEVER be reported as a clean pass.
    """
    attempts = [
        ExecutionAttempt(
            attempt_number=1,
            passed=False,
            duration_ms=512.0,
            error_type="TimeoutException",
            error_message="Timed out waiting for condition",
            failure_category=FailureCategory.SYNCHRONIZATION.value,
        ),
        ExecutionAttempt(
            attempt_number=2,
            passed=True,
            duration_ms=420.0,
        ),
    ]

    analysis = FlakyDetector.analyze_test_attempts(
        test_id="experiments/test_example.py::test_flaky_target",
        attempts=attempts,
    )

    # Must be identified as flaky
    assert analysis.is_flaky is True
    assert analysis.verdict == TestVerdict.PASSED_AFTER_RETRY_FLAKY
    assert analysis.first_attempt_passed == 0
    assert analysis.first_attempt_failed == 1
    assert analysis.retry_passed == 1
    assert analysis.final_passed == 1
    assert analysis.failure_distribution.get("Synchronization") == 1


def test_multi_run_intermittent_flakiness_detection():
    """
    MULTI-RUN INSTABILITY DETECTION:
    In a series of 10 repeated executions, if 8 pass and 2 fail,
    the test must be classified as INTERMITTENT_FLAKY.
    """
    run_records = [
        {"iteration": 1, "passed": True, "duration_ms": 100.0},
        {"iteration": 2, "passed": True, "duration_ms": 105.0},
        {"iteration": 3, "passed": False, "duration_ms": 500.0, "failure_category": "Actionability"},
        {"iteration": 4, "passed": True, "duration_ms": 95.0},
        {"iteration": 5, "passed": True, "duration_ms": 110.0},
        {"iteration": 6, "passed": False, "duration_ms": 520.0, "failure_category": "Actionability"},
        {"iteration": 7, "passed": True, "duration_ms": 98.0},
        {"iteration": 8, "passed": True, "duration_ms": 102.0},
        {"iteration": 9, "passed": True, "duration_ms": 101.0},
        {"iteration": 10, "passed": True, "duration_ms": 99.0},
    ]

    analysis = FlakyDetector.analyze_multi_run_dataset(
        test_id="experiments/test_race.py::test_intermittent_target",
        run_results=run_records,
    )

    assert analysis.is_flaky is True
    assert analysis.verdict == TestVerdict.INTERMITTENT_FLAKY
    assert analysis.first_attempt_passed == 8
    assert analysis.first_attempt_failed == 2
    assert analysis.failure_distribution.get("Actionability") == 2

    # Calculate suite metrics
    metrics = MetricsCalculator.calculate_suite_metrics([analysis.model_dump()])
    assert metrics.first_attempt_pass_rate_pct == 80.0
    assert metrics.failure_rate_pct == 20.0
    assert metrics.flakiness_rate_pct == 100.0
    assert metrics.flaky_test_count == 1


def test_metrics_calculator_wilson_interval_and_rule_of_three():
    """Verify statistical formulations for Wilson confidence intervals and Rule of Three."""
    # Case 1: 10 passes out of 10 runs
    ci_10 = MetricsCalculator.calculate_wilson_score_interval(10, 10)
    assert ci_10.lower > 70.0  # Wilson lower bound for 10/10 is ~72.25%
    assert ci_10.upper == 100.0

    metrics_perfect = MetricsCalculator.calculate_suite_metrics([
        {
            "test_id": "test_perfect",
            "total_runs": 10,
            "first_attempt_passed": 10,
            "first_attempt_failed": 0,
            "retry_passed": 0,
            "final_passed": 10,
            "is_flaky": False,
            "durations_ms": [100.0] * 10,
        }
    ])
    assert metrics_perfect.rule_of_three_upper_bound_pct == 30.0  # 3 / 10 = 30%
    assert "Rule of Three applies" in metrics_perfect.statistical_disclaimer
