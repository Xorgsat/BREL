"""
EXP-07: JavaScript Dialogs and Modal Interruptions.
Investigates synchronous, thread-blocking browser dialogs (Alert, Confirm, Prompt),
context switching to alert instances, and resulting DOM state verification.
"""

from __future__ import annotations

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from selenium_lab.utilities.alert_manager import AlertManager
from selenium_lab.core.wait_manager import WaitManager


@pytest.mark.experiment
def test_exp07_javascript_alert_acceptance(
    driver: WebDriver,
    alert_mgr: AlertManager,
    wait: WaitManager,
    internet_app_url: str,
):
    """
    MODAL ALERT SYNCHRONIZATION:
    Navigates to /javascript_alerts, triggers standard alert, captures text,
    accepts dialog, and validates resulting application state.
    """
    driver.get(f"{internet_app_url}/javascript_alerts")

    # Click button to trigger JS Alert
    driver.find_element(By.XPATH, "//button[text()='Click for JS Alert']").click()

    # Synchronize on alert presence, read text, and accept
    text = alert_mgr.accept_alert(timeout=5.0)
    assert text == "I am a JS Alert"

    # Assert DOM outcome
    result_text = wait.wait_for_visibility((By.ID, "result"), timeout=3.0).text
    assert result_text == "You successfully clicked an alert"


@pytest.mark.experiment
def test_exp07_javascript_confirm_ok_and_cancel_states(
    driver: WebDriver,
    alert_mgr: AlertManager,
    wait: WaitManager,
    internet_app_url: str,
):
    """
    MODAL CONFIRM DUAL-STATE VERIFICATION:
    Tests both affirmative (accept) and cancellation (dismiss) branches of window.confirm().
    """
    driver.get(f"{internet_app_url}/javascript_alerts")
    confirm_btn = (By.XPATH, "//button[text()='Click for JS Confirm']")

    # Branch 1: Accept (OK)
    driver.find_element(*confirm_btn).click()
    text = alert_mgr.accept_alert(timeout=5.0)
    assert text == "I am a JS Confirm"
    assert driver.find_element(By.ID, "result").text == "You clicked: Ok"

    # Branch 2: Dismiss (Cancel)
    driver.find_element(*confirm_btn).click()
    text = alert_mgr.dismiss_alert(timeout=5.0)
    assert text == "I am a JS Confirm"
    assert driver.find_element(By.ID, "result").text == "You clicked: Cancel"


@pytest.mark.experiment
def test_exp07_javascript_prompt_text_injection(
    driver: WebDriver,
    alert_mgr: AlertManager,
    wait: WaitManager,
    internet_app_url: str,
):
    """
    MODAL PROMPT INTERACTION:
    Sends text into window.prompt() and validates that the browser passes the input
    back into the JavaScript execution context.
    """
    driver.get(f"{internet_app_url}/javascript_alerts")
    driver.find_element(By.XPATH, "//button[text()='Click for JS Prompt']").click()

    payload = "BREL Reliability Engineering Specialist"
    prompt_msg = alert_mgr.send_keys_and_accept(payload, timeout=5.0)
    assert prompt_msg == "I am a JS prompt"

    result_text = wait.wait_for_visibility((By.ID, "result"), timeout=3.0).text
    assert result_text == f"You entered: {payload}"
