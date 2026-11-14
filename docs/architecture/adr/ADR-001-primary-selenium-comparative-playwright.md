# ADR-001: Selection of Selenium as Primary Framework and Playwright as Comparative Lab

## Context
When designing a senior-level browser reliability lab, there is a temptation to either build two duplicate parallel frameworks from scratch or favor one modern tool exclusively. In enterprise environments, legacy test suites predominantly run Selenium WebDriver, while modern greenfield projects frequently adopt Playwright. Understanding the architectural differences between WebDriver (W3C protocol over HTTP/bi-directional CDP/BiDi) and Playwright (direct WebSocket protocol to internal browser processes) is critical for senior test infrastructure engineers.

## Decision
1. **Primary Framework:** Python + Selenium WebDriver + pytest. Selenium is the primary workhorse for deep-dive investigations into synchronization, browser lifecycle, explicit wait architectures, and low-level DOM mechanics.
2. **Comparative Framework:** TypeScript + Playwright Test. Playwright is used specifically as an experimental comparison layer to benchmark auto-waiting, built-in actionability, browser contexts, and trace diagnostics against identical test scenarios.
3. **No Duplicate Frameworks:** We explicitly reject the antipattern of writing 100% duplicate utility code across both frameworks. Playwright implementations will focus strictly on scenarios that provide high-value architectural comparisons (EXP-01, EXP-02, EXP-03, EXP-04, EXP-06, EXP-11, etc.).

## Consequences
- **Positive:** Demonstrates deep mastery of foundational W3C WebDriver mechanisms while providing evidence-based architectural comparisons with Playwright.
- **Positive:** Avoids redundant maintenance overhead.
- **Trade-off:** Requires managing two language ecosystems (Python 3.12 and Node.js/TypeScript), but this is standard practice in advanced SDET evaluations.
