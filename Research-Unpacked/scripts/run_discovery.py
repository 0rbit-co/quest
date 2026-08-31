#!/usr/bin/env python3
"""Stage 2A: PubMed + Crossref discovery ingestion (discovery only).

Fetches recent candidate research metadata from PubMed and Crossref,
normalizes it into one candidate format, deduplicates, applies a
conservative fast filter, and writes candidate JSON files to
research/inbox/. Every candidate is written with verification_status=YELLOW
and ranking_eligible=false -- this script never assigns GREEN and never
computes scientific/YouTube scores. Promotion to GREEN happens later,
through the manual verification pipeline (prompts/verification.md).

Usage:
    python3 scripts/run_discovery.py [--dry-run] [--limit N]
    python3 scripts/run_discovery.py --fixture-mode tests/fixtures --dry-run
    python3 scripts/run_discovery.py --save-raw
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.discovery import (  # noqa: E402
    DiscoveryParseError,
    DiscoveryTransportError,
    SourceHealth,
    compute_discovery_window,
)
from scripts.discovery.crossref import discover_crossref  # noqa: E402
from scripts.discovery.deduplicate import deduplicate_with_audit  # noqa: E402
from scripts.discovery.fixtures import (  # noqa: E402
    make_crossref_fixture_http_get_json,
    make_pubmed_fixture_http_get,
)
from scripts.discovery.normalize import (  # noqa: E402
    apply_fast_filter,
    normalize_crossref_record,
    normalize_pubmed_record,
)
from scripts.discovery.pubmed import discover_pubmed  # noqa: E402

ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = ROOT_DIR / "config" / "discovery.json"
DEFAULT_INBOX_DIR = ROOT_DIR / "research" / "inbox"
DEFAULT_REPORTS_DIR = ROOT_DIR / "reports"
DEFAULT_RAW_DIR = ROOT_DIR / "data" / "raw-discovery"


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@dataclass
class DiscoveryRunResult:
    pubmed_raw: List[Dict[str, Any]] = field(default_factory=list)
    crossref_raw: List[Dict[str, Any]] = field(default_factory=list)
    pubmed_health: SourceHealth = field(
        default_factory=lambda: SourceHealth.success(0, "not run"))
    crossref_health: SourceHealth = field(
        default_factory=lambda: SourceHealth.success(0, "not run"))
    deduplicated: List[Dict[str, Any]] = field(default_factory=list)
    dedup_audit: Dict[str, int] = field(default_factory=dict)
    kept: List[Dict[str, Any]] = field(default_factory=list)
    rejected: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def unique_count(self) -> int:
        return len(self.deduplicated)


def run_discovery(
    config: Dict[str, Any],
    discovered_at: Optional[str] = None,
    limit: Optional[int] = None,
    pubmed_http_get=None,
    crossref_http_get_json=None,
    today: Optional[_dt.date] = None,
    pubmed_on_raw=None,
    crossref_on_raw=None,
) -> DiscoveryRunResult:
    """Runs the full discovery pipeline and returns the result in memory.
    Writing files is the caller's job (see main()) so this function is easy
    to test without touching disk."""
    discovered_at = discovered_at or _dt.datetime.now(_dt.timezone.utc).isoformat()
    window = compute_discovery_window(config.get("lookback_days", 30), today=today)

    pubmed_terms = config.get("pubmed_query_terms") or config.get("priority_topics", [])
    crossref_terms = config.get("crossref_query_terms") or config.get("priority_topics", [])

    result = DiscoveryRunResult()

    try:
        kwargs = {"http_get": pubmed_http_get} if pubmed_http_get is not None else {}
        result.pubmed_raw = discover_pubmed(
            config, window, pubmed_terms, limit=limit, on_raw=pubmed_on_raw, **kwargs
        )
        result.pubmed_health = SourceHealth.success(
            len(result.pubmed_raw), f"fetched {len(result.pubmed_raw)} record(s)"
        )
    except DiscoveryTransportError as exc:
        result.pubmed_health = SourceHealth.api_error(str(exc))
    except DiscoveryParseError as exc:
        result.pubmed_health = SourceHealth.parse_error(str(exc))

    try:
        kwargs = {"http_get_json": crossref_http_get_json} if crossref_http_get_json is not None else {}
        result.crossref_raw = discover_crossref(
            config, window, crossref_terms, limit=limit, on_raw=crossref_on_raw, **kwargs
        )
        result.crossref_health = SourceHealth.success(
            len(result.crossref_raw), f"fetched {len(result.crossref_raw)} record(s)"
        )
    except DiscoveryTransportError as exc:
        result.crossref_health = SourceHealth.api_error(str(exc))
    except DiscoveryParseError as exc:
        result.crossref_health = SourceHealth.parse_error(str(exc))

    normalized: List[Dict[str, Any]] = []
    for raw in result.pubmed_raw:
        normalized.append(normalize_pubmed_record(raw, discovered_at))
    for raw in result.crossref_raw:
        normalized.append(normalize_crossref_record(raw, discovered_at))

    threshold = config.get("title_similarity_threshold", 0.92)
    result.deduplicated, result.dedup_audit = deduplicate_with_audit(
        normalized, title_similarity_threshold=threshold
    )

    for candidate in result.deduplicated:
        if not window.contains(candidate.get("publication_date")):
            candidate["discovery_filter_status"] = "rejected"
            candidate["discovery_filter_reason"] = (
                f"publication_date {candidate.get('publication_date')!r} is not "
                f"confirmed inside the discovery window [{window.start.isoformat()}, "
                f"{window.end.isoformat()}]"
            )
        else:
            apply_fast_filter(candidate, config)

        if candidate["discovery_filter_status"] == "rejected":
            result.rejected.append(candidate)
        else:
            result.kept.append(candidate)

    return result


def write_candidates(kept: List[Dict[str, Any]], inbox_dir: Path) -> List[Path]:
    inbox_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for candidate in kept:
        path = inbox_dir / f"{candidate['id']}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(candidate, f, indent=2, ensure_ascii=False)
            f.write("\n")
        written.append(path)
    return written


def _format_health(name: str, health: SourceHealth) -> List[str]:
    return [
        f"{name}:",
        f"  status: {health.status}",
        f"  records_returned: {health.records_returned}",
        f"  message: {health.message}",
    ]


def render_summary(result: DiscoveryRunResult, config: Dict[str, Any],
                    written_paths: Optional[List[Path]], dry_run: bool,
                    mode_label: str = "LIVE") -> str:
    today = _dt.date.today().isoformat()
    lines = [f"# Discovery Run — {today}", ""]
    lines.append(f"Mode: {mode_label}{' (dry-run, no files written)' if dry_run else ''}")
    lines.append("")

    lines.append("Source Health")
    lines.extend(_format_health("PubMed", result.pubmed_health))
    lines.extend(_format_health("Crossref", result.crossref_health))
    lines.append("")

    lines.append(f"PubMed records fetched: {len(result.pubmed_raw)}")
    lines.append(f"Crossref records fetched: {len(result.crossref_raw)}")
    lines.append(f"Unique records after deduplication: {result.unique_count}")
    lines.append(f"Automatically rejected: {len(result.rejected)}")
    lines.append(f"Candidates written to inbox: {0 if dry_run else len(written_paths or [])}")
    lines.append("")

    lines.append("Deduplication audit:")
    lines.append(f"  PubMed records (pre-dedup): {len(result.pubmed_raw)}")
    lines.append(f"  Crossref records (pre-dedup): {len(result.crossref_raw)}")
    lines.append(f"  DOI duplicates merged: {result.dedup_audit.get('doi_merges', 0)}")
    lines.append(f"  PMID duplicates merged: {result.dedup_audit.get('pmid_merges', 0)}")
    lines.append(f"  Title-fallback duplicates merged: {result.dedup_audit.get('title_merges', 0)}")
    lines.append(f"  Final unique count: {result.unique_count}")
    lines.append("")

    journal_counts = Counter(
        c.get("journal") for c in result.deduplicated if c.get("journal")
    )
    if journal_counts:
        lines.append("Top journals represented:")
        for journal, count in journal_counts.most_common(10):
            lines.append(f"  - {journal}: {count}")
        lines.append("")

    type_counts = Counter()
    for c in result.deduplicated:
        for t in (c.get("publication_types") or [c.get("publication_status")]):
            if t:
                type_counts[t] += 1
    if type_counts:
        lines.append("Publication types:")
        for ptype, count in type_counts.most_common(10):
            lines.append(f"  - {ptype}: {count}")
        lines.append("")

    if result.rejected:
        lines.append("Rejected candidates:")
        for c in result.rejected:
            lines.append(f"  - {c.get('id')}: {c.get('discovery_filter_reason')}")
        lines.append("")

    if any(c.get("deduplication_notes") for c in result.deduplicated):
        lines.append("Merge provenance:")
        for c in result.deduplicated:
            if c.get("deduplication_notes"):
                lines.append(f"  - {c.get('id')} (sources: {c.get('discovery_sources')}):")
                for note in c["deduplication_notes"]:
                    lines.append(f"      {note}")
        lines.append("")

    lines.append(
        "No candidate in this report is scientifically verified. All kept "
        "candidates are written with verification_status=YELLOW and "
        "ranking_eligible=false; GREEN promotion requires the manual "
        "verification pipeline (prompts/verification.md)."
    )
    return "\n".join(lines)


def _make_raw_saver(raw_dir: Path):
    """Returns (on_pubmed_raw, on_crossref_raw, flush) callbacks for
    --save-raw. Only ever writes response BODIES -- never request headers,
    params, API keys, or other environment/credential data."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    counters = {"efetch": 0}
    crossref_records: List[Dict[str, Any]] = []

    def on_pubmed_raw(kind: str, raw_bytes: bytes) -> None:
        if kind == "esearch":
            (raw_dir / "pubmed_esearch.json").write_bytes(raw_bytes)
        elif kind == "efetch":
            counters["efetch"] += 1
            suffix = "" if counters["efetch"] == 1 else f"_{counters['efetch']}"
            (raw_dir / f"pubmed_efetch{suffix}.xml").write_bytes(raw_bytes)

    def on_crossref_raw(kind: str, payload: Dict[str, Any]) -> None:
        crossref_records.append(payload)

    def flush() -> None:
        if crossref_records:
            (raw_dir / "crossref.json").write_text(
                json.dumps(crossref_records, indent=2, ensure_ascii=False), encoding="utf-8"
            )

    return on_pubmed_raw, on_crossref_raw, flush


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                         help="Run the full pipeline but write nothing to disk.")
    parser.add_argument("--limit", type=int, default=None,
                         help="Cap results per source (development/testing).")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--inbox-dir", type=Path, default=DEFAULT_INBOX_DIR)
    parser.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR)
    parser.add_argument(
        "--fixture-mode", type=Path, default=None, metavar="DIR",
        help=(
            "Replay canned responses from DIR (expects DIR/pubmed and "
            "DIR/crossref, e.g. tests/fixtures) through the same parser/"
            "normalize/dedup/filter code as a live run. No network is used."
        ),
    )
    parser.add_argument(
        "--save-raw", action="store_true",
        help=(
            "Save raw API response bodies under data/raw-discovery/YYYY-MM-DD/ "
            "(git-ignored). Ignored in --fixture-mode, since there is no live "
            "response to save. Never saves headers, keys, or env vars."
        ),
    )
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    args = parser.parse_args(argv)

    config = load_config(args.config)

    pubmed_http_get = None
    crossref_http_get_json = None
    mode_label = "LIVE"

    if args.fixture_mode is not None:
        mode_label = f"FIXTURE ({args.fixture_mode})"
        pubmed_http_get = make_pubmed_fixture_http_get(args.fixture_mode / "pubmed")
        crossref_http_get_json = make_crossref_fixture_http_get_json(args.fixture_mode / "crossref")
        # Fixture files are local and static; no need to throttle reads.
        config = dict(config)
        config["rate_limit_requests_per_second_no_key"] = 1000
        config["rate_limit_requests_per_second_with_key"] = 1000

    pubmed_on_raw = crossref_on_raw = flush_raw = None
    if args.save_raw and args.fixture_mode is None:
        today_dir = args.raw_dir / _dt.date.today().isoformat()
        pubmed_on_raw, crossref_on_raw, flush_raw = _make_raw_saver(today_dir)

    result = run_discovery(
        config,
        limit=args.limit,
        pubmed_http_get=pubmed_http_get,
        crossref_http_get_json=crossref_http_get_json,
        pubmed_on_raw=pubmed_on_raw,
        crossref_on_raw=crossref_on_raw,
    )

    if flush_raw is not None:
        flush_raw()

    written_paths = None
    if not args.dry_run:
        written_paths = write_candidates(result.kept, args.inbox_dir)

    summary = render_summary(result, config, written_paths, dry_run=args.dry_run, mode_label=mode_label)
    print(summary)

    if not args.dry_run:
        args.reports_dir.mkdir(parents=True, exist_ok=True)
        report_path = args.reports_dir / f"discovery-{_dt.date.today().isoformat()}.md"
        report_path.write_text(summary, encoding="utf-8")
        print(f"\nWritten to {report_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
