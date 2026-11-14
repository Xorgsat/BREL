# EXP-11: Delayed Network Responses and Server Latency

**Experiment ID:** EXP-11  
**Category:** Network Latency & Page Load Timeouts  
**Status:** Verified & Passing (2/2 Tests Passed)  
**Author:** Principal SDET / Reliability Engineering Specialist  

---

## 1. Hypothesis
Server-side response delays that exceed WebDriver's configured `page_load_timeout` throw `TimeoutException` during navigation. Configuring appropriate load timeouts and eager page load strategies prevents catastrophic test crashes when backends experience transient latency spikes.

---

## 2. Experimental Setup
- **Target Application:** UI Testing Playground (`/loaddelay`)
- **Empirical Baseline:** Verified that `/loaddelay` introduces a server-side delay of ~5.4 seconds before response headers are sent.
- **Scenarios Investigated:**
  1. Failure Mode: Setting `driver.set_page_load_timeout(2.0)` deterministically causes navigation to fail with `TimeoutException`.
  2. Remediation: Setting `driver.set_page_load_timeout(15.0)` allows navigation to complete, verifying the 5.4s delay, and asserting the target button appears.

---

## 3. Empirical Observations & Results

| Test Scenario | Configured Timeout | Observed Duration | Outcome | Notes |
|---|---|---|---|---|
| `test_exp11_server_side_load_delay_timeout` | 2.0s | 2.02s | **CONFIRMED FAILURE** | Threw `TimeoutException` as expected |
| `test_exp11_server_side_load_delay_remediation` | 15.0s | 5.83s | **PASSED** | Waited 5.8s for server response, clicked button |

---

## 4. Engineering Conclusion
1. **Differentiating Page Load vs Element Synchronization:** `set_page_load_timeout` governs initial document navigation (`driver.get()`). Once the initial document is received, `WaitManager` explicit waits govern component-level synchronization.
2. **Eager Page Load Strategy:** Setting `page_load_strategy = "eager"` avoids waiting for irrelevant third-party tracking scripts or remote ad pixels, saving seconds on enterprise applications.
