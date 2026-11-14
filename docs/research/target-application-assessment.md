# Target Application Assessment: Empirical Research Report

**Document ID:** BREL-RES-001  
**Verification Date:** 2026-11-14  
**Investigator:** Principal SDET / Reliability Engineering Specialist  
**Status:** Verified via Empirical Network & DOM Probing

---

## 1. Executive Summary

A core principle of the Browser Reliability Engineering Lab (BREL) is **empirical verification before automation**. Before writing a single automation script or asserting framework capabilities, both public demo applications—**The Internet (Heroku)** and **UI Testing Playground (UITAP)**—were probed via automated HTTP sweeps, SSL certificate validation, and DOM response parsing.

### Key Empirical Discoveries
1. **The Internet (`https://the-internet.herokuapp.com/`)**:
   - Status: Highly operational. 76 challenge routes probed; 73 return `200 OK`.
   - Security/Auth Routes: `/basic_auth`, `/digest_auth`, and `/download_secure` correctly respond with `401 Unauthorized` (challenge-response protocol).
   - Dynamic capabilities: Stale element triggers, dynamic loading (hidden element vs rendered element), and nested frames remain intact.
2. **UI Testing Playground (`http://uitestingplayground.com/`)**:
   - Status: Operational with infrastructure caveats.
   - **Critical Finding (SSL Certificate Mismatch):** When accessed via HTTPS (`https://uitestingplayground.com/`), Azure App Service returns an SSL certificate with `CN=*.azurewebsites.net`. The Subject Alternative Name (SAN) does not include `uitestingplayground.com`. Browsers will abort navigation with `NET::ERR_CERT_COMMON_NAME_INVALID` unless `--ignore-certificate-errors` or `accept_insecure_certs=True` is configured.
   - **Load Delay Endpoint (`/loaddelay`):** Introduces a deliberate server-side processing delay of **5.42 seconds** before emitting HTTP 200 headers.
3. **Controlled Local Application Requirement**:
   - While public applications provide realistic end-to-end browser scenarios, network jitter, CDN caching, third-party hosting outages, and non-configurable timing make them unsuitable for isolated statistical repeatability experiments (e.g., 50–100 iterations of race conditions). A local FastAPI-based controlled testbed is necessary as a deterministic reference standard.

---

## 2. Assessment Matrix: The Internet (Heroku)

| Application | Scenario | URL | Availability | Browser Challenge | Selenium Suitability | Playwright Suitability | Reproducibility | Limitations | Decision |
|---|---|---|---|---|---|---|---|---|---|
| The Internet | Dynamic Loading | `/dynamic_loading` | Verified (200) | Elements rendered or unhidden after user interaction with 5s delay | High | High | Reproducible | Two distinct sub-scenarios: Element rendered vs element unhidden | **Include** (EXP-01) |
| The Internet | Dynamic Controls | `/dynamic_controls` | Verified (200) | Checkbox removed from DOM, input enabled/disabled asynchronously | High | High | Reproducible | Spinner overlay during async state transition | **Include** (EXP-02) |
| The Internet | Stale Element Reference | `/disappearing_elements` & `/dynamic_controls` | Verified (200) | Element detachment from DOM followed by DOM mutation | High | High | Reproducible | Re-rendering invalidates cached element pointers | **Include** (EXP-03) |
| The Internet | JavaScript Alerts | `/javascript_alerts` | Verified (200) | Modal browser dialogs (Alert, Confirm, Prompt) interrupting thread | High | High | Reproducible | Modal dialog locks execution context | **Include** (EXP-07) |
| The Internet | Multiple Windows | `/windows` | Verified (200) | `target="_blank"` triggering secondary window handle creation | High | High | Reproducible | OS-level window handle propagation delay | **Include** (EXP-08) |
| The Internet | Nested Frames | `/nested_frames` | Verified (200) | Complex frameset with top (left, middle, right) and bottom frames | High | High | Reproducible | Hierarchical frame context switching | **Include** (EXP-05) |
| The Internet | Shadow DOM | `/shadowdom` | Verified (200) | Web components encapsulating DOM nodes inside shadow roots | High | High | Reproducible | Open shadow root with slot projections | **Include** (EXP-06) |
| The Internet | File Upload | `/upload` | Verified (200) | Multipart form upload via standard `<input type="file">` | High | High | Reproducible | Drag-and-drop area vs file input element | **Include** (EXP-09) |
| The Internet | File Download | `/download` | Verified (200) | Direct file links triggering browser download manager | High | High | Reproducible | Browser-specific download directory handling | **Include** (EXP-09) |
| The Internet | Challenging DOM | `/challenging_dom` | Verified (200) | Dynamically generated element IDs, canvas element, dynamic tables | High | High | Reproducible | Dynamic IDs change on every refresh | **Include** (EXP-10) |
| The Internet | Slow Resources | `/slow` | Verified (200) | Asset loading delay simulating high latency assets | High | High | Intermittent (depends on Heroku) | Fixed delay, not seedable | **Include (Secondary)** |

