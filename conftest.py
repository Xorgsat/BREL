"""
Root pytest configuration and fixture orchestration for BREL.
Provides lifecycle management, test isolation, and automated failure diagnostic capture.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from selenium_lab.config.settings import settings
from selenium_lab.drivers.driver_factory import DriverFactory
from selenium_lab.core.wait_manager import WaitManager
from selenium_lab.diagnostics.failure_collector import FailureCollector
from selenium_lab.utilities.frame_manager import FrameManager
from selenium_lab.utilities.window_manager import WindowManager
from selenium_lab.utilities.alert_manager import AlertManager
from selenium_lab.utilities.file_manager import FileManager
from selenium_lab.utilities.shadow_dom_manager import ShadowDomManager
from controlled_app.server import ControlledServerManager

logger = logging.getLogger(__name__)


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register custom CLI flags for pytest."""
    parser.addoption(
        "--browser",
        action="store",
        default=os.getenv("BROWSER", "chrome"),
        help="Target browser engine: chrome, firefox, edge",
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=None,
        help="Run browser in headless mode",
    )
    parser.addoption(
        "--headed",
        action="store_true",
        default=None,
        help="Run browser in visible headed mode",
    )
    parser.addoption(
        "--target-url",
        action="store",
        default=None,
        help="Override base target URL",
    )


import time
import requests


