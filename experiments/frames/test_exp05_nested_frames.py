"""
EXP-05: Frames and Nested Frames Context Switching Experiments.
Investigates browser context isolation between parent document and nested framesets,
demonstrating context lookup failures, frame switching, and hierarchical traversal.
"""

from __future__ import annotations

import pytest
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from selenium_lab.utilities.frame_manager import FrameManager
from selenium_lab.core.wait_manager import WaitManager


@pytest.mark.experiment
def test_exp05_direct_lookup_fails_without_frame_switch(
    driver: WebDriver,
    controlled_app_url: str,
):
    """
    FAILURE MODE DEMONSTRATION:
    Attempting to find an element located inside an iframe from the default document context
    must deterministically fail with NoSuchElementException.
    """
    driver.get(f"{controlled_app_url}/scenarios/frames")

    # The element #frame-heading exists inside the child frame, NOT in the top document
    with pytest.raises(NoSuchElementException):
        driver.find_element(By.ID, "frame-heading")


@pytest.mark.experiment
def test_exp05_frame_switch_and_interaction(
    driver: WebDriver,
    frame_mgr: FrameManager,
    wait: WaitManager,
    controlled_app_url: str,
):
    """
    RELIABILITY REMEDIATION:
    1. Switch browsing context into the child iframe.
    2. Interact with element inside frame.
    3. Return to top document (default content).
    """
    driver.get(f"{controlled_app_url}/scenarios/frames")

    # Switch into frame
    frame_mgr.switch_to_frame("child-frame")

    heading = wait.wait_for_visibility((By.ID, "frame-heading"), timeout=5.0)
    assert heading.text == "Inside Child Frame Document"

    action_btn = driver.find_element(By.ID, "frame-action-btn")
    action_btn.click()
    assert action_btn.text == "Clicked in Frame"

    # Switch back to default content
    frame_mgr.switch_to_default_content()

    # In top document, the frame itself is present, but heading is inaccessible
    assert driver.find_element(By.ID, "child-frame").is_displayed()
    with pytest.raises(NoSuchElementException):
        driver.find_element(By.ID, "frame-heading")


@pytest.mark.experiment
def test_exp05_nested_frameset_hierarchical_traversal(
    driver: WebDriver,
    frame_mgr: FrameManager,
    internet_app_url: str,
):
    """
    COMPLEX HIERARCHY BENCHMARK:
    The Internet /nested_frames contains:
    - frame-top
        - frame-left
        - frame-middle
        - frame-right
    - frame-bottom
    Tests full context navigation across multiple hierarchy levels.
    """
    driver.get(f"{internet_app_url}/nested_frames")

    # 1. Traverse into frame-top -> frame-left
    frame_mgr.switch_to_frame("frame-top")
    frame_mgr.switch_to_frame("frame-left")
    body_left = driver.find_element(By.TAG_NAME, "body").text.strip()
    assert body_left == "LEFT"

    # 2. Return to parent frame (frame-top) -> switch to frame-middle
    frame_mgr.switch_to_parent_frame()
    frame_mgr.switch_to_frame("frame-middle")
    content_middle = driver.find_element(By.ID, "content").text.strip()
    assert content_middle == "MIDDLE"

    # 3. Return to parent frame -> switch to frame-right
    frame_mgr.switch_to_parent_frame()
    frame_mgr.switch_to_frame("frame-right")
    body_right = driver.find_element(By.TAG_NAME, "body").text.strip()
    assert body_right == "RIGHT"

    # 4. Return to default content -> switch to frame-bottom
    frame_mgr.switch_to_default_content()
    frame_mgr.switch_to_frame("frame-bottom")
    body_bottom = driver.find_element(By.TAG_NAME, "body").text.strip()
    assert body_bottom == "BOTTOM"

    # 5. Restore default content
    frame_mgr.switch_to_default_content()
