"""
EXP-14: Browser Compatibility and Engine Variances.
Investigates browser capabilities, user agent reporting, viewport consistency,
and engine identification (Chromium, Gecko, WebKit).
"""

from __future__ import annotations

import pytest
from selenium.webdriver.remote.webdriver import WebDriver


@pytest.mark.experiment
def test_exp14_browser_engine_telemetry_capture(
    driver: WebDriver,
    controlled_app_url: str,
):
    """
    ENGINE TELEMETRY AUDIT:
    Extracts and asserts browser name, version, and platform metadata.
    Ensures that test infrastructure records exact browser binary details.
    """
    driver.get(controlled_app_url)

    capabilities = driver.capabilities
    browser_name = capabilities.get("browserName", "").lower()
    browser_version = capabilities.get("browserVersion", "")
    user_agent = driver.execute_script("return navigator.userAgent;")

    assert browser_name in ("chrome", "firefox", "msedge", "edge", "safari")
    assert browser_version != ""
    assert "Mozilla" in user_agent

    # Validate viewport geometry configured in BrowserConfig (1920x1080)
    window_rect = driver.get_window_rect()
    assert window_rect["width"] >= 1280
    assert window_rect["height"] >= 720


@pytest.mark.experiment
def test_exp14_headless_rendering_integrity(
    driver: WebDriver,
    controlled_app_url: str,
):
    """
    HEADLESS CONSISTENCY CHECK:
    Verifies that canvas and client rendering work consistently in headless mode.
    """
    driver.get(f"{controlled_app_url}/scenarios/dynamic-render")

    # Evaluate device pixel ratio and color depth
    dpr = driver.execute_script("return window.devicePixelRatio;")
    color_depth = driver.execute_script("return screen.colorDepth;")

    assert dpr > 0
    assert color_depth >= 24