def pytest_sessionstart(session: pytest.Session) -> None:
    """Pre-start controlled app server on controller process before xdist workers fork."""
    if not hasattr(session.config, "workerinput"):
        try:
            server_mgr = ControlledServerManager(
                host=settings.CONTROLLED_APP_HOST,
                port=settings.CONTROLLED_APP_PORT,
            )
            server_mgr.start()
            session.config._brel_server_mgr = server_mgr
        except Exception as e:
            logger.warning(f"Could not pre-start controlled server in sessionstart: {e}")


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Stop controlled app server on controller node after all workers finish."""
    if not hasattr(session.config, "workerinput"):
        server_mgr = getattr(session.config, "_brel_server_mgr", None)
        if server_mgr:
            server_mgr.stop()


@pytest.fixture(scope="session")
def controlled_server():
    """
    Ensure controlled testbed server is healthy and return base URL.

    Strategy (ADR-006):
    - On the controller process, the server is started in pytest_sessionstart BEFORE
      workers fork, so it should already be healthy by the time this fixture runs.
    - On xdist worker processes (``workerinput`` is present), the server is a shared
      subprocess — workers just poll until it is healthy.
    - The retry window is intentionally generous (15 s) to cover worker startup races
      and slow CI environments.
    """
    base_url = f"http://{settings.CONTROLLED_APP_HOST}:{settings.CONTROLLED_APP_PORT}"

    # Extended retry with exponential back-off to handle worker-startup races.
    deadline = time.time() + 15.0
    sleep_interval = 0.1
    while time.time() < deadline:
        try:
            resp = requests.get(f"{base_url}/api/health", timeout=1.0)
            if resp.status_code == 200:
                logger.info("controlled_server fixture: server healthy at %s", base_url)
                break
        except Exception:
            pass
        time.sleep(sleep_interval)
        sleep_interval = min(sleep_interval * 1.5, 1.0)  # back-off, cap at 1 s
    else:
        # Last-resort self-start: this worker will own the server for its session.
        # ControlledServerManager.start() is idempotent — if the port is already open
        # it returns immediately without spawning a duplicate process.
        logger.warning(
            "controlled_server fixture: health check timed out after 15 s — "
            "attempting self-start fallback."
        )
        server_mgr = ControlledServerManager(
            host=settings.CONTROLLED_APP_HOST,
            port=settings.CONTROLLED_APP_PORT,
        )
        base_url = server_mgr.start()

    yield base_url


@pytest.fixture(scope="session")
def controlled_app_url(controlled_server: str) -> str:
    return controlled_server


@pytest.fixture(scope="session")
def internet_app_url() -> str:
    return settings.INTERNET_APP_URL


@pytest.fixture(scope="session")
def uitap_app_url() -> str:
    return settings.UITAP_APP_URL


@pytest.fixture(scope="function")
def isolated_download_dir(tmp_path: Path) -> Path:
    """Create isolated download directory per test to prevent race conditions (ADR-006)."""
    download_dir = tmp_path / "downloads"
    download_dir.mkdir(parents=True, exist_ok=True)
    return download_dir


@pytest.fixture(scope="function")
def driver(
    request: pytest.FixtureRequest,
    isolated_download_dir: Path,
) -> WebDriver:
    """
    Function-scoped WebDriver instance.
    Guarantees total browser session isolation per test method (ADR-006).
    """
    # Determine browser and headless flags
    cli_browser = request.config.getoption("--browser")
    cli_headless = request.config.getoption("--headless")
    cli_headed = request.config.getoption("--headed")

    if cli_headed:
        headless = False
    elif cli_headless:
        headless = True
    else:
        headless = settings.HEADLESS

    driver_instance = DriverFactory.create_driver(
        browser_name=cli_browser,
        headless=headless,
        download_dir=isolated_download_dir,
    )

    # Attach driver to request node for failure diagnostic hook
    request.node.driver = driver_instance

    yield driver_instance

    # Teardown: ensure complete browser process termination
    try:
        driver_instance.quit()
    except Exception as e:
        logger.warning(f"Error during driver.quit(): {e}")


@pytest.fixture(scope="function")
def wait(driver: WebDriver) -> WaitManager:
    """Provide explicit wait manager bound to the active driver."""
    return WaitManager(driver)


@pytest.fixture(scope="function")
def frame_mgr(driver: WebDriver) -> FrameManager:
    return FrameManager(driver)


@pytest.fixture(scope="function")
def window_mgr(driver: WebDriver) -> WindowManager:
    return WindowManager(driver)


@pytest.fixture(scope="function")
def alert_mgr(driver: WebDriver) -> AlertManager:
    return AlertManager(driver)


@pytest.fixture(scope="function")
def file_mgr() -> type[FileManager]:
    return FileManager


@pytest.fixture(scope="function")
def shadow_mgr(driver: WebDriver) -> ShadowDomManager:
    return ShadowDomManager(driver)


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """
    Auto-mark any test that depends on ``internet_app_url`` or ``uitap_app_url``
    as ``network_sensitive``.

    Rationale (ADR-006 / ADR-004):
      External public demo applications (Heroku, Azure) are susceptible to
      renderer-timeout crashes when multiple headless Chrome instances
      simultaneously hit the same remote host under parallel pytest-xdist
      workers.  Auto-marking at collection time keeps test modules free of
      boilerplate repetition and makes the CI split (parallel vs sequential)
      fully automatic.
    """
    external_fixture_names = {"internet_app_url", "uitap_app_url"}
    network_sensitive_mark = pytest.mark.network_sensitive
    for item in items:
        if hasattr(item, "fixturenames") and external_fixture_names.intersection(
            item.fixturenames
        ):
            item.add_marker(network_sensitive_mark, append=False)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    """
    Automated Failure Diagnostics Hook.
    Whenever a test fails during the execution phase ('call'), automatically captures:
    - Screenshot
    - DOM page_source HTML
    - Browser console logs
    - Full execution context metadata JSON
    """
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        driver_instance = getattr(item, "driver", None)
        if driver_instance:
            try:
                logger.info(f"Test failed: {item.nodeid}. Triggering failure diagnostic capture...")
                FailureCollector.capture_failure_bundle(
                    driver=driver_instance,
                    test_node_id=item.nodeid,
                    exception=call.excinfo.value if call.excinfo else None,
                )
            except Exception as diag_err:
                logger.error(f"Failed to capture diagnostic bundle for {item.nodeid}: {diag_err}")
