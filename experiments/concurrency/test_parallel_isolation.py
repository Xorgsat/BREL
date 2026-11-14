"""
Concurrency and Parallel Execution Isolation Experiments.
Validates ADR-006: Total session isolation across parallel pytest-xdist workers.
Ensures zero cookie leakage, storage contamination, or download collision.
"""

from __future__ import annotations

from pathlib import Path
import time
import uuid
import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from selenium_lab.utilities.file_manager import FileManager


@pytest.mark.experiment
def test_parallel_worker_storage_isolation(
    driver: WebDriver,
    controlled_app_url: str,
):
    """
    PARALLEL STORAGE ISOLATION:
    Generates a unique worker token, writes it to localStorage,
    and asserts that concurrent workers running in parallel never observe foreign tokens.
    """
    worker_uuid = str(uuid.uuid4())
    driver.get(controlled_app_url)

    # Set worker-specific token
    driver.execute_script(f"localStorage.setItem('brel_worker_token', '{worker_uuid}');")

    # Deliberate sleep to simulate long-running concurrent work
    time.sleep(0.5)

    # Retrieve and assert identity
    stored_token = driver.execute_script("return localStorage.getItem('brel_worker_token');")
    assert stored_token == worker_uuid, f"Storage contamination detected: expected {worker_uuid}, got {stored_token}"


@pytest.mark.experiment
def test_parallel_worker_cookie_isolation(
    driver: WebDriver,
    controlled_app_url: str,
):
    """
    PARALLEL COOKIE ISOLATION:
    Injects a UUID-tagged cookie and verifies zero cookie leakage across workers.
    """
    worker_uuid = str(uuid.uuid4())
    driver.get(controlled_app_url)

    cookie = {"name": "worker_session_id", "value": worker_uuid, "path": "/"}
    driver.add_cookie(cookie)

    time.sleep(0.5)

    retrieved = driver.get_cookie("worker_session_id")
    assert retrieved is not None
    assert retrieved["value"] == worker_uuid


@pytest.mark.experiment
def test_parallel_worker_file_download_collision_immunity(
    driver: WebDriver,
    isolated_download_dir: Path,
    controlled_app_url: str,
):
    """
    DOWNLOAD COLLISION IMMUNITY:
    Multiple parallel workers download a file with the identical filename 'concurrent_specimen.txt'.
    ADR-006 mandates ephemeral worker directories, guaranteeing zero file overwrite collisions.
    """
    target_filename = "concurrent_specimen.txt"
    driver.get(f"{controlled_app_url}/scenarios/download-file?filename={target_filename}")

    downloaded = FileManager.wait_for_download(
        directory=isolated_download_dir,
        filename_pattern=f"*{target_filename}*",
        timeout=10.0,
    )

    assert downloaded.exists()
    assert downloaded.parent == isolated_download_dir
    assert downloaded.stat().st_size > 0
