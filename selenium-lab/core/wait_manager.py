"""
Explicit Synchronization Module for Browser Reliability Engineering Lab.
Implements fine-grained state-based waiting conditions over WebDriverWait.
Enforces ADR-002: Zero arbitrary sleeps, zero implicit waits.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Callable, List, Optional, Tuple, Union

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ..config.settings import settings

logger = logging.getLogger(__name__)

LocatorType = Tuple[str, str]


class WaitManager:
    """Central explicit synchronization manager for Selenium WebDriver."""

    def __init__(
        self,
        driver: WebDriver,
        default_timeout: Optional[float] = None,
        poll_frequency: Optional[float] = None,
    ) -> None:
        self.driver = driver
        self.default_timeout = default_timeout or settings.DEFAULT_TIMEOUT
        self.poll_frequency = poll_frequency or settings.POLL_FREQUENCY

    def _get_wait(
        self,
        timeout: Optional[float] = None,
        ignored_exceptions: Optional[List[type[Exception]]] = None,
    ) -> WebDriverWait:
        to = timeout if timeout is not None else self.default_timeout
        exceptions = ignored_exceptions or [NoSuchElementException, StaleElementReferenceException]
        return WebDriverWait(
            self.driver,
            timeout=to,
            poll_frequency=self.poll_frequency,
            ignored_exceptions=exceptions,
        )

    # -------------------------------------------------------------------------
    # DOM Presence and Visibility
    # -------------------------------------------------------------------------

    def wait_for_presence(self, locator: LocatorType, timeout: Optional[float] = None) -> WebElement:
        """Wait until element is present in the DOM (may not be visible)."""
        logger.debug(f"Waiting for presence of {locator}")
        wait = self._get_wait(timeout)
        try:
            return wait.until(EC.presence_of_element_located(locator))
        except TimeoutException as e:
            raise TimeoutException(
                f"Timed out after {wait._timeout}s waiting for presence of locator: {locator}"
            ) from e

    def wait_for_visibility(self, locator: LocatorType, timeout: Optional[float] = None) -> WebElement:
        """Wait until element is both present in the DOM and visible (height & width > 0)."""
        logger.debug(f"Waiting for visibility of {locator}")
        wait = self._get_wait(timeout)
        try:
            return wait.until(EC.visibility_of_element_located(locator))
        except TimeoutException as e:
            raise TimeoutException(
                f"Timed out after {wait._timeout}s waiting for visibility of locator: {locator}"
            ) from e

    def wait_for_invisibility(self, locator: LocatorType, timeout: Optional[float] = None) -> bool:
        """Wait until element is either invisible or completely removed from the DOM."""
        logger.debug(f"Waiting for invisibility of {locator}")
        wait = self._get_wait(timeout)
        try:
            return bool(wait.until(EC.invisibility_of_element_located(locator)))
        except TimeoutException as e:
            raise TimeoutException(
                f"Timed out after {wait._timeout}s waiting for invisibility of locator: {locator}"
            ) from e

    def wait_for_clickable(self, locator: LocatorType, timeout: Optional[float] = None) -> WebElement:
        """Wait until element is both visible and enabled for user interaction."""
        logger.debug(f"Waiting for clickability of {locator}")
        wait = self._get_wait(timeout)
        try:
            return wait.until(EC.element_to_be_clickable(locator))
        except TimeoutException as e:
            raise TimeoutException(
                f"Timed out after {wait._timeout}s waiting for clickability of locator: {locator}"
            ) from e

    # -------------------------------------------------------------------------
    # DOM Lifecycle and Staleness
    # -------------------------------------------------------------------------

    def wait_for_staleness(self, element: WebElement, timeout: Optional[float] = None) -> bool:
        """Wait until the specified WebElement reference becomes detached/stale."""
        logger.debug("Waiting for element reference staleness")
        wait = self._get_wait(timeout, ignored_exceptions=[])
        try:
            return bool(wait.until(EC.staleness_of(element)))
        except TimeoutException as e:
            raise TimeoutException(
                f"Timed out after {wait._timeout}s waiting for element to become stale."
            ) from e

    # -------------------------------------------------------------------------
    # Text and Attribute Synchronization
    # -------------------------------------------------------------------------

    def wait_for_text_to_be_present(
        self,
        locator: LocatorType,
        text: str,
        timeout: Optional[float] = None,
    ) -> bool:
        """Wait until the exact or substring text appears within the target element."""
        logger.debug(f"Waiting for text '{text}' in {locator}")
        wait = self._get_wait(timeout)
        try:
            return bool(wait.until(EC.text_to_be_present_in_element(locator, text)))
        except TimeoutException as e:
            raise TimeoutException(
                f"Timed out after {wait._timeout}s waiting for text '{text}' in locator: {locator}"
            ) from e

    def wait_for_text_to_change(
        self,
        locator: LocatorType,
        initial_text: str,
        timeout: Optional[float] = None,
    ) -> str:
        """Wait until the element text changes from initial_text and returns the new text."""
        logger.debug(f"Waiting for text to change from '{initial_text}' on {locator}")
        wait = self._get_wait(timeout)

        def _condition(driver: WebDriver) -> Union[str, bool]:
            try:
                el = driver.find_element(*locator)
                current_text = el.text
                if current_text != initial_text:
                    return current_text
                return False
            except (NoSuchElementException, StaleElementReferenceException):
                return False

        try:
            result = wait.until(_condition)
            return str(result)
        except TimeoutException as e:
            raise TimeoutException(
                f"Timed out after {wait._timeout}s waiting for text on {locator} to change from '{initial_text}'"
            ) from e

    def wait_for_attribute_to_be(
        self,
        locator: LocatorType,
        attribute: str,
        value: str,
        timeout: Optional[float] = None,
    ) -> bool:
        """Wait until an element attribute matches the exact specified value."""
        wait = self._get_wait(timeout)
        try:
            return bool(wait.until(EC.text_to_be_present_in_element_attribute(locator, attribute, value)))
        except TimeoutException as e:
            raise TimeoutException(
                f"Timed out after {wait._timeout}s waiting for attribute '{attribute}' to equal '{value}' on {locator}"
            ) from e

    # -------------------------------------------------------------------------
    # Collection Count Synchronization
    # -------------------------------------------------------------------------

    def wait_for_element_count_to_be(
        self,
        locator: LocatorType,
        expected_count: int,
        timeout: Optional[float] = None,
    ) -> List[WebElement]:
        """Wait until exactly expected_count elements are present in the DOM."""
        wait = self._get_wait(timeout)

        def _condition(driver: WebDriver) -> Union[List[WebElement], bool]:
            elements = driver.find_elements(*locator)
            if len(elements) == expected_count:
                return elements
            return False

        try:
            return wait.until(_condition)  # type: ignore[return-value]
        except TimeoutException as e:
            current_elements = self.driver.find_elements(*locator)
            raise TimeoutException(
                f"Timed out waiting for count of {locator} to be {expected_count}. Current count: {len(current_elements)}"
            ) from e

    def wait_for_element_count_greater_than(
        self,
        locator: LocatorType,
        count_threshold: int,
        timeout: Optional[float] = None,
    ) -> List[WebElement]:
        """Wait until more than count_threshold elements are present in the DOM."""
        wait = self._get_wait(timeout)

        def _condition(driver: WebDriver) -> Union[List[WebElement], bool]:
            elements = driver.find_elements(*locator)
            if len(elements) > count_threshold:
                return elements
            return False

        try:
            return wait.until(_condition)  # type: ignore[return-value]
        except TimeoutException as e:
            current_elements = self.driver.find_elements(*locator)
            raise TimeoutException(
                f"Timed out waiting for count of {locator} > {count_threshold}. Current count: {len(current_elements)}"
            ) from e

    # -------------------------------------------------------------------------
    # Navigation & URL Synchronization
    # -------------------------------------------------------------------------

    def wait_for_url_to_contain(self, url_fragment: str, timeout: Optional[float] = None) -> bool:
        """Wait until the browser URL contains the expected fragment."""
        wait = self._get_wait(timeout)
        try:
            return bool(wait.until(EC.url_contains(url_fragment)))
        except TimeoutException as e:
            raise TimeoutException(
                f"Timed out waiting for URL to contain '{url_fragment}'. Current URL: {self.driver.current_url}"
            ) from e

    def wait_for_url_to_be(self, expected_url: str, timeout: Optional[float] = None) -> bool:
        """Wait until current URL equals expected_url."""
        wait = self._get_wait(timeout)
        try:
            return bool(wait.until(EC.url_to_be(expected_url)))
        except TimeoutException as e:
            raise TimeoutException(
                f"Timed out waiting for URL to be '{expected_url}'. Current URL: {self.driver.current_url}"
            ) from e

    # -------------------------------------------------------------------------
    # Custom Condition and JavaScript Predicates
    # -------------------------------------------------------------------------

    def wait_for_javascript_condition(
        self,
        script: str,
        timeout: Optional[float] = None,
    ) -> Any:
        """Wait until a custom JavaScript expression evaluates to truthy."""
        wait = self._get_wait(timeout)

        def _condition(driver: WebDriver) -> Any:
            try:
                res = driver.execute_script(script)
                return res if res else False
            except WebDriverException:
                return False

        try:
            return wait.until(_condition)
        except TimeoutException as e:
            raise TimeoutException(f"Timed out waiting for JavaScript condition: '{script}'") from e

    def wait_for_custom_condition(
        self,
        predicate: Callable[[WebDriver], Any],
        timeout: Optional[float] = None,
        description: str = "custom condition",
    ) -> Any:
        """Wait until a user-provided predicate function returns truthy."""
        wait = self._get_wait(timeout)
        try:
            return wait.until(predicate)
        except TimeoutException as e:
            raise TimeoutException(f"Timed out waiting for {description}") from e
