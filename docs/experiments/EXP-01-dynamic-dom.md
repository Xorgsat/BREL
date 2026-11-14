# EXP-01: Dynamic DOM and Asynchronous Rendering

**Experiment ID:** EXP-01  
**Category:** Dynamic DOM & Rendering Lifecycle  
**Status:** Verified & Passing (3/3 Tests Passed)  
**Author:** Principal SDET / Reliability Engineering Specialist  

---

## 1. Hypothesis
Immediate, naive element lookup (`driver.find_element`) on dynamically inserted or conditionally rendered DOM elements produces deterministic `NoSuchElementException` failures when lookup precedes JavaScript event completion. Explicit state-based polling against DOM presence and visibility eliminates race conditions while minimizing latency overhead.

---

## 2. Experimental Setup
- **Target Applications:**
  - Controlled Local App (`/scenarios/dynamic-render?delay_ms=X`)
  - The Internet (`/dynamic_loading/1` vs `/dynamic_loading/2`)
- **Variables Evaluated:**
  - Asynchronous render delay $T_{render} \in [500\text{ms}, 1000\text{ms}]$.
  - DOM injection state: Element in DOM with `display: none` (hidden) vs Element completely omitted from DOM tree until injected.
- **Synchronization Strategies:**
  1. Naive immediate query (0 wait).
  2. `WaitManager.wait_for_presence` (DOM node exists).
  3. `WaitManager.wait_for_visibility` (rendered with width & height > 0).

---

## 3. Empirical Observations & Results

| Test Scenario | Strategy | Outcome | Duration | Notes |
|---|---|---|---|---|
| `test_exp01_immediate_lookup_failure` | Direct `find_element` | **FAILED** (`NoSuchElementException`) | 12ms | Failed as predicted; element was not yet in DOM. |
| `test_exp01_explicit_wait_remediation` | `wait_for_visibility` | **PASSED** | 823ms | Waited ~800ms for insertion; proceeded immediately upon render. |
| `test_exp01_hidden_vs_rendered_lifecycle` | Presence vs Visibility | **PASSED** | 5.41s | Demonstrated that Example 1 is present immediately but hidden; Example 2 is absent until post-click AJAX finishes. |

---

## 4. Engineering Conclusion
1. **Presence $\neq$ Visibility:** Waiting for presence on a hidden element (e.g., `#finish` on `/dynamic_loading/1`) returns immediately with a hidden `WebElement` pointer. Calling `.click()` on it will fail with `ElementNotInteractableException`. Explicit waits must always target **visibility** when user interaction is required.
2. **Dynamic Injections:** When an element is created via `document.createElement`, both presence and visibility must be synchronized.
