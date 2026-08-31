"""Stage 2A tests: PubMed/Crossref discovery ingestion, fully mocked.

No test in this file touches the network. HTTP calls are replaced with
in-memory fakes so the suite runs offline and deterministically.
"""
from __future__ import annotations

import datetime as _dt
import json

import pytest

from scripts.discovery import DiscoveryWindow, compute_discovery_window
from scripts.discovery.deduplicate import deduplicate, merge_candidates
from scripts.discovery.normalize import (
    apply_fast_filter,
    normalize_crossref_record,
    normalize_doi,
    normalize_pubmed_record,
    normalize_title_for_matching,
)
from scripts.discovery.pubmed import parse_pubmed_xml
from scripts.run_discovery import load_config, main as run_discovery_main, run_discovery

DISCOVERED_AT = "2026-08-31T00:00:00+00:00"


# ---------------------------------------------------------------------------
# Fixtures: canned PubMed XML and Crossref JSON
# ---------------------------------------------------------------------------

PUBMED_XML = b"""<?xml version="1.0"?>
<PubmedArticleSet>
  <PubmedArticle>
    <MedlineCitation>
      <PMID>40012345</PMID>
      <Article>
        <Journal>
          <Title>Nature Medicine</Title>
        </Journal>
        <ArticleTitle>A randomized trial of stair climbing in humans</ArticleTitle>
        <Abstract>
          <AbstractText Label="BACKGROUND">Stair climbing may reduce risk.</AbstractText>
          <AbstractText Label="RESULTS">Risk was reduced.</AbstractText>
        </Abstract>
        <AuthorList>
          <Author><LastName>Smith</LastName><Initials>J</Initials></Author>
          <Author><LastName>Doe</LastName><Initials>A</Initials></Author>
        </AuthorList>
        <PublicationTypeList>
          <PublicationType>Journal Article</PublicationType>
          <PublicationType>Randomized Controlled Trial</PublicationType>
        </PublicationTypeList>
        <ArticleDate DateType="Electronic">
          <Year>2026</Year><Month>08</Month><Day>13</Day>
        </ArticleDate>
        <ELocationID EIdType="doi">10.1007/s40256-026-00811-x</ELocationID>
      </Article>
    </MedlineCitation>
    <PubmedData>
      <ArticleIdList>
        <ArticleId IdType="doi">10.1007/s40256-026-00811-x</ArticleId>
        <ArticleId IdType="pubmed">40012345</ArticleId>
      </ArticleIdList>
    </PubmedData>
  </PubmedArticle>
  <PubmedArticle>
    <MedlineCitation>
      <PMID>40099999</PMID>
      <Article>
        <Journal><Title>Journal of Editorials</Title></Journal>
        <ArticleTitle>Editorial: on the state of the field</ArticleTitle>
        <AuthorList>
          <Author><LastName>Editor</LastName><Initials>E</Initials></Author>
        </AuthorList>
        <PublicationTypeList>
          <PublicationType>Editorial</PublicationType>
        </PublicationTypeList>
        <ArticleDate DateType="Electronic">
          <Year>2026</Year><Month>08</Month><Day>10</Day>
        </ArticleDate>
      </Article>
    </MedlineCitation>
  </PubmedArticle>
  <PubmedArticle>
    <MedlineCitation>
      <PMID>40088888</PMID>
      <Article>
        <Journal><Title>Mouse Studies Quarterly</Title></Journal>
        <ArticleTitle>A mouse model of neurogenesis</ArticleTitle>
        <AuthorList>
          <Author><LastName>Mouse</LastName><Initials>M</Initials></Author>
        </AuthorList>
        <PublicationTypeList>
          <PublicationType>Journal Article</PublicationType>
        </PublicationTypeList>
        <ArticleDate DateType="Electronic">
          <Year>2026</Year><Month>08</Month><Day>12</Day>
        </ArticleDate>
      </Article>
      <MeshHeadingList>
        <MeshHeading><DescriptorName>Animals</DescriptorName></MeshHeading>
        <MeshHeading><DescriptorName>Mice</DescriptorName></MeshHeading>
      </MeshHeadingList>
    </MedlineCitation>
  </PubmedArticle>
</PubmedArticleSet>
"""

CROSSREF_WORK_MATCHING_DOI = {
    "DOI": "10.1007/S40256-026-00811-X",  # deliberately different case than PubMed's
    "title": ["A randomized trial of stair climbing in humans"],
    "container-title": ["Nature Medicine"],
    "type": "journal-article",
    "publisher": "Springer",
    "URL": "https://link.springer.com/article/10.1007/s40256-026-00811-x",
    "published": {"date-parts": [[2026, 8, 13]]},
    "author": [{"family": "Smith", "given": "J"}, {"family": "Doe", "given": "A"}],
}

