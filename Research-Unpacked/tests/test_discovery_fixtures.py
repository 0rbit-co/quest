"""Stage 2A.1 fixture-mode integration tests.

These run the FULL discovery pipeline (parser -> normalization -> filtering
-> deduplication -> summary) against the on-disk fixtures in
tests/fixtures/, through the exact same production code a live run uses --
only the HTTP layer is swapped for file reads (scripts/discovery/fixtures.py).
No network is touched.
"""
from __future__ import annotations

from pathlib import Path

from scripts.discovery.fixtures import (
    make_crossref_fixture_http_get_json,
    make_pubmed_fixture_http_get,
)
from scripts.run_discovery import load_config, run_discovery

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def _run_fixture_discovery(**overrides):
    config = load_config()
    config = dict(config)
    config["rate_limit_requests_per_second_no_key"] = 1000  # fixtures are local; no need to throttle
    config["rate_limit_requests_per_second_with_key"] = 1000
    config.update(overrides)

    return run_discovery(
        config,
        limit=None,
        pubmed_http_get=make_pubmed_fixture_http_get(FIXTURES_DIR / "pubmed"),
        crossref_http_get_json=make_crossref_fixture_http_get_json(FIXTURES_DIR / "crossref"),
    )


def test_fixture_mode_source_health_is_success():
    result = _run_fixture_discovery()

    assert result.pubmed_health.status == "SUCCESS"
    assert result.pubmed_health.records_returned == len(result.pubmed_raw) > 0
    assert result.crossref_health.status == "SUCCESS"
    assert result.crossref_health.records_returned == len(result.crossref_raw) > 0


def test_fixture_mode_duplicate_paper_becomes_one_candidate_with_both_sources():
    result = _run_fixture_discovery()

    # efetch_with_doi.xml (PubMed) and works_duplicate_of_pubmed.json (Crossref)
    # share DOI 10.1007/s40256-026-00811-x and must merge into ONE candidate.
    matches = [
        c for c in result.deduplicated
        if c.get("doi") == "10.1007/s40256-026-00811-x"
    ]
    assert len(matches) == 1, "duplicate DOI across PubMed/Crossref must merge into one candidate"

    candidate = matches[0]
    assert set(candidate["discovery_sources"]) == {"PUBMED", "CROSSREF"}
    assert candidate["pmid"] == "40100003"  # PubMed's pmid must survive the merge
    assert any("doi match" in note for note in candidate["deduplication_notes"])
    assert result.dedup_audit["doi_merges"] >= 1


def test_fixture_mode_merged_candidate_stays_yellow_and_unscored():
    result = _run_fixture_discovery()

    for candidate in result.deduplicated:
        assert candidate["verification_status"] == "YELLOW", candidate["id"]
        assert candidate["ranking_eligible"] is False, candidate["id"]
        assert candidate["scientific_score"] is None
        assert candidate["youtube_score"] is None
        assert candidate["final_radar_score"] is None
        assert candidate["evidence_tier"] is None
        assert candidate["content_priority"] is None
        assert candidate["production_priority"] is None
        assert all(v is None for v in candidate["scientific_components"].values())
        assert all(v is None for v in candidate["youtube_components"].values())


def test_fixture_mode_no_green_record_is_ever_produced():
    result = _run_fixture_discovery()
    all_candidates = result.kept + result.rejected
    assert all_candidates, "expected fixture data to produce candidates"
    assert all(c["verification_status"] != "GREEN" for c in all_candidates)
    assert all(c["ranking_eligible"] is False for c in all_candidates)


def test_fixture_mode_obvious_editorial_is_rejected():
    result = _run_fixture_discovery()

    editorial = next(
        (c for c in result.deduplicated if c.get("doi") == "10.1000/xyz-editorial"), None
    )
    assert editorial is not None
    assert editorial in result.rejected
    assert editorial["discovery_filter_status"] == "rejected"
    assert "editorial" in editorial["discovery_filter_reason"].lower()
    # Crossref's own `type` field can't say "editorial" (see works_editorial.json's
    # _fixture_note); this record is only catchable because merging pulled in
    # PubMed's PublicationType=Editorial.
    assert set(editorial["discovery_sources"]) == {"PUBMED", "CROSSREF"}


def test_crossref_editorial_alone_is_not_type_filterable():
    """Documents a real limitation: Crossref's `type` vocabulary has no
    'editorial' value, so a Crossref-only record cannot be caught by
    type-substring matching. This is why cross-source merging matters, and
    why GREEN promotion still requires manual verification."""
    from scripts.discovery.normalize import apply_fast_filter, normalize_crossref_record

    config = load_config()
    crossref_only = normalize_crossref_record(
        {
            "DOI": "10.1000/xyz-editorial-standalone",
            "title": ["Editorial: reflections on the field (standalone fixture)"],
            "type": "journal-article",
            "published": {"date-parts": [[2026, 8, 6]]},
        },
        discovered_at="2026-08-31T00:00:00+00:00",
    )
    apply_fast_filter(crossref_only, config)
    assert crossref_only["discovery_filter_status"] == "kept"


def test_fixture_mode_animal_only_pubmed_record_is_not_in_this_batch():
    # This fixture batch intentionally has no animal-only MeSH record (that
    # scenario is covered directly in tests/test_discovery.py); confirm the
    # filter didn't spuriously reject anything unexpected.
    result = _run_fixture_discovery()
    unexpected_rejections = [
        c for c in result.rejected
        if "animal" in (c.get("discovery_filter_reason") or "").lower()
    ]
    assert unexpected_rejections == []


def test_fixture_mode_kept_candidates_cover_expected_traits():
    result = _run_fixture_discovery()
    kept_dois = {c.get("doi") for c in result.kept}

    # A normal Crossref-only article, a DOI-case-normalization case, a
    # missing-abstract case, a multi-author case, and a JATS-markup case
    # should all survive to `kept` (none are editorials or animal-only).
    for doi in (
        "10.1000/fixture-crossref-normal",
        "10.1000/fixture-crossref-doi-case",  # normalized to lowercase
        "10.1000/fixture-crossref-no-abstract",
        "10.1000/fixture-crossref-multi-author",
        "10.1000/fixture-crossref-jats-abstract",
    ):
        assert doi in kept_dois, f"expected {doi} to be kept"

    jats_candidate = next(c for c in result.kept if c.get("doi") == "10.1000/fixture-crossref-jats-abstract")
    assert "<jats:" not in (jats_candidate.get("abstract") or "")
    assert "Background text goes here." in jats_candidate["abstract"]

    multi_author = next(c for c in result.kept if c.get("doi") == "10.1000/fixture-crossref-multi-author")
    assert len(multi_author["authors"]) == 4


def test_fixture_mode_summary_reports_source_health_and_dedup_audit():
    from scripts.run_discovery import render_summary

    result = _run_fixture_discovery()
    summary = render_summary(result, load_config(), written_paths=None, dry_run=True,
                              mode_label="FIXTURE (test)")

    assert "Source Health" in summary
    assert "status: SUCCESS" in summary
    assert "DOI duplicates merged:" in summary
    assert "PMID duplicates merged:" in summary
    assert "Title-fallback duplicates merged:" in summary
    assert "Final unique count:" in summary
