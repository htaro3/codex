"""Utilities for formatting and sending MCP messages."""

from __future__ import annotations

import json
import logging
import time
from typing import Optional

try:
    import requests
    from requests.exceptions import RequestException
except Exception:  # pragma: no cover - requests might not be installed in all environments
    requests = None  # type: ignore
    RequestException = Exception

logger = logging.getLogger(__name__)


def format_mcp_message(payload: dict) -> str:
    """Serialize a payload dictionary to a JSON string."""
    return json.dumps(payload)


def parse_mcp_message(message: str) -> dict:
    """Parse a JSON message string into a dictionary."""
    return json.loads(message)


def send_mcp_request(
    url: str,
    payload: dict,
    *,
    session: Optional["requests.Session"] = None,
    retries: int = 3,
    backoff: float = 1.0,
) -> "requests.Response":
    """Send an MCP payload to *url* using HTTP POST with retry logic."""
    if requests is None:
        raise RequestException("'requests' library is required to send network requests")

    s = session or requests.Session()
    data = format_mcp_message(payload)
    last_exc: Optional[Exception] = None

    try:
        for attempt in range(1, retries + 1):
            try:
                response = s.post(url, data=data, headers={"Content-Type": "application/json"})
                response.raise_for_status()
                return response
            except RequestException as exc:  # pragma: no cover - network dependent
                last_exc = exc
                logger.error("Request attempt %s failed: %s", attempt, exc)
                if attempt < retries:
                    time.sleep(backoff * attempt)
        assert last_exc is not None
        raise last_exc
    finally:
        if session is None:
            s.close()
