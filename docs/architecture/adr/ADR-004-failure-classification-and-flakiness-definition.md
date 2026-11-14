# ADR-004: Failure Classification Taxonomy and Rigorous Flakiness Definition

## Context
In many test organizations, any test failure that passes upon rerun is casually dismissed as "flaky" without identifying root cause. Conversely, some teams classify genuine environment bugs as test automation defects. Without a standardized taxonomy and strict mathematical definitions, flakiness analysis becomes subjective and unscientific.

## Decision
1. **Flaky Test Definition:** A test is classified as **FLAKY** if and only if it exhibits non-deterministic outcomes ($P(\text{Pass}) \in (0, 1)$) across multiple executions under identical application and environment configurations, OR if it fails on its initial attempt and passes on a subsequent retry within the same run.
2. **Failure Taxonomy:** All execution failures are categorized into exactly one of 11 standardized classes:
   1. `Synchronization`: Condition timeout before DOM reached expected state.
   2. `Locator`: Target element selector not matched in DOM.
   3. `DOM Lifecycle`: Stale element pointer caused by node detach/replace.
   4. `Actionability`: Element obscured by overlay, disabled, or offscreen.
   5. `Navigation`: Unexpected URL, redirection failure, or route hang.
   6. `Network`: Socket timeout, HTTP 5xx error, or gateway abort.
   7. `Browser Crash`: WebDriver or browser binary abruptly terminated.
   8. `Infrastructure`: OS driver mismatch, port conflict, or memory exhaustion.
   9. `State Contamination`: Leakage of storage, cookies, or child windows from prior test.
   10. `Application Defect`: Genuine assertion failure confirming a product bug.
   11. `Unknown`: Insufficient telemetry to categorize.

## Consequences
- **Positive:** Enables automated root-cause clustering and metric reporting.
- **Positive:** Prevents sweeps of unexplained failures under generic "flaky" labels.
