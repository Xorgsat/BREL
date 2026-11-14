"""
EXP-13: Race Conditions and Timing Interleaving Experiments.
Investigates race conditions where user interactions clash with asynchronous
JavaScript event binding or DOM state transitions, reproducing flakiness.
"""

from __future__ import annotations

import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from selenium_lab.core.wait_manager import WaitManager


@pytest.mark.experiment
def test_exp13_reproduce_premature_interaction_race_loss(
    driver: WebDriver,
    controlled_app_url: str,
):
    """
    RACE CONDITION REPRODUCTION:
    The target application delays listener attachment by 300ms.
    Immediately clicking the element (< 50ms) triggers the click handler before
    the handler state is committed, producing RACE_LOST_CLICK_IGNORED.
    """
    driver.get(f"{controlled_app_url}/scenarios/race-condition?race_window_ms=300")
    btn = driver.find_element(By.ID, "race-trigger-btn")

    # Immediate naive click races the JS event binding window
    btn.click()

    status = driver.find_element(By.ID, "race-status").text
    final_state = driver.find_element(By.ID, "final-state").text

    assert status == "RACE_LOST_CLICK_IGNORED"
    assert final_state == "FAILED_EARLY_INTERACTION"


@pytest.mark.experiment
def test_exp13_synchronized_interaction_race_prevention(
    driver: WebDriver,
    wait: WaitManager,
    controlled_app_url: str,
):
    """
    RACE CONDITION REMEDIATION:
    Waits for the application readiness condition (e.g. JS readiness or state flag)
    before dispatching the interaction, guaranteeing deterministic state commitment.
    """
    race_window = 200
    driver.get(f"{controlled_app_url}/scenarios/race-condition?race_window_ms={race_window}")

    # Synchronize on the listenerAttached JS state flag
    wait.wait_for_javascript_condition("return window.listenerAttached === true;", timeout=5.0)

    btn = driver.find_element(By.ID, "race-trigger-btn")
    btn.click()

    status = driver.find_element(By.ID, "race-status").text
    final_state = driver.find_element(By.ID, "final-state").text

    assert status == "RACE_WON_STATE_COMMITTED"
    assert final_state == "SUCCESS_TOKEN_ACCEPTED"
