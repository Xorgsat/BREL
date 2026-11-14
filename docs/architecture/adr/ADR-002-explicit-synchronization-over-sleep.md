# ADR-002: Mandating Explicit State-Based Synchronization Over Fixed Sleeps and Implicit Waits

## Context
Browser automation flakiness is overwhelmingly caused by synchronization failures. Junior test suites rely heavily on `time.sleep(N)` or set a blanket `implicitly_wait(10)`.
- `time.sleep(N)` is an antipattern: it either wastes time when an operation finishes early or fails intermittently when background operations experience transient latency spikes.
- `implicitly_wait` is applied globally to every `find_element` call, slowing down negative assertion checks (waiting for disappearance) and conflicting with explicit waits according to official Selenium documentation.

## Decision
1. **Zero Fixed Sleeps:** Arbitrary sleeps are banned in production test scenarios. Sleeps may only be introduced within deliberate diagnostic benchmark experiments specifically designed to measure the cost and inefficiency of fixed waits.
2. **Implicit Wait Disabled:** Implicit wait is set to `0` across all WebDriver sessions.
3. **Centralized Explicit Synchronization:** All test interactions must wait for a concrete, deterministic state transition using a custom `WaitManager` wrapping `WebDriverWait` with custom condition predicates (e.g., element visibility, clickability, DOM staleness, text mutation, URL change, or JS evaluation).

## Consequences
- **Positive:** Execution speed is optimized (tests proceed immediately when conditions are met).
- **Positive:** Dramatic reduction in intermittent flakiness under system load.
- **Negative:** Test code requires thoughtful engineering of exact precondition states rather than blanket delay calls.