CROSSREF_WORK_UNIQUE = {
    "DOI": "10.1038/s41591-026-04571-8",
    "title": ["Dysregulated adult hippocampal neurogenesis in major depressive disorder"],
    "container-title": ["Nature Medicine"],
    "type": "journal-article",
    "publisher": "Springer Nature",
    "URL": "https://www.nature.com/articles/s41591-026-04571-8",
    "published": {"date-parts": [[2026, 8, 21]]},
    "abstract": "<jats:p>MDD hippocampi showed altered neurogenesis.</jats:p>",
    "author": [{"family": "Lee", "given": "K"}],
}


# ---------------------------------------------------------------------------
# DOI normalization
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw,expected", [
    ("10.1038/s41591-026-04571-8", "10.1038/s41591-026-04571-8"),
    ("https://doi.org/10.1038/S41591-026-04571-8", "10.1038/s41591-026-04571-8"),
    ("http://dx.doi.org/10.1038/s41591-026-04571-8", "10.1038/s41591-026-04571-8"),
    ("doi:10.1038/s41591-026-04571-8", "10.1038/s41591-026-04571-8"),
    ("  10.1038/s41591-026-04571-8.  ", "10.1038/s41591-026-04571-8"),
    (None, None),
    ("", None),
])
def test_normalize_doi(raw, expected):
    assert normalize_doi(raw) == expected


# ---------------------------------------------------------------------------
# PubMed XML parsing + normalization
# ---------------------------------------------------------------------------

def test_parse_pubmed_xml_extracts_three_articles():
    records = parse_pubmed_xml(PUBMED_XML)
    assert len(records) == 3
    assert records[0]["pmid"] == "40012345"
    assert records[0]["doi"] == "10.1007/s40256-026-00811-x"
    assert records[0]["journal"] == "Nature Medicine"
    assert records[0]["publication_date"] == "2026-08-13"
    assert "Smith J" in records[0]["authors"]
    assert "Randomized Controlled Trial" in records[0]["publication_types"]
    assert "reduce risk" in records[0]["abstract"]


def test_normalize_pubmed_record_is_yellow_with_null_scoring():
    raw = parse_pubmed_xml(PUBMED_XML)[0]
    candidate = normalize_pubmed_record(raw, DISCOVERED_AT)

    assert candidate["verification_status"] == "YELLOW"
    assert candidate["ranking_eligible"] is False
    assert candidate["verification_notes"] == "Discovery metadata only. Primary-source verification required."
    assert candidate["scientific_score"] is None
    assert candidate["youtube_score"] is None
    assert candidate["final_radar_score"] is None
    assert candidate["evidence_tier"] is None
    assert candidate["content_priority"] is None
    assert candidate["production_priority"] is None
    assert all(v is None for v in candidate["scientific_components"].values())
    assert all(v is None for v in candidate["youtube_components"].values())
    assert candidate["discovery_sources"] == ["PUBMED"]
    assert candidate["doi"] == "10.1007/s40256-026-00811-x"
    assert candidate["pmid"] == "40012345"


# ---------------------------------------------------------------------------
# Crossref normalization
# ---------------------------------------------------------------------------

def test_normalize_crossref_record_is_yellow_with_null_scoring():
    candidate = normalize_crossref_record(CROSSREF_WORK_UNIQUE, DISCOVERED_AT)

    assert candidate["verification_status"] == "YELLOW"
    assert candidate["ranking_eligible"] is False
    assert candidate["doi"] == "10.1038/s41591-026-04571-8"
    assert candidate["journal"] == "Nature Medicine"
    assert candidate["publication_date"] == "2026-08-21"
    assert candidate["discovery_sources"] == ["CROSSREF"]
    assert candidate["abstract"] == "MDD hippocampi showed altered neurogenesis."  # JATS tags stripped
    assert candidate["scientific_score"] is None
    assert candidate["youtube_score"] is None


# ---------------------------------------------------------------------------
# Deduplication: PubMed/Crossref merge by DOI, and title-similarity fallback
# ---------------------------------------------------------------------------

def test_pubmed_crossref_duplicate_merge_by_doi():
    pubmed_raw = parse_pubmed_xml(PUBMED_XML)[0]
    pubmed_candidate = normalize_pubmed_record(pubmed_raw, DISCOVERED_AT)
    crossref_candidate = normalize_crossref_record(CROSSREF_WORK_MATCHING_DOI, DISCOVERED_AT)

    merged = deduplicate([pubmed_candidate, crossref_candidate])

    assert len(merged) == 1
    record = merged[0]
    assert set(record["discovery_sources"]) == {"PUBMED", "CROSSREF"}
    # PubMed's abstract/pmid must survive the merge (not deleted by Crossref's emptier record)
    assert record["pmid"] == "40012345"
    assert record["abstract"] and "reduce risk" in record["abstract"]
    assert record["publisher"] == "Springer"  # only Crossref had this field


