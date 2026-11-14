"""
Browser Options Builder for Selenium WebDriver.
Configures Chrome, Firefox, and Edge capabilities according to reliability standards.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional, Union

from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

from .settings import settings

logger = logging.getLogger(__name__)


class BrowserConfig:
    """Constructs framework-standard browser capabilities and options."""

    @staticmethod
    def get_chrome_options(
        headless: Optional[bool] = None,
        download_dir: Optional[Union[str, Path]] = None,
    ) -> ChromeOptions:
        options = ChromeOptions()
        is_headless = headless if headless is not None else settings.HEADLESS

        if is_headless:
            # Modern Chrome headless mode
            options.add_argument("--headless=new")

        # Container & sandboxing flags for reliability
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-search-engine-choice-screen")

        # Logging preferences for console error extraction
        options.set_capability("goog:loggingPrefs", {"browser": "ALL", "performance": "ALL"})

        # Custom download directory if specified
        if download_dir:
            download_path = str(Path(download_dir).resolve())
            prefs = {
                "download.default_directory": download_path,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,
            }
            options.add_experimental_option("prefs", prefs)

        return options

    @staticmethod
    def get_firefox_options(
        headless: Optional[bool] = None,
        download_dir: Optional[Union[str, Path]] = None,
    ) -> FirefoxOptions:
        options = FirefoxOptions()
        is_headless = headless if headless is not None else settings.HEADLESS

        if is_headless:
            options.add_argument("-headless")

        options.add_argument("--width=1920")
        options.add_argument("--height=1080")
        options.accept_insecure_certs = True

        if download_dir:
            download_path = str(Path(download_dir).resolve())
            options.set_preference("browser.download.folderList", 2)
            options.set_preference("browser.download.dir", download_path)
            options.set_preference(
                "browser.helperApps.neverAsk.saveToDisk",
                "application/octet-stream,text/csv,text/plain,application/pdf",
            )

        return options

    @staticmethod
    def get_edge_options(
        headless: Optional[bool] = None,
        download_dir: Optional[Union[str, Path]] = None,
    ) -> EdgeOptions:
        options = EdgeOptions()
        is_headless = headless if headless is not None else settings.HEADLESS

        if is_headless:
            options.add_argument("--headless=new")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--ignore-certificate-errors")

        if download_dir:
            download_path = str(Path(download_dir).resolve())
            options.add_experimental_option(
                "prefs",
                {
                    "download.default_directory": download_path,
                    "download.prompt_for_download": False,
                },
            )

        return options
