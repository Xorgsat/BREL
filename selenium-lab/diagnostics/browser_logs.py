"""
Browser Console Log Harvester for BREL Selenium Lab.
Extracts browser-level console warnings, errors, and performance traces where supported.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver

logger = logging.getLogger(__name__)


class BrowserLogCollector:
    """Extracts and persists browser console logs."""

    @staticmethod
    def get_console_logs(driver: WebDriver) -> List[Dict[str, Any]]:
        """Retrieve browser console log entries if supported by current driver."""
        try:
            available_types = driver.log_types
            if "browser" in available_types:
                return driver.get_log("browser")
            return []
        except (WebDriverException, AttributeError) as e:
            logger.debug(f"Console logging not accessible on current browser/driver: {e}")
            return []

    @staticmethod
    def save_console_logs(driver: WebDriver, destination_dir: Path, filename: str = "console_logs.json") -> Path:
        """Fetch and serialize browser console logs to a JSON artifact."""
        logs = BrowserLogCollector.get_console_logs(driver)
        destination_dir.mkdir(parents=True, exist_ok=True)
        file_path = destination_dir / filename

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2)

        return file_path
