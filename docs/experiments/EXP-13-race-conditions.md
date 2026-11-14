# EXP-13: Race Conditions and Timing Interleaving

**Experiment ID:** EXP-13  
**Category:** Asynchronous Race Conditions & Timing Windows  
**Status:** Verified & Passing (2/2 Tests Passed)  
**Author:** Principal SDET / Reliability Engineering Specialist  

---

## 1. Hypothesis
Race conditions occur when user interactions clash with internal asynchronous state transitions (e.g., clicking a button before its JavaScript event handler has bound, or reading text while a DOM mutation is underway). Naive automation fails intermittently depending on CPU scheduling. Synchronizing against a discrete application readiness flag completely eliminates race flakiness.

---

## 2. Experimental Setup
- **Target Application:** Controlled Local App (`/scenarios/race-condition?race_window_ms=200`)
- **Scenarios Investigated:**
  1. Premature Interaction: The client delays event listener attachment by 300ms. Clicking immediately (< 50ms) triggers the click handler prematurely, resulting in `RACE_LOST_CLICK_IGNORED` and `FAILED_EARLY_INTERACTION`.
  2. Synchronized Interaction: The test uses `WaitManager.wait_for_javascript_condition` to wait for `window.listenerAttached === true` before dispatching the click, guaranteeing `SUCCESS_TOKEN_ACCEPTED`.

---

## 3. Empirical Observations & Results

| Test Scenario | Timing Strategy | Outcome | Resulting Application State |
|---|---|---|---|
| `test_exp13_reproduce_premature_interaction_race_loss` | Immediate click (< 50ms) | **CONFIRMED FAILURE** | `RACE_LOST_CLICK_IGNORED` |
| `test_exp13_synchronized_interaction_race_prevention` | Wait for readiness predicate | **PASSED** | `RACE_WON_STATE_COMMITTED` (`SUCCESS_TOKEN_ACCEPTED`) |

---

## 4. Engineering Conclusion
1. **The Root Cause of "Intermittent" Click Failures:** In complex React/Vue/Angular apps, DOM elements often mount before `useEffect` or hydration binds event listeners. A test that clicks immediately will succeed on fast machines but fail intermittently under CI CPU contention.
2. **Readiness Predicates:** Real-world enterprise automation must synchronize against observable readiness signals (e.g., network idle, custom data attributes `data-ready="true"`, or Vue/React component state).
