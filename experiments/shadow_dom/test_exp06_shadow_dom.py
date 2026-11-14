"""
EXP-06: Shadow DOM Encapsulation and Piercing Experiments.
Investigates Web Component encapsulation barriers, documents standard W3C
shadow_root access, and contrasts CSS shadow traversal with traditional XPath limitations.
"""

from __future__ import annotations

import pytest
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from selenium_lab.utilities.shadow_dom_manager import ShadowDomManager


@pytest.mark.experiment
def test_exp06_direct_lookup_fails_across_shadow_boundary(
    driver: WebDriver,
    controlled_app_url: str,
):
    """
    FAILURE MODE DEMONSTRATION:
    Elements encapsulated inside an open shadow root cannot be selected via standard
    document-level find_element queries or XPath expressions.
    """
    driver.get(f"{controlled_app_url}/scenarios/shadow-dom")

    # Host element is present in main DOM
    host = driver.find_element(By.ID, "shadow-host")
    assert host is not None

    # Internal shadow node #shadow-content cannot be found from document root
    with pytest.raises(NoSuchElementException):
        driver.find_element(By.ID, "shadow-content")

    # XPath cannot pierce shadow boundaries per W3C specification
    with pytest.raises(NoSuchElementException):
        driver.find_element(By.XPATH, "//p[@id='shadow-content']")


@pytest.mark.experiment
def test_exp06_w3c_shadow_root_traversal(
    driver: WebDriver,
    shadow_mgr: ShadowDomManager,
    controlled_app_url: str,
):
    """
    RELIABILITY REMEDIATION:
    Uses W3C standard host.shadow_root property to locate and assert elements
    inside the encapsulated shadow tree.
    """
    driver.get(f"{controlled_app_url}/scenarios/shadow-dom")

    shadow_text_el = shadow_mgr.find_element_in_shadow(
        host_locator=(By.ID, "shadow-host"),
        css_selector="#shadow-content",
        timeout=5.0,
    )
    assert shadow_text_el.text == "Inside Open Shadow Root"

    shadow_btn = shadow_mgr.find_element_in_shadow(
        host_locator=(By.ID, "shadow-host"),
        css_selector="#shadow-btn",
        timeout=5.0,
    )
    assert shadow_btn.is_displayed()
    assert shadow_btn.text == "Shadow Action"


@pytest.mark.experiment
def test_exp06_uitap_shadow_dom_guid_generator(
    driver: WebDriver,
    shadow_mgr: ShadowDomManager,
    uitap_app_url: str,
):
    """
    PUBLIC BENCHMARK (UITAP):
    On /shadowdom, tests accessing the shadow host <guid-generator>
    and interacting with its shadow elements: button#buttonGenerate and input#editField.
    """
    driver.get(f"{uitap_app_url}/shadowdom")

    # Locate shadow host element
    host_locator = (By.TAG_NAME, "guid-generator")

    # Find the generate button inside shadow root
    generate_btn = shadow_mgr.find_element_in_shadow(
        host_locator=host_locator,
        css_selector="#buttonGenerate",
        timeout=5.0,
    )
    assert generate_btn.is_displayed()
    generate_btn.click()

    # Find the edit field containing the generated GUID
    edit_field = shadow_mgr.find_element_in_shadow(
        host_locator=host_locator,
        css_selector="#editField",
        timeout=5.0,
    )
    guid_value = edit_field.get_attribute("value")
    assert guid_value is not None and len(guid_value) > 10, f"Expected valid GUID, got: {guid_value}"
