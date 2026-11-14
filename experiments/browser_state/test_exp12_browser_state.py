"""
EXP-12: Browser Navigation and State Persistence Experiments.
Investigates browser storage mechanisms (Cookies, localStorage, sessionStorage),
history navigation transitions (back, forward, refresh), and state leakage prevention.
"""

from __future__ import annotations

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from selenium_lab.core.wait_manager import WaitManager


@pytest.mark.experiment
def test_exp12_cookie_lifecycle_and_isolation(
    driver: WebDriver,
    controlled_app_url: str,
):
    """
    COOKIE PERSISTENCE AND MANIPULATION:
    Injects custom session cookie, verifies presence via WebDriver API,
    deletes cookie, and asserts complete cleanup.
    """
    driver.get(controlled_app_url)

    # Inject cookie
    test_cookie = {"name": "brel_auth_token", "value": "sec_token_99812", "path": "/"}
    driver.add_cookie(test_cookie)

    retrieved = driver.get_cookie("brel_auth_token")
    assert retrieved is not None
    assert retrieved["value"] == "sec_token_99812"

    # Delete cookie
    driver.delete_cookie("brel_auth_token")
    assert driver.get_cookie("brel_auth_token") is None


@pytest.mark.experiment
def test_exp12_storage_persistence_across_refresh(
    driver: WebDriver,
    controlled_app_url: str,
):
    """
    WEB STORAGE PERSISTENCE:
    Sets localStorage and sessionStorage items via JavaScript, triggers page reload,
    and verifies that localStorage survives reload while session boundaries are maintained.
    """
    driver.get(controlled_app_url)

    # Set keys
    driver.execute_script("localStorage.setItem('brel_theme', 'dark');")
    driver.execute_script("sessionStorage.setItem('brel_session', 'sess_active');")

    # Refresh page
    driver.refresh()

    local_val = driver.execute_script("return localStorage.getItem('brel_theme');")
    session_val = driver.execute_script("return sessionStorage.getItem('brel_session');")

    assert local_val == "dark"
    assert session_val == "sess_active"

    # Clean storage
    driver.execute_script("localStorage.clear(); sessionStorage.clear();")
    assert driver.execute_script("return localStorage.getItem('brel_theme');") is None


@pytest.mark.experiment
def test_exp12_history_navigation_back_and_forward(
    driver: WebDriver,
    wait: WaitManager,
    controlled_app_url: str,
):
    """
    BROWSER HISTORY NAVIGATION:
    Navigates Page A -> Page B -> driver.back() -> driver.forward()
    and asserts URL and DOM state synchronization at each step.
    """
    url_a = f"{controlled_app_url}/scenarios/dynamic-render"
    url_b = f"{controlled_app_url}/scenarios/stale-dom"

    # Step 1: Navigate to A
    driver.get(url_a)
    assert "Dynamic Render" in driver.title

    # Step 2: Navigate to B
    driver.get(url_b)
    assert "Stale DOM" in driver.title

    # Step 3: Browser Back to A
    driver.back()
    wait.wait_for_url_to_contain("dynamic-render", timeout=5.0)
    assert "Dynamic Render" in driver.title

    # Step 4: Browser Forward to B
    driver.forward()
    wait.wait_for_url_to_contain("stale-dom", timeout=5.0)
    assert "Stale DOM" in driver.title
