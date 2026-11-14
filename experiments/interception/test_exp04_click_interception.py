"""
EXP-04: Element Interception and Actionability Experiments.
Investigates physical interaction obstacles: overlapping layers, modal backdrops,
and elements outside viewport. Contrasts native click failure with overlay synchronization
and diagnostic JavaScript dispatch.
"""

from __future__ import annotations

import time
import pytest
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from selenium_lab.core.wait_manager import WaitManager


@pytest.mark.experiment
def test_exp04_reproduce_click_intercepted_exception(
    driver: WebDriver,
    controlled_app_url: str,
):
    """
    FAILURE MODE REPRODUCTION:
    Attempts to click #target-action-btn while #blocking-overlay is positioned on top of it.
    W3C WebDriver hit-testing detects that the target element cannot receive pointer events
    at its coordinates, raising ElementClickInterceptedException.
    """
    driver.get(f"{controlled_app_url}/scenarios/click-interception?overlay_ms=3000")
    target_btn = driver.find_element(By.ID, "target-action-btn")

    # Native click while overlay is present must raise ElementClickInterceptedException
    with pytest.raises(ElementClickInterceptedException) as exc_info:
        target_btn.click()

    assert "click intercepted" in str(exc_info.value).lower() or "other element would receive the click" in str(exc_info.value).lower()


@pytest.mark.experiment
def test_exp04_overlay_invisibility_synchronization_remedy(
    driver: WebDriver,
    wait: WaitManager,
    controlled_app_url: str,
):
    """
    RELIABILITY REMEDIATION:
    Wait explicitly for the obscuring overlay to become invisible/detached before clicking.
    """
    driver.get(f"{controlled_app_url}/scenarios/click-interception?overlay_ms=1000")
    overlay_locator = (By.ID, "blocking-overlay")
    target_locator = (By.ID, "target-action-btn")

    # Synchronize on overlay removal
    wait.wait_for_invisibility(overlay_locator, timeout=5.0)

    # Now clickability check and native click succeed cleanly
    action_btn = wait.wait_for_clickable(target_locator, timeout=5.0)
    action_btn.click()

    feedback = wait.wait_for_visibility((By.ID, "click-feedback"), timeout=2.0)
    assert feedback.text == "Action Button Successfully Clicked!"


@pytest.mark.experiment
def test_exp04_uitap_hidden_layers_interception(
    driver: WebDriver,
    uitap_app_url: str,
):
    """
    PUBLIC BENCHMARK (UITAP):
    On /hiddenlayers, clicking the green button generates a blue button directly over it.
    Attempting to click the green button a second time raises ElementClickInterceptedException.
    """
    driver.get(f"{uitap_app_url}/hiddenlayers")
    green_btn = driver.find_element(By.ID, "greenButton")

    # First click succeeds
    green_btn.click()

    # Second click is intercepted by the newly spawned blue button
    with pytest.raises(ElementClickInterceptedException):
        green_btn.click()


@pytest.mark.experiment
def test_exp04_diagnostic_js_click_contrast(
    driver: WebDriver,
    controlled_app_url: str,
):
    """
    DIAGNOSTIC EXPERIMENT:
    Demonstrates that driver.execute_script("arguments[0].click()", target) bypasses
    browser pointer hit-testing and actionability checks.
    IMPORTANT ARCHITECTURAL RULE: JS click must not be used as an automatic workaround
    for normal user interactions, as it does not simulate authentic user behavior.
    """
    driver.get(f"{controlled_app_url}/scenarios/click-interception?overlay_ms=4000")
    target_btn = driver.find_element(By.ID, "target-action-btn")

    # Native click fails due to overlay
    with pytest.raises(ElementClickInterceptedException):
        target_btn.click()

    # Diagnostic JS click directly invokes DOM click() event handler, bypassing overlay!
    driver.execute_script("arguments[0].click();", target_btn)

    feedback = driver.find_element(By.ID, "click-feedback")
    assert feedback.text == "Action Button Successfully Clicked!"
