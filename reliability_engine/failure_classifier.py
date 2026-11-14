"""
Failure Classification Taxonomy Module for BREL Reliability Engine.
Classifies exceptions and failure outcomes into 11 standardized categories per ADR-004.
"""

from __future__ import annotations

from enum import Enum
import re
from typing import Any, Dict, Optional


class FailureCategory(str, Enum):
    SYNCHRONIZATION = "Synchronization"
    LOCATOR = "Locator"
    DOM_LIFECYCLE = "DOM Lifecycle"
    ACTIONABILITY = "Actionability"
    NAVIGATION = "Navigation"
    NETWORK = "Network"
    BROWSER_CRASH = "Browser Crash"
    INFRASTRUCTURE = "Infrastructure"
    STATE_CONTAMINATION = "State Contamination"
    APPLICATION_DEFECT = "Application Defect"
    UNKNOWN = "Unknown"


class FailureClassifier:
    """Classifies exceptions, error messages, and stack traces into standardized categories."""

    @staticmethod
    def classify(
        exception_type: Optional[str] = None,
        error_message: Optional[str] = None,
        stacktrace: Optional[str] = None,
    ) -> FailureCategory:
        """Evaluate error indicators and return matching FailureCategory."""
        text_corpus = f"{exception_type or ''} {error_message or ''} {stacktrace or ''}".lower()

        if not text_corpus.strip():
            return FailureCategory.UNKNOWN

        # 1. DOM Lifecycle (Stale Element Pointers)
        if "staleelementreferenceexception" in text_corpus or "stale element reference" in text_corpus:
            return FailureCategory.DOM_LIFECYCLE

        # 2. Actionability (Interception, Obscuring, Unclickable)
        if (
            "elementclickinterceptedexception" in text_corpus
            or "click intercepted" in text_corpus
            or "other element would receive the click" in text_corpus
            or "elementnotinteractableexception" in text_corpus
        ):
            return FailureCategory.ACTIONABILITY

        # 3. Synchronization (Timeouts waiting for state)
        if "timeoutexception" in text_corpus or "timed out waiting for" in text_corpus:
            return FailureCategory.SYNCHRONIZATION

        # 4. Locator (Element Not Found)
        if "nosuchelementexception" in text_corpus or "unable to locate element" in text_corpus:
            return FailureCategory.LOCATOR

        # 5. Network Failures
        if (
            "connection refused" in text_corpus
            or "err_connection" in text_corpus
            or "injected network failure" in text_corpus
            or "502 bad gateway" in text_corpus
            or "504 gateway timeout" in text_corpus
        ):
            return FailureCategory.NETWORK

        # 6. Navigation Failures
        if "navigation" in text_corpus or "page load" in text_corpus:
            return FailureCategory.NAVIGATION

        # 7. Browser Crash
        if "session deleted because of a crash" in text_corpus or "browser closed" in text_corpus:
            return FailureCategory.BROWSER_CRASH

        # 8. Infrastructure
        if "driver startup" in text_corpus or "port already in use" in text_corpus or "chromedriver" in text_corpus and "cannot connect" in text_corpus:
            return FailureCategory.INFRASTRUCTURE

        # 9. Application Defect (Assertion Errors with product expectations)
        if "assertionerror" in text_corpus:
            return FailureCategory.APPLICATION_DEFECT

        return FailureCategory.UNKNOWN
