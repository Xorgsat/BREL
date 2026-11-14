"""
File System & Download Management Utility for BREL Selenium Lab.
Orchestrates sample test file creation, file upload dispatch,
and robust verification of asynchronous browser downloads.
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
import time
from typing import Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from ..config.settings import settings

logger = logging.getLogger(__name__)


class FileManager:
    """Manages file uploads, download completion tracking, and artifact verification."""

    @staticmethod
    def create_sample_file(
        directory: Path,
        filename: str = "sample_test_file.txt",
        content: str = "BREL test fixture payload\n",
    ) -> Path:
        """Create a deterministic sample text file for upload testing."""
        directory.mkdir(parents=True, exist_ok=True)
        file_path = directory / filename
        file_path.write_text(content, encoding="utf-8")
        return file_path

    @staticmethod
    def upload_file(
        driver: WebDriver,
        file_input_locator: tuple[str, str],
        file_path: Path,
    ) -> WebElement:
        """Send absolute file path directly to the input element."""
        if not file_path.exists():
            raise FileNotFoundError(f"Upload source file not found: {file_path}")
        input_el = driver.find_element(*file_input_locator)
        input_el.send_keys(str(file_path.resolve()))
        logger.debug(f"Dispatched file path to input element: {file_path}")
        return input_el

    @staticmethod
    def wait_for_download(
        directory: Path,
        filename_pattern: Optional[str] = None,
        timeout: float = 15.0,
        poll_interval: float = 0.25,
    ) -> Path:
        """
        Poll download directory until a file finishes downloading.
        Rejects partial files ending with .crdownload, .tmp, or .part.
        """
        start_time = time.time()
        logger.debug(f"Waiting for download completion in {directory}")

        while time.time() - start_time < timeout:
            if directory.exists():
                candidates = list(directory.glob(filename_pattern or "*"))
                # Filter out temporary download files
                completed = [
                    f for f in candidates
                    if f.is_file() and not f.name.endswith((".crdownload", ".tmp", ".part"))
                ]
                if completed:
                    # Return the most recently modified completed file
                    target = max(completed, key=lambda f: f.stat().st_mtime)
                    # Verify non-zero size
                    if target.stat().st_size > 0:
                        logger.info(f"Verified downloaded file: {target} ({target.stat().st_size} bytes)")
                        return target

            time.sleep(poll_interval)

        raise TimeoutError(
            f"Download did not complete in {directory} within {timeout}s. Files present: {list(directory.iterdir()) if directory.exists() else 'Dir does not exist'}"
        )

    @staticmethod
    def compute_sha256(file_path: Path) -> str:
        """Compute SHA256 checksum of a file for integrity verification."""
        sha = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha.update(chunk)
        return sha.hexdigest()
