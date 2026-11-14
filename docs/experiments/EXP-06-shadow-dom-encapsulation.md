# EXP-06: Shadow DOM Encapsulation and Piercing

**Experiment ID:** EXP-06  
**Category:** Web Components & Shadow Root Encapsulation  
**Status:** Verified & Passing (3/3 Tests Passed)  
**Author:** Principal SDET / Reliability Engineering Specialist  

---

## 1. Hypothesis
Shadow DOM encapsulates styling and DOM subtrees inside a shadow root. According to the W3C WebDriver specification, standard document-level CSS selectors and XPath expressions cannot pierce shadow boundaries, causing `NoSuchElementException`. Standardized access requires obtaining the `ShadowRoot` reference from the shadow host element and executing CSS queries scoped specifically to that root.

---

## 2. Experimental Setup
- **Target Applications:**
  - Controlled Local App (`/scenarios/shadow-dom`)
  - UI Testing Playground (`/shadowdom` with `<guid-generator>`)
- **Scenarios Investigated:**
  1. Direct document query across shadow boundary (asserting `NoSuchElementException`).
  2. XPath query attempting to pierce shadow boundary (confirming W3C XPath limitation).
  3. Standard W3C `host.shadow_root` query using CSS selector.
  4. Real-world interaction with UITAP shadow component (`#buttonGenerate` and `#editField`).

---

## 3. Empirical Observations & Results

| Test Scenario | Query Approach | Outcome | Observed Behavior |
|---|---|---|---|
| `test_exp06_direct_lookup_fails_across_shadow_boundary` | Document-level `find_element(By.ID)` & XPath | **CONFIRMED** | Both raised `NoSuchElementException`. |
| `test_exp06_w3c_shadow_root_traversal` | `host.shadow_root.find_element(By.CSS_SELECTOR)` | **PASSED** | Accessed `#shadow-content` and `#shadow-btn` successfully. |
| `test_exp06_uitap_shadow_dom_guid_generator` | `guid-generator.shadow_root` | **PASSED** | Clicked `#buttonGenerate`, read dynamic GUID from `#editField`. |

---

## 4. Engineering Conclusion
1. **XPath Incompatibility:** XPath engines operate strictly on the main document XML/HTML DOM tree and have no specification for crossing ShadowRoot boundaries. Tests interacting with Web Components or Shadow DOM **must** use CSS selectors scoped to the shadow root.
2. **Framework Contrast:** Selenium WebDriver requires explicit programmatic extraction of `element.shadow_root` followed by scoped queries. In contrast, Playwright's locator engine pierces open shadow roots by default for standard CSS selectors.
