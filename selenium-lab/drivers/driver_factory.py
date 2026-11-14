"""
WebDriver Factory for Browser Reliability Engineering Lab.
Instantiates, configures, and standardizes WebDriver lifecycle.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional, Union

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver

from ..config.browser_config import BrowserConfig
from ..config.settings import settings

logger = logging.getLogger(__name__)


class DriverFactory:
    """Factory responsible for instantiating and configuring WebDriver instances."""

    @staticmethod
    def create_driver(
        browser_name: Optional[str] = None,
        headless: Optional[bool] = None,
        download_dir: Optional[Union[str, Path]] = None,
        page_load_timeout: Optional[float] = None,
    ) -> WebDriver:
        """
        Create and return a configured WebDriver instance.
        Uses Selenium Manager automatically for browser/driver resolution.
        """
        browser = (browser_name or settings.BROWSER).lower()
        timeout = page_load_timeout or settings.DEFAULT_TIMEOUT

        logger.info(f"Initializing WebDriver for browser='{browser}', headless={headless}")

        if browser in ("chrome", "googlechrome", "chromium"):
            options = BrowserConfig.get_chrome_options(headless=headless, download_dir=download_dir)
            driver = webdriver.Chrome(options=options)
        elif browser in ("firefox", "mozilla", "gecko"):
            options = BrowserConfig.get_firefox_options(headless=headless, download_dir=download_dir)
            driver = webdriver.Firefox(options=options)
        elif browser in ("edge", "msedge"):
            options = BrowserConfig.get_edge_options(headless=headless, download_dir=download_dir)
            driver = webdriver.Edge(options=options)
        else:
            raise ValueError(f"Unsupported browser engine requested: '{browser}'. Supported: chrome, firefox, edge")

        # Standardize timeouts across sessions
        driver.set_page_load_timeout(timeout)
        driver.set_script_timeout(timeout)

        # Enforce ADR-002: Implicit wait strictly 0.0 to prevent wait pollution
        driver.implicitly_wait(0.0)

        logger.info(f"WebDriver successfully created: session_id={driver.session_id}")
        return driver
