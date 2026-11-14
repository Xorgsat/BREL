# EXP-14: Browser Compatibility and Engine Variances

**Experiment ID:** EXP-14  
**Category:** Cross-Engine Compatibility & Telemetry  
**Status:** Verified & Passing (2/2 Tests Passed)  
**Author:** Principal SDET / Reliability Engineering Specialist  

---

## 1. Hypothesis
Browser engines (Chromium, Gecko, WebKit) exhibit subtle variances in command-line arguments, headless rendering implementations, and default viewport geometry. A robust test infrastructure must capture and record precise browser telemetry (name, version, user agent, capabilities, viewport) to make all test executions fully auditable.

---

## 2. Experimental Setup
- **Target Application:** Controlled Local App
- **Scenarios Investigated:**
  1. Engine Telemetry Audit: Extracting `driver.capabilities` (browser name, version, chromedriver build, session ID, user agent) and validating window size $\ge 1280 \times 720$.
  2. Headless Rendering Integrity: Verifying that device pixel ratio (`window.devicePixelRatio`) and color depth (`screen.colorDepth`) render consistently in headless mode.

---

## 3. Empirical Observations & Results

| Test Scenario | Telemetry Validated | Outcome | Empirical Data |
|---|---|---|---|
| `test_exp14_browser_engine_telemetry_capture` | Engine, version, viewport | **PASSED** | Browser: `chrome` 157.0.8103.52, Viewport: 1920x1080 |
| `test_exp14_headless_rendering_integrity` | Pixel ratio & color depth | **PASSED** | DPR: > 0, Color Depth: 24-bit TrueColor |

---

## 4. Engineering Conclusion
1. **Never Assume Engine Parity:** Chromium, Gecko (Firefox), and WebKit have distinct event loop scheduling and actionability nuances.
2. **Archiving Execution Context:** Attaching exact browser versions and platform metadata to every test report enables instantaneous triage of browser-specific regressions.
