"""
Frame Context Management Utility for BREL Selenium Lab.
Handles frame switching, nested frame traversal, and parent document restoration.
"""

from __future__ import annotations

import logging
from typing import Optional, Union

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ..config.settings import settings

logger = logging.getLogger(__name__)


class FrameManager:
    """Manages browsing context transitions across iframes and framesets."""

    def __init__(self, driver: WebDriver, default_timeout: Optional[float] = None) -> None:
        self.driver = driver
        self.timeout = default_timeout or settings.DEFAULT_TIMEOUT

    def switch_to_frame(
        self,
        frame_reference: Union[int, str, WebElement],
        timeout: Optional[float] = None,
    ) -> None:
        """Wait until frame is available and switch to it."""
        to = timeout or self.timeout
        wait = WebDriverWait(self.driver, timeout=to, poll_frequency=settings.POLL_FREQUENCY)
        try:
            wait.until(EC.frame_to_be_available_and_switch_to_it(frame_reference))
            logger.debug(f"Switched to frame: {frame_reference}")
        except TimeoutException as e:
            raise TimeoutException(f"Timed out after {to}s switching to frame: {frame_reference}") from e

    def switch_to_frame_by_locator(
        self,
        locator: tuple[str, str],
        timeout: Optional[float] = None,
    ) -> None:
        """Locate iframe element and switch context into it."""
        to = timeout or self.timeout
        wait = WebDriverWait(self.driver, timeout=to, poll_frequency=settings.POLL_FREQUENCY)
        try:
            frame_element = wait.until(EC.presence_of_element_located(locator))
            self.driver.switch_to.frame(frame_element)
            logger.debug(f"Switched to frame at locator: {locator}")
        except TimeoutException as e:
            raise TimeoutException(f"Timed out after {to}s locating and switching to frame: {locator}") from e

    def switch_to_parent_frame(self) -> None:
        """Switch context to the immediate parent frame."""
        self.driver.switch_to.parent_frame()
        logger.debug("Switched to parent frame.")

    def switch_to_default_content(self) -> None:
        """Return context to the top-level main document."""
        self.driver.switch_to.default_content()
        logger.debug("Switched to default content.")
