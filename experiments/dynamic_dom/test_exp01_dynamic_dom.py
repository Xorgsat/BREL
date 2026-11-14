"""
EXP-01: Dynamic DOM and Asynchronous Rendering Experiments.
Investigates browser behaviour and failure modes when interacting with elements
rendered or mutated asynchronously via client-side JavaScript or AJAX.
"""

from __future__ import annotations

import time
import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from selenium_lab.core.wait_manager import WaitManager


@pytest.mark.experiment
def test_exp01_immediate_lookup_failure_on_dynamic_element(
    driver: WebDriver,
    controlled_app_url: str,
):
    """
    FAILURE MODE DEMONSTRATION:
    Attempts immediate element lookup on an element rendered with a 1000ms delay.
    Proves that naive immediate lookup deterministically raises NoSuchElementException.
    """
    driver.get(f"{controlled_app_url}/scenarios/dynamic-render?delay_ms=1000")
    trigger_btn = driver.find_element(By.ID, "trigger-btn")
    trigger_btn.click()

    # Immediate lookup without wait: element does not yet exist in the DOM
    with pytest.raises(NoSuchElementException) as exc_info:
        driver.find_element(By.ID, "target-element")

    assert "target-element" in str(exc_info.value)


@pytest.mark.experiment
def test_exp01_explicit_wait_remediation(
    driver: WebDriver,
    wait: WaitManager,
    controlled_app_url: str,
):
    """
    RELIABILITY REMEDIATION:
    Applies WaitManager explicit condition synchronization.
    Measures duration waited until DOM presence and visibility are satisfied.
    """
    driver.get(f"{controlled_app_url}/scenarios/dynamic-render?delay_ms=800")
    driver.find_element(By.ID, "trigger-btn").click()

    start_time = time.perf_counter()
    element = wait.wait_for_visibility((By.ID, "target-element"), timeout=5.0)
    elapsed = time.perf_counter() - start_time

    assert element.is_displayed()
    assert element.text == "Target Loaded Successfully!"
    # Ensure wait was state-driven (elapsed >= ~0.8s and < 5.0s)
    assert 0.7 <= elapsed <= 3.0, f"Expected elapsed ~0.8s, observed {elapsed:.3f}s"


@pytest.mark.experiment
def test_exp01_hidden_vs_rendered_lifecycle_contrast(
    driver: WebDriver,
    wait: WaitManager,
    internet_app_url: str,
):
    """
    BEHAVIOURAL LIFECYCLE INVESTIGATION:
    Compares two distinct asynchronous rendering models:
    - Case A: Element present in DOM at page load, but hidden via CSS display: none (/dynamic_loading/1)
    - Case B: Element completely absent from DOM until injected by JavaScript (/dynamic_loading/2)
    """
    # Case A: Hidden Element
    driver.get(f"{internet_app_url}/dynamic_loading/1")
    finish_locator = (By.CSS_SELECTOR, "#finish h4")

    # Present immediately before click
    hidden_node = wait.wait_for_presence(finish_locator, timeout=2.0)
    assert not hidden_node.is_displayed(), "Element must initially be hidden"

    # Case B: Absent Element
    driver.get(f"{internet_app_url}/dynamic_loading/2")
    # Must NOT be present in DOM before start
    with pytest.raises(NoSuchElementException):
        driver.find_element(*finish_locator)

    # Trigger render on Case B
    start_btn = wait.wait_for_clickable((By.CSS_SELECTOR, "#start button"), timeout=5.0)
    start_btn.click()

    # Wait for completion on Case B
    rendered_node = wait.wait_for_visibility(finish_locator, timeout=10.0)
    assert rendered_node.is_displayed()
    assert rendered_node.text == "Hello World!"
