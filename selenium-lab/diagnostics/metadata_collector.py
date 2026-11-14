"""
Diagnostic Metadata Collector for BREL Selenium Lab.
Harvests comprehensive browser runtime state: URL, window handles, user agent,
capabilities, and system environment.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import platform
from typing import Any, Dict

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver

logger = logging.getLogger(__name__)


class MetadataCollector:
    """Collects runtime execution metadata from the active WebDriver session."""

    @staticmethod
    def collect(driver: WebDriver, test_id: str, exception: Exception | None = None) -> Dict[str, Any]:
        """Harvest complete runtime snapshot."""
        metadata: Dict[str, Any] = {
            "test_id": test_id,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "machine": platform.machine(),
                "python_version": platform.python_version(),
            },
        }

        try:
            metadata["current_url"] = driver.current_url
            metadata["page_title"] = driver.title
            metadata["current_window_handle"] = driver.current_window_handle
            metadata["all_window_handles"] = driver.window_handles
            metadata["window_count"] = len(driver.window_handles)
            metadata["capabilities"] = driver.capabilities
            metadata["session_id"] = driver.session_id
        except WebDriverException as e:
            metadata["driver_telemetry_error"] = str(e)

        if exception:
            metadata["exception"] = {
                "type": type(exception).__name__,
                "message": str(exception),
            }

        return metadata

    @staticmethod
    def save_metadata(
        metadata: Dict[str, Any],
        destination_dir: Path,
        filename: str = "metadata.json",
    ) -> Path:
        """Persist metadata dictionary to JSON artifact."""
        destination_dir.mkdir(parents=True, exist_ok=True)
        file_path = destination_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        return file_path