def test_fallback_duplicate_handling_by_title_similarity():
    a = normalize_crossref_record({
        "DOI": None,
        "title": ["Stair climbing and cardiovascular mortality risk"],
        "container-title": ["Some Journal"],
        "type": "journal-article",
        "published": {"date-parts": [[2026, 8, 13]]},
    }, DISCOVERED_AT)
    b = normalize_crossref_record({
        "DOI": None,
        "title": ["Stair climbing and cardiovascular mortality risk."],
        "container-title": ["Some Journal"],
        "type": "journal-article",
        "published": {"date-parts": [[2026, 8, 13]]},
        "publisher": "Some Publisher",
    }, DISCOVERED_AT)

    merged = deduplicate([a, b], title_similarity_threshold=0.92)

    assert len(merged) == 1
    assert merged[0]["publisher"] == "Some Publisher"


def test_distinct_titles_are_not_merged():
    a = normalize_crossref_record(CROSSREF_WORK_UNIQUE, DISCOVERED_AT)
    b = normalize_crossref_record({
        "DOI": "10.1038/s41591-026-04561-w",
        "title": ["County, district and community-level measles transmission"],
        "container-title": ["Nature Medicine"],
        "type": "journal-article",
        "published": {"date-parts": [[2026, 8, 18]]},
    }, DISCOVERED_AT)

    merged = deduplicate([a, b])
    assert len(merged) == 2


def test_merge_candidates_unions_discovery_sources_without_deleting_fields():
    base = {"discovery_sources": ["PUBMED"], "abstract": "rich abstract", "doi": "10.1/x",
            "authors": ["A"], "mesh_terms": ["Humans"], "publication_types": ["Journal Article"],
            "provisional_fields": ["journal"], "scientific_components": {"a": None},
            "youtube_components": {"b": None}, "id": "doi-10-1-x", "exact_title": "T"}
    other = {"discovery_sources": ["CROSSREF"], "abstract": None, "doi": "10.1/x",
             "authors": ["B"], "mesh_terms": [], "publication_types": [],
             "provisional_fields": ["journal"], "scientific_components": {"a": None},
             "youtube_components": {"b": None}, "id": "doi-10-1-x", "publisher": "Pub Co",
             "exact_title": "T"}

    merged = merge_candidates(base, other)

    assert set(merged["discovery_sources"]) == {"PUBMED", "CROSSREF"}
    assert merged["abstract"] == "rich abstract"
    assert merged["authors"] == ["A", "B"]
    assert merged["publisher"] == "Pub Co"


# ---------------------------------------------------------------------------
# Fast discovery filter
# ---------------------------------------------------------------------------

def test_editorial_publication_type_is_rejected():
    raw = parse_pubmed_xml(PUBMED_XML)[1]  # the "Editorial" fixture
    candidate = normalize_pubmed_record(raw, DISCOVERED_AT)
    config = load_config()

    apply_fast_filter(candidate, config)

    assert candidate["discovery_filter_status"] == "rejected"
    assert "editorial" in candidate["discovery_filter_reason"].lower()


def test_animal_only_mesh_is_rejected():
    raw = parse_pubmed_xml(PUBMED_XML)[2]  # the mouse-only fixture
    candidate = normalize_pubmed_record(raw, DISCOVERED_AT)
    config = load_config()

    apply_fast_filter(candidate, config)

    assert candidate["discovery_filter_status"] == "rejected"
    assert "animal" in candidate["discovery_filter_reason"].lower()


def test_uncertain_publication_type_is_kept_conservatively():
    candidate = normalize_crossref_record({
        "DOI": "10.1/uncertain",
        "title": ["Some study with no declared type info"],
        "type": "journal-article",
        "published": {"date-parts": [[2026, 8, 15]]},
    }, DISCOVERED_AT)
    # No publication_types, no mesh_terms -> nothing to reject on.
    candidate["publication_types"] = []
    config = load_config()

    apply_fast_filter(candidate, config)

    assert candidate["discovery_filter_status"] == "kept"


def test_normal_journal_article_is_kept():
    raw = parse_pubmed_xml(PUBMED_XML)[0]
    candidate = normalize_pubmed_record(raw, DISCOVERED_AT)
    config = load_config()

    apply_fast_filter(candidate, config)

    assert candidate["discovery_filter_status"] == "kept"


# ---------------------------------------------------------------------------
# Window filtering + end-to-end run_discovery with fake HTTP layer
# ---------------------------------------------------------------------------

def _fake_pubmed_http_get(url, params, timeout):
    if "esearch" in url:
        return json.dumps({"esearchresult": {"idlist": ["40012345", "40099999", "40088888"]}}).encode()
    return PUBMED_XML


