# EXP-10: Dynamic Selectors and Locator Reliability

**Experiment ID:** EXP-10  
**Category:** Locator Resilience & Selector Strategy  
**Status:** Verified & Passing (3/3 Tests Passed)  
**Author:** Principal SDET / Reliability Engineering Specialist  

---

## 1. Hypothesis
Locators that bind to auto-generated dynamic IDs, composite class names with indeterminate ordering, or text containing Unicode whitespace variations (`\u00A0`) exhibit high fragility. Adopting semantic, user-facing role locators and robust XPath whitespace normalization eliminates selector-induced flakiness.

---

## 2. Experimental Setup
- **Target Application:** UI Testing Playground (`/dynamicid`, `/classattr`, `/nbsp`)
- **Scenarios Investigated:**
  1. Dynamic ID: Demonstrating that storing an ID from one page render fails upon reload (`NoSuchElementException`), while semantic text locators remain 100% resilient.
  2. Composite Class Attribute: Demonstrating robust matching via `contains(concat(' ', normalize-space(@class), ' '), ' btn-primary ')`.
  3. Non-breaking space pitfall: Demonstrating that regular ASCII space queries fail on `\u00A0`, while whitespace-normalized or translate-based queries succeed.

---

## 3. Empirical Observations & Results

| Scenario | Fragile Query | Result | Resilient Query | Result |
|---|---|---|---|---|
| Dynamic ID | `By.ID(initial_id)` | **FAILED** (`NoSuchElementException`) | `//button[text()='Button with Dynamic ID']` | **PASSED** |
| Composite Class | `@class='btn-primary'` | **FAILED** (misses composite) | `//button[contains(concat(' ', normalize-space(@class), ' '), ' btn-primary ')]` | **PASSED** |
| Non-Breaking Space | `//button[text()='My Button']` | **FAILED** (space $\neq$ `\u00A0`) | `//button[normalize-space(translate(text(), '\u00a0', ' ')) = 'My Button']` | **PASSED** |

---

## 4. Engineering Conclusion
1. **Never Depend on Framework Generated IDs:** Modern frontends (React, Angular, ASP.NET) often generate transient GUIDs or hashed class names (CSS Modules). Always anchor locators to accessible roles, test IDs, or stable semantic text.
2. **Whitespace Awareness:** Hidden Unicode non-breaking spaces are a frequent source of "mysterious" locator failures.
