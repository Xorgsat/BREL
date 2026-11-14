"""
Controlled Application Server Runner.
Provides programmatic start/stop for the FastAPI controlled testbed.
"""

from __future__ import annotations

import logging
import socket
import subprocess
import sys
import threading
import time
from typing import Optional

import requests
import uvicorn

logger = logging.getLogger(__name__)


def is_port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


class ControlledServerManager:
    """Manages the lifecycle of the local FastAPI controlled testbed."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8000):
        self.host = host
        self.port = port
        self.proc: Optional[subprocess.Popen] = None
        self.server: Optional[uvicorn.Server] = None
        self.thread: Optional[threading.Thread] = None

    def start(self, timeout: float = 6.0) -> str:
        base_url = f"http://{self.host}:{self.port}"

        # If server is already running and healthy, reuse it immediately
        try:
            resp = requests.get(f"{base_url}/api/health", timeout=0.5)
            if resp.status_code == 200:
                logger.info(f"Controlled testbed already active on {base_url}")
                return base_url
        except Exception:
            pass

        # Launch via subprocess so it runs independently across pytest-xdist worker processes
        logger.info(f"Starting controlled testbed server on {base_url} via subprocess...")
        try:
            self.proc = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "uvicorn",
                    "controlled_app.app.main:app",
                    "--host",
                    self.host,
                    "--port",
                    str(self.port),
                    "--log-level",
                    "warning",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception as e:
            logger.warning(f"Could not launch uvicorn subprocess: {e}")

        # Wait for healthcheck to respond
        start_wait = time.time()
        while time.time() - start_wait < timeout:
            try:
                resp = requests.get(f"{base_url}/api/health", timeout=0.5)
                if resp.status_code == 200:
                    logger.info("Controlled testbed server is healthy and responding.")
                    return base_url
            except Exception:
                time.sleep(0.1)

        raise TimeoutError(f"Failed to start controlled testbed on {base_url} within {timeout}s")

    def stop(self) -> None:
        if self.proc:
            logger.info("Stopping controlled testbed server subprocess...")
            try:
                self.proc.terminate()
                self.proc.wait(timeout=2.0)
            except Exception:
                try:
                    self.proc.kill()
                except Exception:
                    pass
            self.proc = None

        if self.server:
            logger.info("Stopping controlled testbed server...")
            self.server.should_exit = True
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=2.0)
            self.server = None
            self.thread = None
            logger.info("Controlled testbed server stopped.")