def _fake_crossref_http_get_json(url, params, headers, timeout):
    return {"message": {"items": [CROSSREF_WORK_UNIQUE]}}


def test_out_of_window_record_is_excluded(monkeypatch):
    config = load_config()
    config["lookback_days"] = 30
    config["rate_limit_requests_per_second_no_key"] = 1000  # keep the test fast; no real network involved

    # Force the discovery window to a range that excludes every fixture date.
    fixed_today = _dt.date(2026, 8, 31)

    def fake_pubmed_far_in_past(url, params, timeout):
        if "esearch" in url:
            return json.dumps({"esearchresult": {"idlist": ["40012345"]}}).encode()
        # Reuse the real XML but note its dates (2026-08) will be far outside
        # a window computed from a `today` many days later.
        return PUBMED_XML

    result = run_discovery(
        config,
        limit=10,
        pubmed_http_get=fake_pubmed_far_in_past,
        crossref_http_get_json=lambda *a, **k: {"message": {"items": []}},
        today=_dt.date(2027, 6, 1),  # far past the 30-day lookback from the fixtures' 2026-08 dates
    )

    assert len(result.kept) == 0
    assert len(result.rejected) >= 1
    assert any("discovery window" in c["discovery_filter_reason"] for c in result.rejected)


def test_in_window_record_is_kept_and_yellow():
    config = load_config()
    config["rate_limit_requests_per_second_no_key"] = 1000  # keep the test fast; no real network involved
    result = run_discovery(
        config,
        limit=10,
        pubmed_http_get=_fake_pubmed_http_get,
        crossref_http_get_json=_fake_crossref_http_get_json,
        today=_dt.date(2026, 8, 31),
    )

    kept_ids = {c["id"] for c in result.kept}
    assert any("40256-026-00811" in i or "stair" in i for i in kept_ids) or len(result.kept) >= 1
    for candidate in result.kept:
        assert candidate["verification_status"] == "YELLOW"
        assert candidate["ranking_eligible"] is False
        assert candidate["scientific_score"] is None

    # the editorial and mouse-only fixtures must not survive to `kept`
    kept_titles = " ".join((c.get("exact_title") or "") for c in result.kept).lower()
    assert "editorial" not in kept_titles
    assert "mouse model" not in kept_titles


def test_dry_run_does_not_write_files(monkeypatch, tmp_path):
    import scripts.run_discovery as run_discovery_module

    monkeypatch.setattr(run_discovery_module, "discover_pubmed",
                         lambda *a, **k: [parse_pubmed_xml(PUBMED_XML)[0]])
    monkeypatch.setattr(run_discovery_module, "discover_crossref",
                         lambda *a, **k: [CROSSREF_WORK_UNIQUE])

    inbox_dir = tmp_path / "inbox"
    reports_dir = tmp_path / "reports"

    exit_code = run_discovery_main([
        "--dry-run", "--limit", "5",
        "--inbox-dir", str(inbox_dir),
        "--reports-dir", str(reports_dir),
    ])

    assert exit_code == 0
    assert not inbox_dir.exists() or list(inbox_dir.iterdir()) == []
    assert not reports_dir.exists()


def test_live_run_writes_candidate_files(monkeypatch, tmp_path):
    import scripts.run_discovery as run_discovery_module

    monkeypatch.setattr(run_discovery_module, "discover_pubmed",
                         lambda *a, **k: [parse_pubmed_xml(PUBMED_XML)[0]])
    monkeypatch.setattr(run_discovery_module, "discover_crossref",
                         lambda *a, **k: [])

    inbox_dir = tmp_path / "inbox"
    reports_dir = tmp_path / "reports"

    exit_code = run_discovery_main([
        "--limit", "5",
        "--inbox-dir", str(inbox_dir),
        "--reports-dir", str(reports_dir),
    ])

    assert exit_code == 0
    written = list(inbox_dir.glob("*.json"))
    assert len(written) == 1
    data = json.loads(written[0].read_text())
    assert data["verification_status"] == "YELLOW"
    assert data["ranking_eligible"] is False
    assert list(reports_dir.glob("discovery-*.md"))


def test_title_similarity_helper_is_symmetric_and_normalizes():
    a = normalize_title_for_matching("Stair-Climbing & Cardiovascular Mortality!")
    b = normalize_title_for_matching("stair climbing   cardiovascular mortality")
    assert a == b


def test_compute_discovery_window():
    window = compute_discovery_window(30, today=_dt.date(2026, 8, 31))
    assert isinstance(window, DiscoveryWindow)
    assert window.end == _dt.date(2026, 8, 31)
    assert window.start == _dt.date(2026, 8, 1)
    assert window.contains("2026-08-15")
    assert not window.contains("2026-07-01")
    assert not window.contains(None)
