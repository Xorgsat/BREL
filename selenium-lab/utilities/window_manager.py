"""
Window and Tab Management Utility for BREL Selenium Lab.
Orchestrates multi-tab switching, popup detection, and handle synchronization.
"""

from __future__ import annotations

import logging
from typing import List, Optional, Set

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

from ..config.settings import settings

logger = logging.getLogger(__name__)


class WindowManager:
    """Manages browser windows, tabs, and handle transitions."""

    def __init__(self, driver: WebDriver, default_timeout: Optional[float] = None) -> None:
        self.driver = driver
        self.timeout = default_timeout or settings.DEFAULT_TIMEOUT

    def get_current_handle(self) -> str:
        return self.driver.current_window_handle

    def get_all_handles(self) -> List[str]:
        return self.driver.window_handles

    def wait_for_new_window(
        self,
        current_handles: Set[str],
        timeout: Optional[float] = None,
    ) -> str:
        """Wait for a new window handle to appear and return its handle ID."""
        to = timeout or self.timeout
        wait = WebDriverWait(self.driver, timeout=to, poll_frequency=settings.POLL_FREQUENCY)

        def _has_new_handle(d: WebDriver) -> str | bool:
            diff = set(d.window_handles) - current_handles
            if diff:
                return next(iter(diff))
            return False

        try:
            new_handle = wait.until(_has_new_handle)
            logger.debug(f"New window handle detected: {new_handle}")
            return str(new_handle)
        except TimeoutException as e:
            raise TimeoutException(
                f"Timed out after {to}s waiting for new window handle. Known: {len(current_handles)}, Current: {len(self.driver.window_handles)}"
            ) from e

    def switch_to_window(self, handle: str) -> None:
        """Switch active browsing context to target window handle."""
        self.driver.switch_to.window(handle)
        logger.debug(f"Switched to window handle: {handle}")

    def switch_to_new_window(
        self,
        known_handles: Set[str],
        timeout: Optional[float] = None,
    ) -> str:
        """Wait for new window handle and immediately switch to it."""
        new_handle = self.wait_for_new_window(known_handles, timeout=timeout)
        self.switch_to_window(new_handle)
        return new_handle

    def close_current_and_switch_back(self, return_handle: str) -> None:
        """Close active child window/tab and safely return to parent handle."""
        self.driver.close()
        self.switch_to_window(return_handle)
        logger.debug(f"Closed window and switched back to: {return_handle}")
