"""
Phase 1 Smoke Tests: Verification of Selenium Lab Foundation.
Tests browser lifecycle, WaitManager synchronization, target app connectivity,
and failure diagnostic artifact generation.
"""

from __future__ import annotations

from pathlib import Path
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from selenium_lab.core.wait_manager import WaitManager
from selenium_lab.diagnostics.failure_collector import FailureCollector


@pytest.mark.smoke
def test_driver_lifecycle_and_navigation(driver: WebDriver, controlled_app_url: str):
    """Verify clean browser initialization, navigation, and page title extraction."""
    driver.get(controlled_app_url)
    assert "BREL Controlled Testbed" in driver.title
    assert driver.session_id is not None


@pytest.mark.smoke
def test_explicit_wait_dynamic_render(driver: WebDriver, wait: WaitManager, controlled_app_url: str):
    """Verify WaitManager synchronization on asynchronously injected element."""
    driver.get(f"{controlled_app_url}/scenarios/dynamic-render?delay_ms=800")
    trigger_btn = driver.find_element(By.ID, "trigger-btn")
    trigger_btn.click()

    # Wait for dynamic target element to appear and be visible
    target = wait.wait_for_visibility((By.ID, "target-element"), timeout=5.0)
    assert target.is_displayed()
    assert target.text == "Target Loaded Successfully!"


@pytest.mark.smoke
def test_wait_manager_presence_vs_visibility(driver: WebDriver, wait: WaitManager, internet_app_url: str):
    """
    Verify distinction between DOM presence and visual display on The Internet Dynamic Loading.
    In Example 1, #finish element is present in DOM before start, but hidden (display: none).
    """
    driver.get(f"{internet_app_url}/dynamic_loading/1")

    # Before clicking start, element is present in DOM but NOT visible
    finish_locator = (By.CSS_SELECTOR, "#finish h4")
    hidden_element = wait.wait_for_presence(finish_locator, timeout=5.0)
    assert not hidden_element.is_displayed()

    # Trigger async loading
    start_btn = wait.wait_for_clickable((By.CSS_SELECTOR, "#start button"), timeout=5.0)
    start_btn.click()

    # Loading spinner appears then disappears
    wait.wait_for_invisibility((By.ID, "loading"), timeout=10.0)

    # Now wait for visibility
    visible_element = wait.wait_for_visibility(finish_locator, timeout=5.0)
    assert visible_element.is_displayed()
    assert visible_element.text == "Hello World!"


@pytest.mark.smoke
def test_ajax_delay_resolution(driver: WebDriver, wait: WaitManager, controlled_app_url: str):
    """Verify synchronization on text appearance under delayed execution."""
    driver.get(f"{controlled_app_url}/scenarios/dynamic-render?delay_ms=600")
    driver.find_element(By.ID, "trigger-btn").click()

    # Synchronize on text content appearing
    text_found = wait.wait_for_text_to_be_present(
        (By.ID, "target-element"),
        "Target Loaded Successfully!",
        timeout=5.0,
    )
    assert text_found is True


@pytest.mark.smoke
def test_diagnostic_failure_bundle_generation(driver: WebDriver, tmp_path: Path):
    """
    Verify that FailureCollector generates the complete artifact bundle:
    screenshot.png, page_source.html, console_logs.json, metadata.json.
    """
    driver.get("data:text/html,<html><head><title>Diagnostic Test</title></head><body><h1>Failure Specimen</h1></body></html>")
    test_node_id = "test_smoke_foundation::test_diagnostic_failure_bundle_generation"

    # Simulate failure collection directly to verify integrity
    bundle = FailureCollector.capture_failure_bundle(
        driver=driver,
        test_node_id=test_node_id,
        exception=AssertionError("Simulated Failure for Diagnostics Verification"),
        base_dir=tmp_path,
    )

    artifact_dir = Path(bundle["artifact_directory"])
    assert artifact_dir.exists(), "Failure artifact directory must be created"

    # Check for screenshot
    screenshot_file = artifact_dir / "screenshot.png"
    assert screenshot_file.exists(), "screenshot.png must be captured"
    assert screenshot_file.stat().st_size > 0, "screenshot.png must not be empty"

    # Check for DOM snapshot
    dom_file = artifact_dir / "page_source.html"
    assert dom_file.exists(), "page_source.html must be saved"
    dom_content = dom_file.read_text(encoding="utf-8")
    assert "Failure Specimen" in dom_content

    # Check for metadata
    meta_file = artifact_dir / "metadata.json"
    assert meta_file.exists(), "metadata.json must be generated"
    assert bundle["metadata"]["current_url"].startswith("data:text/html")
    assert bundle["metadata"]["page_title"] == "Diagnostic Test"
    assert bundle["metadata"]["exception"]["type"] == "AssertionError"
