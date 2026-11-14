"""
Flaky Test Detection Engine for BREL.
Identifies outcome instability, tracks retry histories, and enforces non-concealment
of initial failures per ADR-004 and ADR-005.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TestVerdict(str, Enum):
    __test__ = False
    CLEAN_PASS = "CLEAN_PASS"
    PASSED_AFTER_RETRY_FLAKY = "PASSED_AFTER_RETRY (FLAKY)"
    INTERMITTENT_FLAKY = "INTERMITTENT_FLAKY"
    FAILED = "FAILED"
    NOT_MEASURED = "NOT_MEASURED"


class ExecutionAttempt(BaseModel):
    attempt_number: int
    passed: bool
    duration_ms: float
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    failure_category: Optional[str] = None


class TestFlakinessAnalysis(BaseModel):
    __test__ = False
    test_id: str
    total_runs: int
    first_attempt_passed: int
    first_attempt_failed: int
    retry_passed: int
    final_passed: int
    final_failed: int
    verdict: TestVerdict
    is_flaky: bool
    failure_distribution: Dict[str, int] = Field(default_factory=dict)
    durations_ms: List[float] = Field(default_factory=list)


class FlakyDetector:
    """Evaluates multi-run and multi-attempt test records to detect intermittent instability."""

    @staticmethod
    def analyze_test_attempts(test_id: str, attempts: List[ExecutionAttempt]) -> TestFlakinessAnalysis:
        """
        Analyze all sequential attempts of a single test execution run (e.g. attempt 1, 2, ...).
        Enforces ADR-005: If attempt 1 failed and attempt 2 passed, flag as PASSED_AFTER_RETRY (FLAKY).
        """
        if not attempts:
            return TestFlakinessAnalysis(
                test_id=test_id,
                total_runs=0,
                first_attempt_passed=0,
                first_attempt_failed=0,
                retry_passed=0,
                final_passed=0,
                final_failed=0,
                verdict=TestVerdict.NOT_MEASURED,
                is_flaky=False,
            )

        first_attempt = attempts[0]
        final_attempt = attempts[-1]
        first_passed = 1 if first_attempt.passed else 0
        first_failed = 0 if first_attempt.passed else 1

        retry_passed = 0
        if not first_attempt.passed and any(a.passed for a in attempts[1:]):
            retry_passed = 1

        final_passed = 1 if final_attempt.passed else 0
        final_failed = 0 if final_attempt.passed else 1

        # Classify verdict
        if first_passed and len(attempts) == 1:
            verdict = TestVerdict.CLEAN_PASS
            is_flaky = False
        elif not first_passed and final_passed:
            # Failed first, passed on retry -> FLAKY
            verdict = TestVerdict.PASSED_AFTER_RETRY_FLAKY
            is_flaky = True
        else:
            verdict = TestVerdict.FAILED
            is_flaky = False

        failure_dist: Dict[str, int] = {}
        for a in attempts:
            if not a.passed and a.failure_category:
                failure_dist[a.failure_category] = failure_dist.get(a.failure_category, 0) + 1

        return TestFlakinessAnalysis(
            test_id=test_id,
            total_runs=len(attempts),
            first_attempt_passed=first_passed,
            first_attempt_failed=first_failed,
            retry_passed=retry_passed,
            final_passed=final_passed,
            final_failed=final_failed,
            verdict=verdict,
            is_flaky=is_flaky,
            failure_distribution=failure_dist,
            durations_ms=[a.duration_ms for a in attempts],
        )

    @staticmethod
    def analyze_multi_run_dataset(
        test_id: str,
        run_results: List[Dict[str, Any]],
    ) -> TestFlakinessAnalysis:
        """
        Analyze a repeated execution dataset (N executions under identical conditions).
        If outcome varies (e.g. 9 passes and 1 failure out of 10), test is INTERMITTENT_FLAKY.
        """
        if not run_results:
            return TestFlakinessAnalysis(
                test_id=test_id,
                total_runs=0,
                first_attempt_passed=0,
                first_attempt_failed=0,
                retry_passed=0,
                final_passed=0,
                final_failed=0,
                verdict=TestVerdict.NOT_MEASURED,
                is_flaky=False,
            )

        total_runs = len(run_results)
        passed_runs = sum(1 for r in run_results if r.get("passed", False))
        failed_runs = total_runs - passed_runs

        failure_dist: Dict[str, int] = {}
        durations: List[float] = []

        for r in run_results:
            durations.append(r.get("duration_ms", 0.0))
            if not r.get("passed", False):
                cat = r.get("failure_category", "Unknown")
                failure_dist[cat] = failure_dist.get(cat, 0) + 1

        if passed_runs == total_runs:
            verdict = TestVerdict.CLEAN_PASS
            is_flaky = False
        elif failed_runs == total_runs:
            verdict = TestVerdict.FAILED
            is_flaky = False
        else:
            # Intermittent failure across identical repeated runs
            verdict = TestVerdict.INTERMITTENT_FLAKY
            is_flaky = True

        return TestFlakinessAnalysis(
            test_id=test_id,
            total_runs=total_runs,
            first_attempt_passed=passed_runs,
            first_attempt_failed=failed_runs,
            retry_passed=0,
            final_passed=passed_runs,
            final_failed=failed_runs,
            verdict=verdict,
            is_flaky=is_flaky,
            failure_distribution=failure_dist,
            durations_ms=durations,
        )