---

## 3. Assessment Matrix: UI Testing Playground

| Application | Scenario | URL | Availability | Browser Challenge | Selenium Suitability | Playwright Suitability | Reproducibility | Limitations | Decision |
|---|---|---|---|---|---|---|---|---|---|
| UITAP | AJAX Data | `/ajax` | Verified (200) | Client-side AJAX request with 15-second response delay | High | High | Reproducible | Fixed 15-second wait can slow test runs | **Include** (EXP-01, EXP-02) |
| UITAP | Client Side Delay | `/clientdelay` | Verified (200) | Client-side `setTimeout` rendering button after 15s | High | High | Reproducible | Requires high wait timeout | **Include** (EXP-02) |
| UITAP | Click Interception / Overlapped | `/overlapped` & `/hiddenlayers` | Verified (200) | Green button clicked generates a blue overlay intercepting subsequent clicks | High | High | Reproducible | Clickability condition triggers `ElementClickInterceptedException` | **Include** (EXP-04) |
| UITAP | Dynamic ID | `/dynamicid` | Verified (200) | Button ID changes on each DOM render | High | High | Reproducible | Prohibits static ID locators | **Include** (EXP-10) |
| UITAP | Class Attribute | `/classattr` | Verified (200) | Primary button has composite and dynamic classes | High | High | Reproducible | Multiple class matching pitfalls | **Include** (EXP-10) |
| UITAP | Load Delay | `/loaddelay` | Verified (200, 5.4s delay) | Server holds response headers for 5+ seconds before emitting HTML | High | High | Reproducible | Page-load timeout sensitivity | **Include** (EXP-11) |
| UITAP | Shadow DOM | `/shadowdom` | Verified (200) | Shadow DOM guid generator with clipboard copy | High | High | Reproducible | Shadow root encapsulation | **Include** (EXP-06) |
| UITAP | Auto Wait | `/autowait` | Verified (200) | Delayed element states (hidden -> visible, disabled -> enabled, text change) | High | High | Reproducible | Designed specifically to evaluate framework auto-waiting | **Include** (EXP-01, EXP-02) |
| UITAP | Non-Breaking Space | `/nbsp` | Verified (200) | Button text contains `&nbsp;` (`\u00A0`) instead of regular space | High | High | Reproducible | Locator text matching failure trap | **Include** (EXP-10) |
| UITAP | Scrollbars | `/scrollbars` | Verified (200) | Button placed inside a hidden scrollable container | High | High | Reproducible | Viewport vs scroll container | **Include** (EXP-04) |

---

## 4. Supplementary Controlled Test Application Specification

Public demo applications have limitations:
1. **Lack of seedable timing:** Delay intervals are fixed (e.g., exactly 15 seconds) or fluctuate with internet latency.
2. **Rate limiting / network flakiness:** Running 100 iterations of an experiment against a remote server can lead to false positives caused by intermediate proxy resets.
3. **No programmatic failure injection:** Remote servers cannot be told "fail with 500 on 30% of requests" or "replace the DOM element exactly 120ms after click".

### Controlled Application Feature Set
The BREL controlled application is implemented as an ultra-fast, lightweight FastAPI application (`controlled-app/`) with the following deterministic endpoints:
- `/scenarios/dynamic-render`: Injectable delay parameter `?delay_ms=X` and DOM injection mode.
- `/scenarios/stale-dom`: Configurable DOM recycling interval `?recycle_ms=X`.
- `/scenarios/click-interception`: Transparent or visual overlay persisting for `?overlay_ms=X` before detaching.
- `/scenarios/race-condition`: Read/write race condition with configurable window `?race_window_ms=X`.
- `/scenarios/delayed-api`: Server API response holding for `?delay_ms=X` with seedable random error injection `?failure_rate=0.2&seed=42`.
- `/scenarios/shadow-dom`: Nested open shadow roots with dynamic shadow trees.
- `/scenarios/frames`: Nested dynamic iframes with independent loading lags.

---

## 5. Summary of Decisions

1. **Both Public Applications Approved:**
   - Both `the-internet.herokuapp.com` and `uitestingplayground.com` are active and well-suited for end-to-end browser interaction validation.
   - For UITAP, all WebDriver sessions and HTTP clients MUST accept insecure certificates or use HTTP (`http://uitestingplayground.com`).
2. **Local Controlled Application Mandated:**
   - For repeatable flakiness benchmarks (10, 25, 50, 100 runs) and race condition investigations, the controlled application will be utilized to guarantee statistical validity without confounding network variance.
