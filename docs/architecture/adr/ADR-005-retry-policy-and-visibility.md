# ADR-005: Retry Policy and Non-Concealment of Initial Failures

## Context
Automatic test retry (e.g., `pytest-rerunfailures` or Playwright `retries: 2`) is often abused in CI pipelines as a mechanism to achieve "green builds" while concealing latent flakiness. When a test fails on attempt 1 and passes on attempt 2, traditional CI dashboards report a clean pass, hiding the underlying synchronization flaw.

## Decision
1. **No Silent Retries:** In standard experimental suites and regression tests, automated retries are disabled by default (`retries = 0`).
2. **Explicit Retry Investigation Mode:** When retries are enabled within the Reliability Engine for resilience studies:
   - Initial failure diagnostic artifacts (screenshots, logs, DOM snapshots) MUST be preserved.
   - The test outcome must be permanently flagged as `PASSED_AFTER_RETRY (FLAKY)` rather than `PASSED`.
   - CI quality gates must account for `PASSED_AFTER_RETRY` as a reliability warning/defect.
3. **Infrastructure Failures vs Assertion Failures:** If a browser process crashes during startup, an infrastructure retry is permitted, but the incident is logged in the infrastructure error ledger.

## Consequences
- **Positive:** Flaky tests cannot hide behind green CI checkmarks.
- **Positive:** Complete diagnostic evidence of the initial failure is preserved for root cause analysis.
- **Negative:** Engineering teams must fix underlying synchronization bugs rather than relying on retries to mask problems.
