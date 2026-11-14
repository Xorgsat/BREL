"""
EXP-03: Stale Element References and Lifecycle Invalidation.
Investigates how DOM tree mutations invalidate cached WebElement pointers,
reproduces StaleElementReferenceException, and evaluates recovery patterns.
"""

from __future__ import annotations

import time
import pytest
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from selenium_lab.core.wait_manager import WaitManager


@pytest.mark.experiment
def test_exp03_reproduce_stale_element_reference_exception(
    driver: WebDriver,
    controlled_app_url: str,
):
    """
    FAILURE MODE REPRODUCTION:
    1. Locate #victim-element in the DOM.
    2. Click it, which triggers a JavaScript timeout that replaces the parent container's innerHTML.
    3. Attempt to interact with the previously stored WebElement reference after replacement.
    4. Deterministically catches StaleElementReferenceException.
    """
    driver.get(f"{controlled_app_url}/scenarios/stale-dom?recycle_ms=300")
    victim = driver.find_element(By.ID, "victim-element")
    assert victim.is_displayed()

    # Trigger DOM mutation
    victim.click()

    # Wait for the recycling timeout to execute in browser
    time.sleep(0.5)

    # Attempting to access property or click the stale reference must fail
    with pytest.raises(StaleElementReferenceException) as exc_info:
        victim.click()

    assert "stale element reference" in str(exc_info.value).lower()


@pytest.mark.experiment
def test_exp03_staleness_synchronization_and_relocation_remedy(
    driver: WebDriver,
    wait: WaitManager,
    controlled_app_url: str,
):
    """
    REMEDIATION PATTERN:
    1. Store old reference.
    2. Trigger DOM mutation.
    3. Explicitly synchronize on staleness: wait_for_staleness(old_ref).
    4. Re-query the locator to obtain the fresh DOM pointer.
    5. Successfully interact with the fresh element.
    """
    driver.get(f"{controlled_app_url}/scenarios/stale-dom?recycle_ms=300")
    victim_locator = (By.ID, "victim-element")
    old_victim = driver.find_element(*victim_locator)

    # Trigger DOM replacement
    old_victim.click()

    # 1. Wait for the old node to be detached/invalidated
    is_stale = wait.wait_for_staleness(old_victim, timeout=5.0)
    assert is_stale is True

    # 2. Re-locate fresh node
    fresh_victim = wait.wait_for_visibility(victim_locator, timeout=5.0)
    assert "recycled" in fresh_victim.get_attribute("class")
    assert fresh_victim.text == "Recycled Button Node"


@pytest.mark.experiment
def test_exp03_dynamic_controls_stale_checkbox(
    driver: WebDriver,
    wait: WaitManager,
    internet_app_url: str,
):
    """
    PUBLIC BENCHMARK:
    The Internet /dynamic_controls checkbox removal:
    1. Locate checkbox element.
    2. Click 'Remove' button.
    3. Wait for staleness of checkbox element.
    4. Verify checkbox is completely gone from DOM.
    """
    driver.get(f"{internet_app_url}/dynamic_controls")
    checkbox = driver.find_element(By.CSS_SELECTOR, "#checkbox input")
    remove_btn = driver.find_element(By.CSS_SELECTOR, "#checkbox-example button")

    remove_btn.click()

    # Synchronize on staleness of the checkbox reference
    wait.wait_for_staleness(checkbox, timeout=10.0)

    # Checkbox reference must now be stale
    with pytest.raises(StaleElementReferenceException):
        _ = checkbox.is_displayed()

    # Verification message appears
    message = wait.wait_for_visibility((By.ID, "message"), timeout=5.0)
    assert "It's gone!" in message.text
