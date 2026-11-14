"""
Controlled Application Server Runner.
Provides programmatic start/stop for the FastAPI controlled testbed.
"""

from __future__ import annotations

import logging
import socket
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
        self.server: Optional[uvicorn.Server] = None
        self.thread: Optional[threading.Thread] = None

    def start(self, timeout: float = 5.0) -> str:
        base_url = f"http://{self.host}:{self.port}"
        # Check if already running
        if is_port_in_use(self.host, self.port):
            try:
                resp = requests.get(f"{base_url}/api/health", timeout=1.0)
                if resp.status_code == 200:
                    logger.info(f"Controlled testbed already active on {base_url}")
                    return base_url
            except Exception:
                pass

        logger.info(f"Starting controlled testbed server on {base_url}...")
        config = uvicorn.Config(
            "controlled_app.app.main:app",
            host=self.host,
            port=self.port,
            log_level="warning",
        )
        self.server = uvicorn.Server(config)
        self.thread = threading.Thread(target=self.server.run, daemon=True)
        self.thread.start()

        # Wait for healthcheck
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                resp = requests.get(f"{base_url}/api/health", timeout=0.5)
                if resp.status_code == 200:
                    logger.info("Controlled testbed server is healthy and responding.")
                    return base_url
            except Exception:
                time.sleep(0.1)

        raise TimeoutError(f"Failed to start controlled testbed on {base_url} within {timeout}s")

    def stop(self) -> None:
        if self.server:
            logger.info("Stopping controlled testbed server...")
            self.server.should_exit = True
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=2.0)
            self.server = None
            self.thread = None
            logger.info("Controlled testbed server stopped.")
