# ADR-007: Reliability Metric Formulations and Statistical Limitations

## Context
Quality metrics in automation are often ambiguously defined. Terms like "Pass Rate" can mean "tests that passed eventually after 3 retries" or "tests that passed on the very first try". Furthermore, teams often run a test 10 times, see 10 passes, and claim "100% reliability", ignoring sample variance and confidence intervals.

## Decision
1. **Mathematical Metric Definitions:**
   - **First-Attempt Pass Rate ($FPR$):**
     $$FPR = \frac{\text{Passed on First Attempt}}{\text{Total First-Attempt Executions}} \times 100$$
   - **Failure Rate ($FR$):**
     $$FR = \frac{\text{Failed on First Attempt}}{\text{Total First-Attempt Executions}} \times 100 = 100 - FPR$$
   - **Retry Recovery Rate ($RR$):**
     $$RR = \frac{\text{Initially Failed Tests Passing on Subsequent Attempt}}{\text{Total Tests Retried}} \times 100$$
   - **Final Pass Rate ($FPR_{\text{final}}$):**
     $$FPR_{\text{final}} = \frac{\text{Tests Ultimately Passing within Allowed Attempts}}{\text{Total Valid Executions}} \times 100$$
   - **Flakiness Rate ($Flakiness$):**
     $$Flakiness = \frac{\text{Tests Exhibiting Inconsistent Results}}{\text{Total Tests Evaluated}} \times 100$$
2. **Latency Percentiles:** Execution times must report $P_{50}$ (median), $P_{90}$, and $P_{95}$ alongside mean and standard deviation.
3. **Finite Sample Rigor:** All benchmark reports must explicitly state:
   - Sample size $N$.
   - The 95% confidence interval for observed pass/failure rates (e.g., via Wilson score interval).
   - A disclaimer that zero observed failures in $N$ runs indicates failure probability $p < \frac{3}{N}$ (Rule of Three), not $p = 0$.
4. **Zero Fabrication Policy:** If an experiment or browser configuration has not been run, its metrics must be explicitly recorded as `NOT MEASURED`.

## Consequences
- **Positive:** Elevates automation metrics to rigorous engineering research standards.
- **Positive:** Clear auditability for senior leadership and technical interviews.
