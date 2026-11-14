"""
JavaScript Dialog and Alert Management Utility for BREL Selenium Lab.
Synchronizes and handles Alert, Confirm, and Prompt modal dialogs.
"""

from __future__ import annotations

import logging
from typing import Optional

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ..config.settings import settings

logger = logging.getLogger(__name__)


class AlertManager:
    """Manages modal browser dialogs (Alert, Confirm, Prompt)."""

    def __init__(self, driver: WebDriver, default_timeout: Optional[float] = None) -> None:
        self.driver = driver
        self.timeout = default_timeout or settings.DEFAULT_TIMEOUT

    def wait_for_alert(self, timeout: Optional[float] = None) -> Alert:
        """Wait until a JavaScript alert/dialog is present and return it."""
        to = timeout or self.timeout
        wait = WebDriverWait(self.driver, timeout=to, poll_frequency=settings.POLL_FREQUENCY)
        try:
            alert = wait.until(EC.alert_is_present())
            logger.debug(f"Alert detected with text: '{alert.text}'")
            return alert  # type: ignore[return-value]
        except TimeoutException as e:
            raise TimeoutException(f"Timed out after {to}s waiting for JavaScript alert to appear.") from e

    def get_alert_text(self, timeout: Optional[float] = None) -> str:
        """Wait for alert and return its message text."""
        alert = self.wait_for_alert(timeout)
        return alert.text

    def accept_alert(self, timeout: Optional[float] = None) -> str:
        """Wait for alert, record text, accept it (OK), and return message."""
        alert = self.wait_for_alert(timeout)
        text = alert.text
        alert.accept()
        logger.debug(f"Accepted alert with text: '{text}'")
        return text

    def dismiss_alert(self, timeout: Optional[float] = None) -> str:
        """Wait for confirm/dialog, dismiss it (Cancel), and return message."""
        alert = self.wait_for_alert(timeout)
        text = alert.text
        alert.dismiss()
        logger.debug(f"Dismissed alert with text: '{text}'")
        return text

    def send_keys_and_accept(self, text_to_send: str, timeout: Optional[float] = None) -> str:
        """Wait for prompt dialog, send input keys, accept it, and return prompt message."""
        alert = self.wait_for_alert(timeout)
        original_text = alert.text
        alert.send_keys(text_to_send)
        alert.accept()
        logger.debug(f"Sent '{text_to_send}' to prompt dialog and accepted.")
        return original_text
