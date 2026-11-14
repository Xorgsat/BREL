# EXP-12: Browser Navigation and State Persistence

**Experiment ID:** EXP-12  
**Category:** State Hygiene & Storage Isolation  
**Status:** Verified & Passing (3/3 Tests Passed)  
**Author:** Principal SDET / Reliability Engineering Specialist  

---

## 1. Hypothesis
Test contamination frequently occurs when residual browser state (cookies, `localStorage`, `sessionStorage`) leaks between tests. Strict session lifecycle teardown and targeted storage cleanup are mandatory to ensure that each test starts with an immaculate, pristine browser state.

---

## 2. Experimental Setup
- **Target Application:** Controlled Local App
- **Scenarios Investigated:**
  1. Cookie injection, retrieval, and complete deletion via WebDriver API.
  2. Web storage (`localStorage` vs `sessionStorage`) persistence across page reloads.
  3. Browser history navigation (`driver.back()`, `driver.forward()`) with URL synchronization.

---

## 3. Empirical Observations & Results

| Test Scenario | Action | Outcome | Verified State |
|---|---|---|---|
| `test_exp12_cookie_lifecycle_and_isolation` | Set, verify, delete cookie | **PASSED** | Cookie created and cleanly erased |
| `test_exp12_storage_persistence_across_refresh` | Set storage, refresh, assert | **PASSED** | Storage survived refresh; cleared cleanly |
| `test_exp12_history_navigation_back_and_forward` | Nav A -> B -> Back -> Forward | **PASSED** | Correct URL and title synchronization |

---

## 4. Engineering Conclusion
1. **Total Session Isolation (ADR-006):** In modern Single Page Applications (SPAs) with complex JWT tokens and cached application states, relying on manual cookie cleanup can still leave stale indexedDB or service worker caches. Terminating the browser process per test function guarantees 100% state isolation.
