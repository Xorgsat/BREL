# EXP-07: JavaScript Dialogs and Modal Interruptions

**Experiment ID:** EXP-07  
**Category:** Modal Dialogs & Thread Interruption  
**Status:** Verified & Passing (3/3 Tests Passed)  
**Author:** Principal SDET / Reliability Engineering Specialist  

---

## 1. Hypothesis
JavaScript modal dialogs (`window.alert`, `window.confirm`, `window.prompt`) interrupt the browser's JavaScript event thread and present native modal dialogs outside the DOM. Any attempt to interact with the underlying DOM while a dialog is displayed raises `UnexpectedAlertPresentException`. Furthermore, unlike DOM elements, dialogs require explicit context switching via WebDriver's `Alert` interface (`driver.switch_to.alert`).

---

## 2. Experimental Setup
- **Target Application:** The Internet (`/javascript_alerts`)
- **Scenarios Investigated:**
  1. Standard alert: message extraction, acceptance (`alert.accept()`), and resulting DOM state.
  2. Confirm dialog dual-state verification: acceptance ("You clicked: Ok") vs dismissal ("You clicked: Cancel").
  3. Prompt dialog text injection: `alert.send_keys()` verification with input reflection in DOM.

---

## 3. Empirical Observations & Results

| Test Scenario | Action | Outcome | Verified DOM Result |
|---|---|---|---|
| `test_exp07_javascript_alert_acceptance` | Read message & accept | **PASSED** | "You successfully clicked an alert" |
| `test_exp07_javascript_confirm_ok_and_cancel_states` | Branch 1: OK, Branch 2: Cancel | **PASSED** | Validated both affirmative and negative outcomes |
| `test_exp07_javascript_prompt_text_injection` | Inject "BREL Reliability Engineering Specialist" | **PASSED** | "You entered: BREL Reliability Engineering Specialist" |

---

## 4. Engineering Conclusion
1. **Thread Blocking:** Native browser dialogs synchronously suspend JavaScript execution until dismissed or accepted.
2. **Context Switching:** WebDriver does not treat dialogs as DOM nodes. The `Alert` interface must be used, and synchronization must poll `EC.alert_is_present()`.
