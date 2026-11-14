"""
EXP-11: Delayed Network Responses and Server Latency Experiments.
Investigates browser and WebDriver behaviour under delayed backend responses,
page load timeout thresholds, and asynchronous API data delivery.
"""

from __future__ import annotations

import time
import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from selenium_lab.core.wait_manager import WaitManager


@pytest.mark.experiment
def test_exp11_server_side_load_delay_timeout(
    driver: WebDriver,
    uitap_app_url: str,
):
    """
    PAGE LOAD TIMEOUT FAILURE DEMONSTRATION:
    UITAP /loaddelay delays response headers by ~5.4 seconds.
    Setting a strict page load timeout of 2.0s deterministically induces TimeoutException.
    """
    driver.set_page_load_timeout(2.0)

    with pytest.raises(TimeoutException):
        driver.get(f"{uitap_app_url}/loaddelay")


@pytest.mark.experiment
def test_exp11_server_side_load_delay_remediation(
    driver: WebDriver,
    wait: WaitManager,
    uitap_app_url: str,
):
    """
    PAGE LOAD TIMEOUT REMEDIATION:
    Configures adequate page load timeout (15.0s), navigates, and verifies
    button appearing after server delay.
    """
    driver.set_page_load_timeout(15.0)

    start_time = time.perf_counter()
    driver.get(f"{uitap_app_url}/loaddelay")
    elapsed = time.perf_counter() - start_time

    # Verify that the server delayed the navigation
    assert elapsed >= 4.0, f"Expected server load delay of >= 4s, observed {elapsed:.2f}s"

    # Button is immediately available after DOM load event fires
    btn = wait.wait_for_visibility((By.CSS_SELECTOR, "button.btn-primary"), timeout=5.0)
    assert "Button Appearing After Delay" in btn.text
