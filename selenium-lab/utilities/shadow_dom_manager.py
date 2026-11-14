"""
Shadow DOM Navigation Utility for BREL Selenium Lab.
Enables standard W3C ShadowRoot access, nested piercing, and shadow element synchronization.
"""

from __future__ import annotations

import logging
from typing import List, Optional

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait

from ..config.settings import settings

logger = logging.getLogger(__name__)


class ShadowDomManager:
    """Manages traversal and synchronization inside Shadow DOM subtrees."""

    def __init__(self, driver: WebDriver, default_timeout: Optional[float] = None) -> None:
        self.driver = driver
        self.timeout = default_timeout or settings.DEFAULT_TIMEOUT

    def get_shadow_root(self, host_locator: tuple[str, str], timeout: Optional[float] = None) -> WebElement:
        """Wait for host element and return its open ShadowRoot."""
        to = timeout or self.timeout
        wait = WebDriverWait(self.driver, timeout=to, poll_frequency=settings.POLL_FREQUENCY)

        def _get_root(d: WebDriver):
            try:
                host = d.find_element(*host_locator)
                return host.shadow_root
            except (NoSuchElementException, AttributeError):
                return False

        try:
            shadow_root = wait.until(_get_root)
            logger.debug(f"Retrieved shadow root for host: {host_locator}")
            return shadow_root  # type: ignore[return-value]
        except TimeoutException as e:
            raise TimeoutException(
                f"Timed out after {to}s attempting to access shadow_root on {host_locator}"
            ) from e

    def find_element_in_shadow(
        self,
        host_locator: tuple[str, str],
        css_selector: str,
        timeout: Optional[float] = None,
    ) -> WebElement:
        """Locate element inside the shadow root of host_locator using a CSS selector."""
        to = timeout or self.timeout
        wait = WebDriverWait(self.driver, timeout=to, poll_frequency=settings.POLL_FREQUENCY)

        def _find(d: WebDriver):
            try:
                host = d.find_element(*host_locator)
                shadow = host.shadow_root
                el = shadow.find_element(By.CSS_SELECTOR, css_selector)
                return el
            except (NoSuchElementException, AttributeError):
                return False

        try:
            return wait.until(_find)  # type: ignore[return-value]
        except TimeoutException as e:
            raise TimeoutException(
                f"Timed out waiting for '{css_selector}' inside shadow root of {host_locator}"
            ) from e

    def find_nested_shadow_element(
        self,
        host_locators_chain: List[tuple[str, str]],
        target_css: str,
        timeout: Optional[float] = None,
    ) -> WebElement:
        """Traverse a chain of nested shadow hosts down to the target element."""
        to = timeout or self.timeout
        wait = WebDriverWait(self.driver, timeout=to, poll_frequency=settings.POLL_FREQUENCY)

        def _traverse(d: WebDriver):
            try:
                current_context: WebElement = d.find_element(*host_locators_chain[0])
                for host_loc in host_locators_chain[1:]:
                    current_context = current_context.shadow_root.find_element(*host_loc)
                return current_context.shadow_root.find_element(By.CSS_SELECTOR, target_css)
            except (NoSuchElementException, AttributeError):
                return False

        try:
            return wait.until(_traverse)  # type: ignore[return-value]
        except TimeoutException as e:
            raise TimeoutException(
                f"Timed out traversing nested shadow chain {host_locators_chain} for '{target_css}'"
            ) from e
