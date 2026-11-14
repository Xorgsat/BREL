# EXP-05: Frames and Nested Frames Context Switching

**Experiment ID:** EXP-05  
**Category:** Context Switching & Document Isolation  
**Status:** Verified & Passing (3/3 Tests Passed)  
**Author:** Principal SDET / Reliability Engineering Specialist  

---

## 1. Hypothesis
Browsers maintain strict context boundaries between top-level documents and child iframes or framesets. Elements inside an iframe are completely invisible to queries executed against the top-level document context, producing `NoSuchElementException`. Robust automation requires structured context transitions, hierarchical traversal, and safe parent/default content restoration.

---

## 2. Experimental Setup
- **Target Applications:**
  - Controlled Local App (`/scenarios/frames` with child iframe `/scenarios/child-frame`)
  - The Internet (`/nested_frames` frameset)
- **Scenarios Investigated:**
  1. Direct element query without switching context (asserting `NoSuchElementException`).
  2. Frame context transition, in-frame interaction, and return to default content.
  3. Hierarchical navigation across nested frameset: `top` -> `left` -> `parent` -> `middle` -> `parent` -> `right` -> `default_content` -> `bottom`.

---

## 3. Empirical Observations & Results

| Test Scenario | Context Switch Operation | Outcome | Telemetry & Notes |
|---|---|---|---|
| `test_exp05_direct_lookup_fails_without_frame_switch` | None (query from top document) | **CONFIRMED** | `NoSuchElementException` raised as element is isolated within frame context. |
| `test_exp05_frame_switch_and_interaction` | `switch_to.frame("child-frame")` | **PASSED** | Heading read, button clicked, text mutated, context cleanly restored to top document. |
| `test_exp05_nested_frameset_hierarchical_traversal` | Multi-level hierarchical traversal | **PASSED** | Validated: `LEFT`, `MIDDLE`, `RIGHT`, and `BOTTOM` frame contents. |

---

## 4. Engineering Conclusion
1. **Context State Persistence:** In Selenium WebDriver, switching to a frame mutates the active context of the session. If a test fails while inside a frame, subsequent cleanup or teardown fixtures must ensure context is restored to `default_content()`, or the subsequent test might start within an unexpected sub-frame if the session were shared.
2. **Session Isolation Benefit:** Function-scoped browser sessions completely eliminate frame context leakage between tests.
