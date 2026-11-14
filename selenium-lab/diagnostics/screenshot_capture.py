"""
Screenshot Capture Module for BREL Selenium Lab.
Safely saves viewport snapshots to isolated artifact directories.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver

logger = logging.getLogger(__name__)


class ScreenshotCapture:
    """Safely captures and saves browser screenshots on demand or upon test failure."""

    @staticmethod
    def capture(
        driver: WebDriver,
        destination_path: Path,
        filename: Optional[str] = None,
    ) -> Optional[Path]:
        """
        Capture viewport screenshot and write to destination_path.
        Returns the absolute path to the saved file or None if capture failed.
        """
        try:
            destination_path.mkdir(parents=True, exist_ok=True)
            file_name = filename or "screenshot.png"
            full_path = destination_path / file_name

            success = driver.save_screenshot(str(full_path))
            if success:
                logger.info(f"Screenshot successfully saved: {full_path}")
                return full_path
            else:
                logger.warning(f"driver.save_screenshot returned False for {full_path}")
                return None
        except WebDriverException as e:
            logger.error(f"Failed to capture screenshot: {e}")
            return None
