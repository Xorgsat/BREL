"""
Configuration and Environment Settings for Browser Reliability Engineering Lab (BREL).
Loads settings from environment variables with sensible production defaults.
"""

from __future__ import annotations

import os
from pathlib import Path
from pydantic import Field
# Base project directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings:
    """Central settings manager for BREL test infrastructure."""

    # Browser & WebDriver Configuration
    BROWSER: str = os.getenv("BROWSER", "chrome").lower()
    HEADLESS: bool = os.getenv("HEADLESS", "true").lower() in ("true", "1", "yes")
    DEFAULT_TIMEOUT: float = float(os.getenv("BROWSER_TIMEOUT", "15.0"))
    POLL_FREQUENCY: float = float(os.getenv("POLL_FREQUENCY", "0.25"))
    IMPLICIT_WAIT: float = float(os.getenv("IMPLICIT_WAIT", "0.0"))

    # Target Applications
    INTERNET_APP_URL: str = os.getenv("INTERNET_APP_URL", "https://the-internet.herokuapp.com").rstrip("/")
    UITAP_APP_URL: str = os.getenv("UITAP_APP_URL", "http://uitestingplayground.com").rstrip("/")
    CONTROLLED_APP_URL: str = os.getenv("CONTROLLED_APP_URL", "http://127.0.0.1:8000").rstrip("/")

    # Controlled Application Settings
    CONTROLLED_APP_HOST: str = os.getenv("CONTROLLED_APP_HOST", "127.0.0.1")
    CONTROLLED_APP_PORT: int = int(os.getenv("CONTROLLED_APP_PORT", "8000"))

    # File and Artifact Paths
    ARTIFACTS_DIR: Path = Path(os.getenv("ARTIFACTS_DIR", str(PROJECT_ROOT / "artifacts")))
    REPORTS_DIR: Path = Path(os.getenv("REPORTS_DIR", str(PROJECT_ROOT / "reports")))
    TEST_DATA_DIR: Path = Path(os.getenv("TEST_DATA_DIR", str(PROJECT_ROOT / "test-data" / "files")))

    # Reliability & Repeatability Settings
    DEFAULT_ITERATIONS: int = int(os.getenv("DEFAULT_ITERATIONS", "10"))
    RANDOM_SEED: int = int(os.getenv("RANDOM_SEED", "42"))
    MAX_PARALLEL_WORKERS: int = int(os.getenv("MAX_PARALLEL_WORKERS", "4"))

    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure runtime directories exist."""
        cls.ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        cls.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        cls.TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_directories()
