# EXP-03: Stale Element References and DOM Lifecycle

**Experiment ID:** EXP-03  
**Category:** DOM Lifecycle & Pointer Invalidation  
**Status:** Verified & Passing (3/3 Tests Passed)  
**Author:** Principal SDET / Reliability Engineering Specialist  

---

## 1. Hypothesis
In W3C WebDriver, a `WebElement` represents an internal memory pointer to a specific DOM node. When JavaScript mutates the DOM tree (replacing innerHTML, re-rendering virtual DOM components, or detaching a node), that pointer becomes permanently detached, causing any subsequent operation on that object reference to raise `StaleElementReferenceException`.

---

## 2. Experimental Setup
- **Target Applications:**
  - Controlled Local App (`/scenarios/stale-dom?recycle_ms=300`)
  - The Internet (`/dynamic_controls`)
- **Scenarios Investigated:**
  1. Reproduction of `StaleElementReferenceException` by reusing detached reference.
  2. Remediation via explicit staleness waiting (`wait_for_staleness`) followed by re-locating.
  3. Dynamic DOM node removal (checkbox detachment).

---

## 3. Empirical Observations & Results

| Test Scenario | Action | Outcome | Observed Exception |
|---|---|---|---|
| `test_exp03_reproduce_stale_element_reference_exception` | Reuse reference after innerHTML replacement | **CONFIRMED** | `StaleElementReferenceException: stale element reference: stale element not found in the current frame` |
| `test_exp03_staleness_synchronization_and_relocation_remedy` | `wait_for_staleness` -> re-query | **PASSED** | Recovered cleanly; fresh node clicked and verified |
| `test_exp03_dynamic_controls_stale_checkbox` | Remove checkbox -> assert staleness | **PASSED** | Checkbox staleness confirmed; removal verified |

---

## 4. Engineering Conclusion
1. **Never Cache WebElements Across Mutations:** Never store `WebElement` references as long-lived test fixture state or Page Object instance variables.
2. **Explicit Staleness Synchronization:** When an operation causes an element to be re-rendered (e.g., table sorting, form reset), explicitly waiting for the old reference to become stale guarantees that the subsequent locator query grabs the newly rendered node rather than the dying one.
