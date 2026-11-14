# ADR-006: Test Isolation and Parallel Worker Resource Allocation

## Context
Running browser automation in parallel (e.g., using `pytest -n auto` via `pytest-xdist` or Playwright parallel workers) frequently introduces catastrophic flakiness due to shared mutable state:
- Shared download directories causing file overwrite collisions.
- Shared user sessions or browser cookies leaking across concurrent tests.
- Shared ports or port exhaustion.
- CPU/Memory saturation leading to timing-out waits.

## Decision
1. **Total WebDriver Process Isolation:** Each test method receives its own dedicated browser session initialized and terminated strictly within the test lifecycle fixture (`scope="function"`). No WebDriver instance is ever shared across concurrent threads or worker processes.
2. **Ephemeral Worker Directories:** Each parallel test execution creates an isolated, ephemeral sandbox directory for downloads, screenshots, and logs keyed by worker ID and UUID (`artifacts/workers/{worker_id}_{uuid}`).
3. **Controlled Concurrency Limits:** Parallelism is defaulted to a conservative maximum (e.g., 2–4 workers) tuned to host system resource constraints, avoiding thread contention and timing skew.

## Consequences
- **Positive:** Complete immunity against inter-test state contamination and file system collisions.
- **Positive:** Tests can execute in random orders without flakiness.
- **Trade-off:** Marginal browser startup overhead per test function compared to a shared session, but offset by bulletproof reliability.
