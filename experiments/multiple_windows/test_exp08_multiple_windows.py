"""
EXP-08: Multiple Windows and Context Switching Experiments.
Investigates browser window handle propagation delays, context switching to new tabs,
child tab lifecycle termination, and parent context restoration.
"""

from __future__ import annotations

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from selenium_lab.utilities.window_manager import WindowManager
from selenium_lab.core.wait_manager import WaitManager


@pytest.mark.experiment
def test_exp08_window_handle_detection_and_switching(
    driver: WebDriver,
    window_mgr: WindowManager,
    wait: WaitManager,
    internet_app_url: str,
):
    """
    WINDOW HANDLE SYNCHRONIZATION:
    Navigates to /windows, clicks link with target='_blank', synchronizes on the
    creation of the secondary window handle, switches context, validates content,
    closes secondary window, and restores focus to parent handle.
    """
    driver.get(f"{internet_app_url}/windows")
    parent_handle = window_mgr.get_current_handle()
    initial_handles = set(window_mgr.get_all_handles())
    assert len(initial_handles) == 1

    # Click link to open new tab
    driver.find_element(By.LINK_TEXT, "Click Here").click()

    # Synchronize on new window handle appearance
    child_handle = window_mgr.switch_to_new_window(initial_handles, timeout=5.0)
    assert child_handle != parent_handle

    # In child window context
    new_window_heading = wait.wait_for_visibility((By.TAG_NAME, "h3"), timeout=5.0)
    assert new_window_heading.text == "New Window"

    # Close child window and restore context to parent
    window_mgr.close_current_and_switch_back(parent_handle)

    # Verify focus returned to parent
    assert window_mgr.get_current_handle() == parent_handle
    assert "Opening a new window" in driver.page_source
    assert len(window_mgr.get_all_handles()) == 1
