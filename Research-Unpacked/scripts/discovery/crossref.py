"""Crossref discovery via the official Crossref REST API (/works).

No HTML scraping. Every network call goes through `_http_get_json`, which is
injectable so tests/fixture-mode can run entirely offline.

Error handling distinguishes two failure classes (see
scripts/discovery/__init__.py): DiscoveryTransportError (the request itself
failed) vs DiscoveryParseError (a response was received but wasn't the
expected shape). This lets the caller report "SUCCESS - 0 results" as
something different from "FAILED - API error" or "FAILED - parse error".
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Callable, Dict, List, Optional

from . import (
    DiscoveryParseError,
    DiscoveryTransportError,
    DiscoveryWindow,
    RateLimiter,
    request_with_retries,
)

HttpGetJson = Callable[..., Dict[str, Any]]

# The response is a body only; no headers or credentials are ever passed to
# a caller-supplied on_raw callback, so a raw-response dump can never leak
# a mailto address's request context beyond what Crossref itself echoes.
OnRaw = Optional[Callable[[str, Dict[str, Any]], None]]

CROSSREF_SELECT_FIELDS = (
    "DOI,title,container-title,published,published-print,published-online,"
    "author,type,abstract,publisher,URL"
)


def _user_agent() -> str:
    mailto = os.environ.get("CROSSREF_MAILTO")
    base = "ResearchUnpacked-Discovery/1.0 (https://github.com/; mailto:{})"
    return base.format(mailto) if mailto else "ResearchUnpacked-Discovery/1.0"


def _http_get_json(url: str, params: Dict[str, Any], headers: Dict[str, str],
                    timeout: float) -> Dict[str, Any]:
    query = urllib.parse.urlencode(params)
    full_url = f"{url}?{query}"
    req = urllib.request.Request(full_url, headers=headers)

    def _attempt() -> bytes:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()

    try:
        raw = request_with_retries(_attempt)
    except urllib.error.HTTPError as exc:
        raise DiscoveryTransportError(
            f"Crossref request failed ({full_url}): HTTP {exc.code} {exc.reason}"
        ) from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise DiscoveryTransportError(f"Crossref request failed ({full_url}): {exc}") from exc

    return _validate_crossref_body(raw, full_url)


def _validate_crossref_body(raw: bytes, full_url: str) -> Dict[str, Any]:
    if not raw:
        raise DiscoveryParseError(f"Crossref response is empty ({full_url})")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise DiscoveryParseError(f"Crossref response is not valid JSON ({full_url}): {exc}") from exc
    return validate_crossref_message(data, full_url)


def validate_crossref_message(data: Any, context: str = "") -> Dict[str, Any]:
    if not isinstance(data, dict):
        raise DiscoveryParseError(f"Crossref response is not a JSON object ({context})")
    status = data.get("status")
    if status not in (None, "ok"):
        raise DiscoveryParseError(f"Crossref reported status={status!r} ({context})")
    message = data.get("message")
    if not isinstance(message, dict) or "items" not in message:
        raise DiscoveryParseError(
            f"Crossref response is missing the expected 'message.items' structure ({context})"
        )
    if not isinstance(message["items"], list):
        raise DiscoveryParseError(f"Crossref 'message.items' is not a list ({context})")
    return data


def discover_crossref(
    config: Dict[str, Any],
    window: DiscoveryWindow,
    query_terms: List[str],
    limit: Optional[int] = None,
    http_get_json: HttpGetJson = _http_get_json,
    on_raw: OnRaw = None,
) -> List[Dict[str, Any]]:
    """Queries Crossref once per topic term (query.bibliographic), restricted
    to the discovery window and journal-article type, until the configured
    (or --limit-overridden) budget is reached. Returns raw Crossref work
    items (the dicts under message.items). An empty result is a valid,
    successful outcome, not an error."""
    budget = config.get("max_results_per_source", 100)
    if limit is not None:
        budget = min(budget, limit)
    if budget <= 0 or not query_terms:
        return []

    limiter = RateLimiter(config.get("rate_limit_requests_per_second_no_key", 3))
    headers = {"User-Agent": _user_agent()}
    timeout = config.get("request_timeout_seconds", 20)

    filter_value = (
        f"type:journal-article,"
        f"from-pub-date:{window.start.isoformat()},"
        f"until-pub-date:{window.end.isoformat()}"
    )

    seen_dois = set()
    items: List[Dict[str, Any]] = []
    per_topic_rows = max(1, budget // max(1, len(query_terms)))

    for topic in query_terms:
        if len(items) >= budget:
            break
        rows = min(per_topic_rows, budget - len(items))
        params = {
            "query.bibliographic": topic,
            "filter": filter_value,
            "rows": rows,
            "select": CROSSREF_SELECT_FIELDS,
        }
        limiter.wait()
        data = http_get_json(config["crossref_api_url"], params, headers, timeout)
        data = validate_crossref_message(data, context=f"topic={topic!r}")
        if on_raw:
            on_raw("crossref", {"topic": topic, "response": data})
        for work in data["message"]["items"]:
            doi = (work.get("DOI") or "").lower().strip()
            if doi and doi in seen_dois:
                continue
            if doi:
                seen_dois.add(doi)
            items.append(work)
            if len(items) >= budget:
                break

    return items
