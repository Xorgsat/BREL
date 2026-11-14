"""
EXP-09: File Upload and Download Verification Experiments.
Investigates file system boundaries, direct input interactions, download completion tracking,
and file hash integrity verification.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from selenium_lab.utilities.file_manager import FileManager
from selenium_lab.core.wait_manager import WaitManager


@pytest.mark.experiment
def test_exp09_file_upload_verification(
    driver: WebDriver,
    wait: WaitManager,
    tmp_path: Path,
    internet_app_url: str,
):
    """
    FILE UPLOAD VERIFICATION:
    Creates an isolated specimen file, dispatches path to input#file-upload,
    submits form, and verifies server confirms file receipt.
    """
    driver.get(f"{internet_app_url}/upload")

    # Create temporary file
    test_file = FileManager.create_sample_file(
        directory=tmp_path,
        filename="brel_upload_test.txt",
        content="Automated Browser Reliability Lab Upload Specimen\n",
    )

    # Dispatch to input element directly (no OS dialog interaction needed)
    FileManager.upload_file(driver, (By.ID, "file-upload"), test_file)

    # Submit
    driver.find_element(By.ID, "file-submit").click()

    # Validate upload result page
    heading = wait.wait_for_visibility((By.TAG_NAME, "h3"), timeout=5.0)
    assert heading.text == "File Uploaded!"

    uploaded_filename = driver.find_element(By.ID, "uploaded-files").text.strip()
    assert uploaded_filename == "brel_upload_test.txt"


@pytest.mark.experiment
def test_exp09_file_download_and_integrity_check(
    driver: WebDriver,
    isolated_download_dir: Path,
    controlled_app_url: str,
):
    """
    FILE DOWNLOAD INTEGRITY VERIFICATION:
    Triggers attachment download, polls isolated download directory until
    temporary download files resolve, and verifies SHA256 checksum against expected payload.
    """
    target_filename = "brel_integrity_specimen.txt"
    expected_content = f"BREL Download Verification Test Payload - Filename: {target_filename}\n"
    expected_hash = hashlib.sha256(expected_content.encode("utf-8")).hexdigest()

    # Navigate to trigger endpoint
    driver.get(f"{controlled_app_url}/scenarios/download-file?filename={target_filename}")

    # Wait for file download to complete in the isolated directory
    downloaded_path = FileManager.wait_for_download(
        directory=isolated_download_dir,
        filename_pattern=f"*{target_filename}*",
        timeout=10.0,
    )

    assert downloaded_path.exists()
    assert downloaded_path.stat().st_size > 0

    # Verify SHA256 integrity
    actual_hash = FileManager.compute_sha256(downloaded_path)
    assert actual_hash == expected_hash, f"Hash mismatch: expected {expected_hash}, got {actual_hash}"
