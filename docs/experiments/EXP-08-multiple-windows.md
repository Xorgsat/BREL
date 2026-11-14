# EXP-08: Multiple Windows and Context Switching

**Experiment ID:** EXP-08  
**Category:** Window Handles & Multi-Tab Synchronization  
**Status:** Verified & Passing (1/1 Tests Passed)  
**Author:** Principal SDET / Reliability Engineering Specialist  

---

## 1. Hypothesis
When a user interaction triggers `target="_blank"` or calls `window.open()`, the OS and browser require variable latency to initialize the new browsing context and populate WebDriver's `driver.window_handles` collection. Naive immediate index lookup (`driver.window_handles[1]`) causes `IndexError` flakiness. Explicit synchronization polling against handle count growth guarantees reliable tab switching.

---

## 2. Experimental Setup
- **Target Application:** The Internet (`/windows`)
- **Scenarios Investigated:**
  1. Capture initial handle set.
  2. Click link with `target="_blank"`.
  3. `WindowManager.wait_for_new_window` polls `driver.window_handles` until set difference resolves the new handle.
  4. Switch context to new window, validate heading ("New Window"), close child window, and restore context to parent handle.

---

## 3. Empirical Observations & Results

| Test Scenario | Action | Outcome | Duration | Notes |
|---|---|---|---|---|
| `test_exp08_window_handle_detection_and_switching` | Multi-tab open, assertion, close, restore | **PASSED** | 1.82s | Clean handle resolution and parent restoration |

---

## 4. Engineering Conclusion
1. **Handle State Management:** WebDriver sessions keep secondary window handles open even after tests finish unless explicitly closed or the driver is terminated. Function-scoped driver lifecycles prevent window handle leaks across tests.
2. **Context Switching Discipline:** Closing a window does not automatically return focus to the parent window; `driver.switch_to.window(parent_handle)` must be invoked explicitly.
