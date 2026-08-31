"""Fixture-mode support: replays canned PubMed/Crossref responses from disk
through the exact same parsing/normalization code used for live requests.

No network is touched, and no parsing/normalization/dedup/filter logic is
duplicated here -- these functions only build `http_get`/`http_get_json`
replacements that read fixture files instead of calling urlopen. Everything
downstream (parse_pubmed_xml, normalize_*, deduplicate, apply_fast_filter)
is the exact same production code path a live run uses.
"""
from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List

from . import DiscoveryParseError


def load_pubmed_esearch_fixture(fixture_dir: Path) -> bytes:
    path = fixture_dir / "esearch_response.json"
    if not path.exists():
        raise DiscoveryParseError(f"fixture-mode: missing {path}")
    return path.read_bytes()


def load_pubmed_efetch_fixture(fixture_dir: Path) -> bytes:
    """Combines every efetch_*.xml fixture file in `fixture_dir` into one
    <PubmedArticleSet>, so a fixture-mode run exercises the same
    "batch efetch response" parsing path a live multi-record fetch would."""
    files = sorted(fixture_dir.glob("efetch_*.xml"))
    if not files:
        raise DiscoveryParseError(f"fixture-mode: no efetch_*.xml fixtures found in {fixture_dir}")
    combined = ET.Element("PubmedArticleSet")
    for f in files:
        try:
            tree = ET.parse(f)
        except ET.ParseError as exc:
            raise DiscoveryParseError(f"fixture-mode: could not parse {f}: {exc}") from exc
        for article in tree.getroot().findall(".//PubmedArticle"):
            combined.append(article)
    return ET.tostring(combined)


def make_pubmed_fixture_http_get(fixture_dir: Path):
    """Returns an http_get-shaped callable (url, params, timeout) -> bytes
    that reads from fixture files instead of the network. Passed straight
    into scripts.discovery.pubmed.discover_pubmed(..., http_get=...)."""

    def _fixture_http_get(url: str, params: Dict[str, Any], timeout: float) -> bytes:
        if "esearch" in url:
            return load_pubmed_esearch_fixture(fixture_dir)
        return load_pubmed_efetch_fixture(fixture_dir)

    return _fixture_http_get


def load_crossref_items_fixture(fixture_dir: Path) -> List[Dict[str, Any]]:
    """Combines the message.items of every works_*.json fixture file in
    `fixture_dir` into one list, so a fixture-mode run exercises the same
    "many works in one response" parsing path a live query would."""
    files = sorted(fixture_dir.glob("works_*.json"))
    if not files:
        raise DiscoveryParseError(f"fixture-mode: no works_*.json fixtures found in {fixture_dir}")
    items: List[Dict[str, Any]] = []
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise DiscoveryParseError(f"fixture-mode: could not parse {f}: {exc}") from exc
        message = data.get("message") if isinstance(data, dict) else None
        file_items = message.get("items") if isinstance(message, dict) else None
        if file_items is None:
            raise DiscoveryParseError(f"fixture-mode: {f} is missing message.items")
        items.extend(file_items)
    return items


def make_crossref_fixture_http_get_json(fixture_dir: Path):
    """Returns an http_get_json-shaped callable
    (url, params, headers, timeout) -> dict that reads from fixture files
    instead of the network. Passed straight into
    scripts.discovery.crossref.discover_crossref(..., http_get_json=...).

    All combined fixture items are returned on every call (the `rows`
    param is not honored -- fixture files are small and static); the
    per-topic loop in discover_crossref already deduplicates by DOI across
    repeated calls, so this only affects wall-clock time, not results.
    """
    cache: Dict[str, List[Dict[str, Any]]] = {}

    def _fixture_http_get_json(url: str, params: Dict[str, Any],
                                headers: Dict[str, str], timeout: float) -> Dict[str, Any]:
        if "items" not in cache:
            cache["items"] = load_crossref_items_fixture(fixture_dir)
        return {"status": "ok", "message-type": "work-list", "message": {"items": cache["items"]}}

    return _fixture_http_get_json
