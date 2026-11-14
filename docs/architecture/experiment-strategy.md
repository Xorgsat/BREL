# Experiment Strategy and Methodology: BREL Laboratory

**Document ID:** BREL-STRAT-001  
**Status:** Approved  
**Author:** Principal SDET / Reliability Engineering Specialist  

---

## 1. Overview and Core Research Question

The core research question of the Browser Reliability Engineering Lab is:

> **How do different browser automation approaches behave under difficult, asynchronous, and unreliable browser conditions, and how can we systematically measure, diagnose, and improve their reliability?**

To answer this question rigorously, BREL structures its work into 14 distinct experimental domains (EXP-01 through EXP-14). Each experiment tests a specific browser or DOM lifecycle failure mode, benchmarks mitigation strategies, and records empirical metrics.

---

## 2. Experiment Catalogue (EXP-01 through EXP-14)

### EXP-01: Dynamic DOM and Asynchronous Rendering
- **Objective:** Quantify failure probability when interacting with elements rendered or unhidden asynchronously after initial page load or AJAX dispatch.
- **Scenarios:**
  1. *Public App A:* `/dynamic_loading/1` (element hidden via `display: none` -> rendered visible after 5s) vs `/dynamic_loading/2` (element not present in DOM -> injected into DOM after 5s).
  2. *Controlled App:* Configurable DOM insertion delay ($T_{render} \in [100\text{ms}, 3000\text{ms}]$).
- **Comparison:**
  - Selenium: Immediate `find_element` (expected `NoSuchElementException`), `presence_of_element_located` vs `visibility_of_element_located`.
  - Playwright: Locator auto-waiting (`locator.click()`, `expect(locator).toBeVisible()`).
- **Target Metrics:** Pass rate, wait duration (ms), timeout rate.

### EXP-02: Synchronization and Waiting Strategies
- **Objective:** Evaluate and contrast 5 primary synchronization paradigms:
  1. Arbitrary fixed sleep (`time.sleep(N)`).
  2. Driver-level implicit wait (`implicitly_wait`).
  3. WebDriver explicit wait (`WebDriverWait` + Expected Conditions).
  4. Custom polling wait with custom condition predicates and fluent polling intervals.
  5. Playwright web-first auto-retrying assertions.
- **Scenarios:** UITAP `/clientdelay` (15s client delay) & Controlled App `/scenarios/dynamic-render?delay_ms=2500`.
- **Target Metrics:** Execution duration, flakiness under CPU/network throttling, false pass/failure rate.

### EXP-03: Stale Element References
- **Objective:** Investigate how DOM tree mutation invalidates cached element memory pointers (`WebElement` references) and measure recovery mechanisms.
- **Scenarios:**
  - Element detachment followed by re-attachment (`/disappearing_elements`, `/dynamic_controls`).
  - Controlled App: Dynamic DOM node recycling (`/scenarios/stale-dom`).
- **Mitigation Strategies:**
  - Pattern A: Naive reuse (reproduces `StaleElementReferenceException`).
  - Pattern B: Explicit staleness waiting followed by re-querying.
  - Pattern C: Dynamic resilient locator proxy / smart retry wrapper.
  - Playwright Comparison: Auto-re-querying locator model.

### EXP-04: Element Interception and Actionability
- **Objective:** Investigate physical interaction obstacles (overlays, modal backdrops, sticky headers, animations).
- **Scenarios:**
  - UITAP `/hiddenlayers` (click triggers overlapping blue button intercepting subsequent clicks).
  - UITAP `/overlapped` (element partially obscured by a fixed scroll layer).
  - Controlled App: Temporary blocking modal overlay with decay timer $T_{overlay}$.
- **Comparison:**
  - Selenium native click (`ElementClickInterceptedException`) vs `scroll_into_view` vs waiting for overlay invisibility.
  - Diagnostic JavaScript click (evaluated as a diagnostic experiment, explicitly documenting that it bypasses user event dispatch).
  - Playwright actionability checks (visible, stable, enabled, receiving events).

### EXP-05: Frames and Nested Frames
- **Objective:** Measure latency and failure rates when traversing hierarchical document contexts.
- **Scenarios:**
  - The Internet `/nested_frames` (top frameset: left, middle, right; bottom frame).
  - Dynamic frame loading delays.
- **Comparison:**
  - Selenium: Explicit context switching (`switch_to.frame`, `switch_to.default_content`).
  - Playwright: `page.frameLocator()` chaining and frame lifecycle management.

### EXP-06: Shadow DOM Encapsulation
- **Objective:** Test element traversal across open and nested shadow roots.
- **Scenarios:**
  - The Internet `/shadowdom` and UITAP `/shadowdom`.
  - Controlled App: Nested custom elements (`<user-card>` -> `<profile-badge>`).
- **Comparison:**
  - Selenium: `element.shadow_root` API (W3C standard) and CSS selectors within shadow contexts.
  - Playwright: Built-in shadow-piercing CSS locators.

### EXP-07: JavaScript Dialogs and Modal Interruptions
- **Objective:** Verify handling of synchronous execution-blocking browser alerts, confirms, and prompts.
- **Scenarios:** The Internet `/javascript_alerts` (JS Alert, Confirm with OK/Cancel state verification, Prompt with text input).
- **Comparison:**
  - Selenium: `Alert` interface (`switch_to.alert`, `accept()`, `dismiss()`, `send_keys()`).
  - Playwright: Event-driven dialog listener (`page.on('dialog', ...)`).

