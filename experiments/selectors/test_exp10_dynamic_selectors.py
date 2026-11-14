"""
EXP-10: Dynamic Selectors and Locator Reliability Experiments.
Investigates locator brittleness under dynamic attribute mutation, generated IDs,
composite class attributes, and non-breaking space text pitfalls.
"""

from __future__ import annotations

import pytest
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver


@pytest.mark.experiment
def test_exp10_dynamic_id_brittleness_and_semantic_remedy(
    driver: WebDriver,
    uitap_app_url: str,
):
    """
    DYNAMIC ID LOCATOR ANALYSIS:
    On /dynamicid, button IDs are generated randomly on each page render.
    Demonstrates that relying on static IDs produces flaky/broken tests,
    while text-based semantic locators remain completely stable.
    """
    driver.get(f"{uitap_app_url}/dynamicid")

    # 1. Capture dynamic ID on initial render
    button = driver.find_element(By.XPATH, "//button[text()='Button with Dynamic ID']")
    initial_id = button.get_attribute("id")
    assert initial_id, "Button must have a dynamic ID"

    # 2. Reload page to trigger ID regeneration
    driver.refresh()

    # 3. Fragile locator: querying by the old ID fails
    with pytest.raises(NoSuchElementException):
        driver.find_element(By.ID, initial_id)

    # 4. Resilient locator: query by invariant user-facing text succeeds
    resilient_button = driver.find_element(By.XPATH, "//button[text()='Button with Dynamic ID']")
    new_id = resilient_button.get_attribute("id")
    assert new_id != initial_id, f"ID was expected to change: initial={initial_id}, new={new_id}"


@pytest.mark.experiment
def test_exp10_class_attribute_composite_matching(
    driver: WebDriver,
    uitap_app_url: str,
):
    """
    CLASS ATTRIBUTE SENSITIVITY:
    On /classattr, the primary button has multiple composite classes: 'btn class1 btn-primary btn-test'.
    Demonstrates exact class attribute equality failure vs robust class containment.
    """
    driver.get(f"{uitap_app_url}/classattr")

    # Exact string match fails if order or whitespace changes
    # Robust XPath using normalize-space contains
    robust_xpath = "//button[contains(concat(' ', normalize-space(@class), ' '), ' btn-primary ')]"
    button = driver.find_element(By.XPATH, robust_xpath)
    assert "btn-primary" in button.get_attribute("class")


@pytest.mark.experiment
def test_exp10_non_breaking_space_trap(
    driver: WebDriver,
    uitap_app_url: str,
):
    """
    NON-BREAKING SPACE PITFALL:
    On /nbsp, the button text contains &nbsp; (\\u00A0) instead of ASCII space (\\u0020).
    A standard XPath query matching "My Button" with regular ASCII space fails to find the element!
    """
    driver.get(f"{uitap_app_url}/nbsp")

    # 1. Standard text match with regular space fails to match \u00A0
    with pytest.raises(NoSuchElementException):
        driver.find_element(By.XPATH, "//button[text()='My Button']")

    # 2. Resilient XPath normalizing whitespace or matching unicode non-breaking space
    resilient_xpath = "//button[normalize-space(translate(text(), '\u00a0', ' ')) = 'My Button']"
    button = driver.find_element(By.XPATH, resilient_xpath)
    assert button.is_displayed()
