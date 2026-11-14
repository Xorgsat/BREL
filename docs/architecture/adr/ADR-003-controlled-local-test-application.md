# ADR-003: Integration of a Controlled Local Test Application for Deterministic Experiments

## Context
Testing against live third-party demo environments (`the-internet.herokuapp.com` and `uitestingplayground.com`) exposes experiments to uncontrolled external variables:
- Network jitter, DNS latency, and intermediate proxy resets.
- Fixed unconfigurable delays (e.g., 15-second client delays that slow down test execution).
- Inability to programmatically inject microsecond-level race conditions or randomized failure rates.
- Risk of third-party downtime or TLS certificate invalidation (as discovered during empirical probing of UITAP).

## Decision
We implement a lightweight, standalone, asynchronous web application in `controlled-app/` using FastAPI and Uvicorn.
1. The controlled application runs locally on `http://127.0.0.1:8000`.
2. It provides endpoints with configurable parameters:
   - `/scenarios/dynamic-render?delay_ms=X`: Configurable insertion of dynamic DOM elements.
   - `/scenarios/stale-dom?recycle_ms=X`: Programmatic destruction and recreation of elements.
   - `/scenarios/click-interception?overlay_ms=X`: Temporary animated overlays.
   - `/scenarios/race-condition?race_window_ms=X`: Race condition simulations.
   - `/scenarios/delayed-api?delay_ms=X&failure_rate=Y&seed=Z`: Deterministic, seedable API degradation.
3. Every test specifies whether it targets public demo environments or the controlled local app.

## Consequences
- **Positive:** Enables statistically sound repeatability benchmarks (50–100 runs) that measure test framework mechanics without external network noise.
- **Positive:** Enables deterministic injection of edge cases that cannot be produced on static demo sites.
- **Maintenance:** Adds a lightweight local server to test fixtures, automatically started during test execution if not already running.
