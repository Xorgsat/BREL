"""
Failure Diagnostics Coordinator for BREL.
Generates an isolated, comprehensive diagnostic bundle whenever a test fails.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver

from .browser_logs import BrowserLogCollector
from .metadata_collector import MetadataCollector
from .screenshot_capture import ScreenshotCapture
from ..config.settings import settings

logger = logging.getLogger(__name__)


class FailureCollector:
    """Coordinates the collection of all failure evidence into an isolated directory."""

    @staticmethod
    def capture_failure_bundle(
        driver: WebDriver,
        test_node_id: str,
        exception: Optional[Exception] = None,
        base_dir: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """
        Produce a full failure diagnostic bundle:
        - screenshot.png
        - page_source.html
        - console_logs.json
        - metadata.json
        """
        # Clean node id for file system path
        safe_name = test_node_id.replace("::", "__").replace("/", "_").replace("\\", "_")
        target_dir = (base_dir or settings.ARTIFACTS_DIR) / "failures" / safe_name
        target_dir.mkdir(parents=True, exist_ok=True)

        bundle_manifest: Dict[str, Any] = {
            "test_id": test_node_id,
            "artifact_directory": str(target_dir),
            "artifacts": {},
        }

        # 1. Screenshot
        screenshot_path = ScreenshotCapture.capture(driver, target_dir, "screenshot.png")
        if screenshot_path:
            bundle_manifest["artifacts"]["screenshot"] = str(screenshot_path)

        # 2. Complete DOM Snapshot
        try:
            page_source = driver.page_source
            dom_path = target_dir / "page_source.html"
            with open(dom_path, "w", encoding="utf-8") as f:
                f.write(page_source)
            bundle_manifest["artifacts"]["page_source"] = str(dom_path)
        except WebDriverException as e:
            logger.warning(f"Could not capture page_source: {e}")

        # 3. Console Logs
        try:
            logs_path = BrowserLogCollector.save_console_logs(driver, target_dir, "console_logs.json")
            bundle_manifest["artifacts"]["console_logs"] = str(logs_path)
        except Exception as e:
            logger.warning(f"Could not persist console logs: {e}")

        # 4. Metadata Snapshot
        try:
            meta = MetadataCollector.collect(driver, test_node_id, exception)
            meta_path = MetadataCollector.save_metadata(meta, target_dir, "metadata.json")
            bundle_manifest["artifacts"]["metadata"] = str(meta_path)
            bundle_manifest["metadata"] = meta
        except Exception as e:
            logger.warning(f"Could not persist diagnostic metadata: {e}")

        logger.info(f"Captured failure diagnostic bundle in {target_dir}")
        return bundle_manifest