### EXP-08: Multiple Windows and Context Switching
- **Objective:** Evaluate reliability of asynchronous tab/window opening and window handle synchronization.
- **Scenarios:** The Internet `/windows` (`target="_blank"` link dispatch).
- **Comparison:**
  - Selenium: Polling `driver.window_handles` until count changes, switching by handle, closing child tab, returning to parent.
  - Playwright: `page.waitForEvent('popup')`.

### EXP-09: File Uploads and Downloads
- **Objective:** Validate end-to-end file system automation, download completion verification, and temporary artifact isolation.
- **Scenarios:**
  - Upload: The Internet `/upload` via hidden `<input type="file">`.
  - Download: The Internet `/download` with background verification of file existence, non-zero file size, and SHA256 integrity check.
- **Isolation:** UUID-based isolated download directories per test worker.

### EXP-10: Dynamic Selectors and Locator Reliability
- **Objective:** Measure locator fragility under dynamic attribute mutation.
- **Scenarios:**
  - UITAP `/dynamicid` (ID changes on every page load).
  - UITAP `/classattr` (multiple CSS classes with spaces and state changes).
  - UITAP `/nbsp` (non-breaking space `\u00A0` in text content).
- **Comparison:** Fragile absolute XPath vs semantic CSS / robust XPath vs Playwright user-facing role locators (`getByRole`, `getByText`).

### EXP-11: Delayed Network Responses and Server Latency
- **Objective:** Observe test framework behavior under unpredictable API latency and slow static assets.
- **Scenarios:**
  - UITAP `/loaddelay` (5.4s initial response hold).
  - Controlled App: `/scenarios/delayed-api?delay_ms=4000&failure_rate=0.25`.
- **Comparison:**
  - Selenium: Page load strategy (`normal`, `eager`, `none`) and explicit condition waiting.
  - Playwright: `page.waitForResponse()`, `page.route()` network mocking.

### EXP-12: Browser Navigation and State Persistence
- **Objective:** Evaluate test isolation leakage from retained session cookies, `localStorage`, `sessionStorage`, and history navigation.
- **Scenarios:** Cookie injection, state cleanup verification, back/forward cache (bfcache) navigation.

### EXP-13: Race Conditions and Timing Interleaving
- **Objective:** Provoke and measure race conditions where two asynchronous events compete (e.g., clicking before an event listener binds, reading text before DOM mutation finishes).
- **Scenarios:** Controlled App `/scenarios/race-condition?race_window_ms=50`.
- **Measurement:** Running 50-100 repeated runs to derive exact empirical failure distributions.

### EXP-14: Browser Compatibility Matrix
- **Objective:** Run identical test workflows against Chromium, Firefox, and WebKit (in Playwright) to record engine-specific variances.
- **Deliverable:** Compatibility comparison matrix documenting differences in event timing, dialog behavior, and actionability.

---

## 3. Failure Classification Taxonomy

To ensure scientific rigor, every failure observed during test execution is classified into one of 11 distinct categories:

```text
┌───────────────────────────┬────────────────────────────────────────────────────────┐
│ Classification            │ Description & Representative Exception                 │
├───────────────────────────┼────────────────────────────────────────────────────────┤
│ 1. Synchronization        │ Element state transition timed out (TimeoutException)  │
│ 2. Locator                │ Element not found in DOM (NoSuchElementException)      │
│ 3. DOM Lifecycle          │ Cached pointer detached/replaced (StaleElementRef)     │
│ 4. Actionability          │ Element covered or unclickable (ClickIntercepted)      │
│ 5. Navigation             │ URL/State did not transition as expected               │
│ 6. Network                │ Request timeout, connection reset, or 5xx response     │
│ 7. Browser Crash          │ Driver process terminated unexpectedly                 │
│ 8. Infrastructure         │ Driver binary mismatch, display server failure         │
│ 9. State Contamination    │ Residual cookies, storage, or windows from prior test  │
│ 10. Application Defect    │ Genuine assertion failure due to target bug            │
│ 11. Unknown / Unverified  │ Insufficient diagnostic telemetry to isolate cause     │
└───────────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 4. Statistical Rigor and Measurement Methodology

When measuring reliability across repeated iterations ($N \in \{10, 25, 50, 100\}$):

1. **Finite Sample Disclaimer:** A test with 0 failures in 50 runs has an estimated failure rate $\hat{p} = 0$, but the 95% Wilson score confidence interval upper bound is approximately:
   $$U = \frac{0 + \frac{1.96^2}{2 \times 50} + 1.96 \sqrt{\frac{0}{50} + \frac{1.96^2}{4 \times 50^2}}}{1 + \frac{1.96^2}{50}} \approx 7.1\%$$
   Therefore, zero observed failures does **not** prove absolute infallibility.
2. **True Flakiness Definition:** A test is classified as **FLAKY** if it exhibits inconsistent outcomes across identical conditions, or passes on a subsequent retry after failing initially. Retrying a test and having it pass does **not** make it a clean pass; it flags an unresolved reliability defect.
3. **No Fabricated Data:** If an experiment is not executed, its metrics must be explicitly recorded as `NOT MEASURED`.
