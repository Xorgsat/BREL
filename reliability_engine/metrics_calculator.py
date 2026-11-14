"""
Reliability Metrics Calculator for BREL.
Implements mathematical formulations for FPR, FR, RR, Flakiness, Latency percentiles,
and Wilson score confidence intervals per ADR-007.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class LatencyStats(BaseModel):
    mean_ms: float = 0.0
    median_ms: float = 0.0
    p90_ms: float = 0.0
    p95_ms: float = 0.0
    min_ms: float = 0.0
    max_ms: float = 0.0


class ConfidenceInterval(BaseModel):
    lower: float
    upper: float
    confidence_level: float = 0.95


class ReliabilityMetrics(BaseModel):
    total_executions: int
    first_attempt_pass_rate_pct: float
    failure_rate_pct: float
    retry_recovery_rate_pct: float
    final_pass_rate_pct: float
    flakiness_rate_pct: float
    flaky_test_count: int
    total_unique_tests: int
    latency: LatencyStats
    pass_rate_ci_95: ConfidenceInterval
    rule_of_three_upper_bound_pct: Optional[float] = None
    statistical_disclaimer: str


class MetricsCalculator:
    """Calculates standardized reliability metrics from execution records."""

    @staticmethod
    def calculate_percentile(sorted_values: List[float], percentile: float) -> float:
        if not sorted_values:
            return 0.0
        k = (len(sorted_values) - 1) * percentile
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return sorted_values[int(k)]
        d0 = sorted_values[int(f)] * (c - k)
        d1 = sorted_values[int(c)] * (k - f)
        return d0 + d1

    @staticmethod
    def calculate_latency_stats(durations_ms: List[float]) -> LatencyStats:
        if not durations_ms:
            return LatencyStats()

        sorted_d = sorted(durations_ms)
        n = len(sorted_d)
        mean_val = sum(sorted_d) / n

        return LatencyStats(
            mean_ms=round(mean_val, 2),
            median_ms=round(MetricsCalculator.calculate_percentile(sorted_d, 0.50), 2),
            p90_ms=round(MetricsCalculator.calculate_percentile(sorted_d, 0.90), 2),
            p95_ms=round(MetricsCalculator.calculate_percentile(sorted_d, 0.95), 2),
            min_ms=round(sorted_d[0], 2),
            max_ms=round(sorted_d[-1], 2),
        )

    @staticmethod
    def calculate_wilson_score_interval(successes: int, trials: int, z: float = 1.96) -> ConfidenceInterval:
        """
        Wilson Score 95% Confidence Interval for a binomial proportion.
        Handles zero-failure edge cases safely without degenerate intervals.
        """
        if trials == 0:
            return ConfidenceInterval(lower=0.0, upper=0.0)

        p = successes / trials
        denominator = 1 + (z**2) / trials
        centre_adjusted = p + (z**2) / (2 * trials)
        adjusted_std = z * math.sqrt((p * (1 - p) + (z**2) / (4 * trials)) / trials)

        lower = max(0.0, (centre_adjusted - adjusted_std) / denominator) * 100
        upper = min(1.0, (centre_adjusted + adjusted_std) / denominator) * 100

        return ConfidenceInterval(
            lower=round(lower, 2),
            upper=round(upper, 2),
            confidence_level=0.95,
        )

    @classmethod
    def calculate_suite_metrics(
        cls,
        test_analyses: List[Dict[str, Any]],
        all_durations_ms: Optional[List[float]] = None,
    ) -> ReliabilityMetrics:
        """
        Compute high-level suite reliability metrics from individual test analyses.
        """
        total_unique_tests = len(test_analyses)
        if total_unique_tests == 0:
            return ReliabilityMetrics(
                total_executions=0,
                first_attempt_pass_rate_pct=0.0,
                failure_rate_pct=0.0,
                retry_recovery_rate_pct=0.0,
                final_pass_rate_pct=0.0,
                flakiness_rate_pct=0.0,
                flaky_test_count=0,
                total_unique_tests=0,
                latency=LatencyStats(),
                pass_rate_ci_95=ConfidenceInterval(lower=0.0, upper=0.0),
                statistical_disclaimer="No test records provided.",
            )

        total_execs = sum(t.get("total_runs", 1) for t in test_analyses)
        first_passes = sum(t.get("first_attempt_passed", 0) for t in test_analyses)
        first_fails = sum(t.get("first_attempt_failed", 0) for t in test_analyses)
        final_passes = sum(t.get("final_passed", 0) for t in test_analyses)
        retry_passed = sum(t.get("retry_passed", 0) for t in test_analyses)
        flaky_tests = sum(1 for t in test_analyses if t.get("is_flaky", False))

        fpr = (first_passes / total_execs * 100) if total_execs > 0 else 0.0
        fr = (first_fails / total_execs * 100) if total_execs > 0 else 0.0

        tests_retried = sum(1 for t in test_analyses if t.get("first_attempt_failed", 0) > 0)
        rr = (retry_passed / tests_retried * 100) if tests_retried > 0 else 0.0

        final_pr = (final_passes / total_execs * 100) if total_execs > 0 else 0.0
        flakiness_rate = (flaky_tests / total_unique_tests * 100) if total_unique_tests > 0 else 0.0

        # Latency statistics
        durations: List[float] = all_durations_ms or []
        if not durations:
            for t in test_analyses:
                durations.extend(t.get("durations_ms", []))
        latency = cls.calculate_latency_stats(durations)

        # Statistical rigor
        ci = cls.calculate_wilson_score_interval(first_passes, total_execs)
        rule_of_three = round((3.0 / total_execs) * 100, 2) if total_execs > 0 else None

        disclaimer = (
            f"Calculated across sample N={total_execs}. "
            f"95% Wilson confidence interval for first-attempt pass rate: [{ci.lower}%, {ci.upper}%]. "
        )
        if first_fails == 0 and total_execs > 0:
            disclaimer += f"Rule of Three applies: zero failures in N={total_execs} implies true failure rate p < {rule_of_three}% (not 0.00%)."

        return ReliabilityMetrics(
            total_executions=total_execs,
            first_attempt_pass_rate_pct=round(fpr, 2),
            failure_rate_pct=round(fr, 2),
            retry_recovery_rate_pct=round(rr, 2),
            final_pass_rate_pct=round(final_pr, 2),
            flakiness_rate_pct=round(flakiness_rate, 2),
            flaky_test_count=flaky_tests,
            total_unique_tests=total_unique_tests,
            latency=latency,
            pass_rate_ci_95=ci,
            rule_of_three_upper_bound_pct=rule_of_three if first_fails == 0 else None,
            statistical_disclaimer=disclaimer,
        )
