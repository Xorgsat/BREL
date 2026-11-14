# EXP-04: Element Interception and Actionability

**Experiment ID:** EXP-04  
**Category:** Physical Actionability & Hit-Testing  
**Status:** Verified & Passing (4/4 Tests Passed)  
**Author:** Principal SDET / Reliability Engineering Specialist  

---

## 1. Hypothesis
W3C WebDriver native `.click()` dispatches physical mouse coordinates and relies on the browser's hit-testing algorithm to verify that the target element is the top-most visual recipient. If a fixed banner, modal backdrop, or animation layer covers those coordinates, WebDriver deterministically throws `ElementClickInterceptedException`. Waiting for overlay invisibility resolves the condition naturally, whereas executing JavaScript clicks bypasses browser hit-testing and actionability checks.

---

## 2. Experimental Setup
- **Target Applications:**
  - Controlled Local App (`/scenarios/click-interception?overlay_ms=1000`)
  - UI Testing Playground (`/hiddenlayers`)
- **Scenarios Investigated:**
  1. Reproduction of `ElementClickInterceptedException` under an active overlay.
  2. Remediation via explicit waiting for overlay invisibility.
  3. Real-world hit-testing failure on UITAP hidden layers (spawned overlapping button).
  4. Diagnostic JavaScript click contrast (`driver.execute_script("arguments[0].click()", el)`).

---

## 3. Empirical Observations & Results

| Test Scenario | Action | Outcome | Notes |
|---|---|---|---|
| `test_exp04_reproduce_click_intercepted_exception` | Native click with active overlay | **CONFIRMED** | `ElementClickInterceptedException: element click intercepted: Element <button ...> is not clickable at point ... Other element would receive the click: <div id="blocking-overlay">...</div>` |
| `test_exp04_overlay_invisibility_synchronization_remedy` | Wait for overlay invisibility -> click | **PASSED** | Click succeeded as soon as overlay detached |
| `test_exp04_uitap_hidden_layers_interception` | Double click on spawned layers | **CONFIRMED** | Second click intercepted by blue button |
| `test_exp04_diagnostic_js_click_contrast` | JS `arguments[0].click()` with overlay | **PASSED (Diagnostic)** | Bypassed physical actionability; demonstrated hit-testing circumvention |

---

## 4. Engineering Conclusion
1. **Never Default to JS Clicks:** A JavaScript click (`arguments[0].click()`) triggers the DOM event handler directly in the JS engine, completely bypassing hit-testing, CSS z-index, visibility, disabled states, and bounding rect calculations. In a real user flow, a user cannot click a button hidden behind an overlay. JS clicks should only be used in diagnostic research experiments or when interacting with intentionally hidden file inputs.
2. **Actionability Protocol:** When clicks fail, synchronize on the removal of the blocking backdrop/overlay or scroll the target into the visual viewport.
