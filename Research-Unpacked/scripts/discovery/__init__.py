"""Stage 2A discovery ingestion: PubMed + Crossref, discovery only.

Nothing in this package assigns verification_status GREEN or produces
scientific/YouTube scores. Every record it emits is YELLOW,
ranking_eligible=False, with null scoring fields, per
config/verification_rules.md and config/scoring_rules.md (both locked and
untouched by this stage).
"""
from __future__ import annotations

import datetime as _dt
import time
import urllib.error
from dataclasses import dataclass
from typing import Callable, Optional, TypeVar


class DiscoveryAPIError(Exception):
    """Base class for a discovery source that could not be ingested. Prefer
    the specific subclasses below so callers can tell "we never got a
    response" apart from "we got a response but it was unusable"."""


class DiscoveryTransportError(DiscoveryAPIError):
    """The request itself failed: network error, timeout, permanent HTTP
    error (4xx), or retries exhausted on a transient error (429/5xx). No
    response body was ever usably received."""


class DiscoveryParseError(DiscoveryAPIError):
    """A response was received (HTTP success) but its body was not valid or
    not shaped as expected (malformed JSON/XML, missing expected keys)."""


@dataclass
class SourceHealth:
    """Per-source status for the discovery summary. Lets the report say
    "SUCCESS - 0 results" instead of leaving 0 ambiguous with a failure."""
    status: str  # "SUCCESS" | "API_ERROR" | "PARSE_ERROR"
    records_returned: int
    message: str

    @classmethod
    def success(cls, records_returned: int, message: str = "OK") -> "SourceHealth":
        return cls(status="SUCCESS", records_returned=records_returned, message=message)

    @classmethod
    def api_error(cls, message: str) -> "SourceHealth":
        return cls(status="API_ERROR", records_returned=0, message=message)

    @classmethod
    def parse_error(cls, message: str) -> "SourceHealth":
        return cls(status="PARSE_ERROR", records_returned=0, message=message)


@dataclass
class DiscoveryWindow:
    start: _dt.date
    end: _dt.date

    def contains(self, date_str: Optional[str]) -> bool:
        if not date_str:
            return False
        try:
            d = _dt.date.fromisoformat(date_str[:10])
        except (ValueError, TypeError):
            return False
        return self.start <= d <= self.end


def compute_discovery_window(lookback_days: int,
                              today: Optional[_dt.date] = None) -> DiscoveryWindow:
    today = today or _dt.date.today()
    start = today - _dt.timedelta(days=lookback_days)
    return DiscoveryWindow(start=start, end=today)


class RateLimiter:
    """Simple sleep-based limiter respecting NCBI/Crossref request-rate
    etiquette. Not thread-safe; discovery runs are sequential in V1."""

    def __init__(self, requests_per_second: float):
        self.min_interval = 1.0 / requests_per_second if requests_per_second > 0 else 0.0
        self._last_call: Optional[float] = None

    def wait(self) -> None:
        if self.min_interval <= 0:
            return
        now = time.monotonic()
        if self._last_call is not None:
            elapsed = now - self._last_call
            remaining = self.min_interval - elapsed
            if remaining > 0:
                time.sleep(remaining)
        self._last_call = time.monotonic()


T = TypeVar("T")

RETRYABLE_HTTP_STATUSES = (429, 500, 502, 503, 504)


def request_with_retries(
    attempt_fn: Callable[[], T],
    max_attempts: int = 3,
    backoff_seconds: float = 1.0,
    retry_statuses=RETRYABLE_HTTP_STATUSES,
    sleep: Callable[[float], None] = time.sleep,
) -> T:
    """Runs `attempt_fn` (one HTTP request), retrying with exponential
    backoff ONLY on HTTP responses whose status is in `retry_statuses`
    (429/5xx -- transient). A 4xx status outside that set (400/401/403/404)
    is a permanent client-side error and is raised immediately, unretried.
    Any non-HTTPError failure (DNS, connection refused, a proxy policy
    denial surfaced as a bare URLError/OSError) is also raised immediately,
    unretried -- it may be a permanent policy block, and this project never
    retries around network/organization policy denials.
    """
    last_exc: Optional[urllib.error.HTTPError] = None
    for attempt in range(1, max_attempts + 1):
        try:
            return attempt_fn()
        except urllib.error.HTTPError as exc:
            if exc.code in retry_statuses and attempt < max_attempts:
                retry_after = exc.headers.get("Retry-After") if exc.headers else None
                if retry_after and retry_after.isdigit():
                    delay = float(retry_after)
                else:
                    delay = backoff_seconds * (2 ** (attempt - 1))
                last_exc = exc
                sleep(delay)
                continue
            raise
    raise last_exc  # pragma: no cover - loop always returns or raises above
