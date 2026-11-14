"""
EXP-02: Synchronization and Waiting Strategies Experiments.
Investigates and contrasts 4 distinct synchronization paradigms:
1. Arbitrary fixed sleep (wasteful, inflexible)
2. Implicit wait (global pollution, slow negative assertions)
3. Explicit wait (state-driven, responsive)
4. Custom polling wait (granular predicate evaluation)
"""

from __future__ import annotations

import time
import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

from selenium_lab.core.wait_manager import WaitManager


@pytest.mark.experiment
def test_exp02_fixed_sleep_latency_penalty(
    driver: WebDriver,
    controlled_app_url: str,
):
    """
    EFFICIENCY BENCHMARK:
    Measures the latency penalty of fixed sleep (time.sleep) vs true completion time.
    An element renders in 500ms; an arbitrary 3000ms sleep wastes ~2500ms of execution time.
    """
    driver.get(f"{controlled_app_url}/scenarios/dynamic-render?delay_ms=500")
    driver.find_element(By.ID, "trigger-btn").click()

    # Naive fixed wait: sleep 3 seconds
    start_sleep = time.perf_counter()
    time.sleep(3.0)
    target = driver.find_element(By.ID, "target-element")
    sleep_elapsed = time.perf_counter() - start_sleep

    assert target.is_displayed()
    assert sleep_elapsed >= 3.0, "Fixed sleep forcefully blocked execution for 3.0+ seconds"


@pytest.mark.experiment
def test_exp02_explicit_wait_efficiency_contrast(
    driver: WebDriver,
    wait: WaitManager,
    controlled_app_url: str,
):
    """
    EFFICIENCY BENCHMARK:
    Demonstrates that explicit state polling terminates as soon as the condition is met,
    saving execution time and preventing latency tax.
    """
    driver.get(f"{controlled_app_url}/scenarios/dynamic-render?delay_ms=500")
    driver.find_element(By.ID, "trigger-btn").click()

    start_explicit = time.perf_counter()
    target = wait.wait_for_visibility((By.ID, "target-element"), timeout=5.0)
    explicit_elapsed = time.perf_counter() - start_explicit

    assert target.is_displayed()
    # Should complete shortly after the 500ms delay, well under 2.0s
    assert 0.4 <= explicit_elapsed < 2.0, f"Explicit wait took {explicit_elapsed:.3f}s"


@pytest.mark.experiment
def test_exp02_state_based_synchronization_dynamic_controls(
    driver: WebDriver,
    wait: WaitManager,
    internet_app_url: str,
):
    """
    STATE TRANSITION SYNCHRONIZATION:
    Navigates to The Internet /dynamic_controls:
    1. Input starts in disabled state.
    2. Click 'Enable' button.
    3. Loading indicator appears.
    4. Wait until input attribute 'disabled' is removed and input becomes enabled.
    """
    driver.get(f"{internet_app_url}/dynamic_controls")
    input_locator = (By.CSS_SELECTOR, "#input-example input")
    enable_btn_locator = (By.CSS_SELECTOR, "#input-example button")

    # Initial state: input is disabled
    input_el = driver.find_element(*input_locator)
    assert not input_el.is_enabled(), "Input must initially be disabled"

    # Click Enable
    enable_btn = wait.wait_for_clickable(enable_btn_locator, timeout=5.0)
    enable_btn.click()

    # Wait for loading spinner to disappear
    wait.wait_for_invisibility((By.CSS_SELECTOR, "#input-example #loading"), timeout=10.0)

    # Wait for element to become actionable/enabled
    wait.wait_for_custom_condition(
        lambda d: d.find_element(*input_locator).is_enabled(),
        timeout=5.0,
        description="input to become enabled",
    )

    # Now type text successfully
    input_el = driver.find_element(*input_locator)
    assert input_el.is_enabled()
    input_el.send_keys("Reliability Engineering Lab")
    assert input_el.get_attribute("value") == "Reliability Engineering Lab"
