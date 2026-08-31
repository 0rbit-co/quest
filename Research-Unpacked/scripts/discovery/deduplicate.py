"""Deduplicates normalized candidates found by both PubMed and Crossref.

Matching priority, per spec: (1) normalized DOI, (2) PMID, (3) fallback
normalized-title similarity. Merging never deletes useful metadata -- for
each field it prefers whichever record has the more complete (non-null,
non-empty) value, and list-valued fields (authors, discovery_sources, etc.)
are unioned rather than overwritten. Each merge is recorded in the merged
candidate's `deduplication_notes` for provenance.
"""
from __future__ import annotations

import difflib
from typing import Any, Dict, List, Optional, Tuple

from .normalize import make_candidate_id, normalize_title_for_matching

_LIST_FIELDS = ("discovery_sources", "authors", "mesh_terms", "publication_types",
                 "provisional_fields", "deduplication_notes")


def _is_empty(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def _prefer(a: Any, b: Any) -> Any:
    """Prefer a if non-empty, else b."""
    return a if not _is_empty(a) else b


def merge_candidates(base: Dict[str, Any], other: Dict[str, Any],
                      match_reason: str = "unspecified") -> Dict[str, Any]:
    merged = dict(base)
    for key in set(base.keys()) | set(other.keys()):
        if key in _LIST_FIELDS:
            combined = list(base.get(key) or [])
            for item in (other.get(key) or []):
                if item not in combined:
                    combined.append(item)
            merged[key] = combined
        elif key in ("scientific_components", "youtube_components"):
            # Discovery-time components are always all-null; keep base's shape.
            merged[key] = base.get(key) or other.get(key)
        else:
            merged[key] = _prefer(base.get(key), other.get(key))

    other_sources = other.get("discovery_sources") or ["unknown source"]
    note = f"merged {other_sources} record into base via {match_reason} match"
    notes = list(base.get("deduplication_notes") or [])
    notes.append(note)
    merged["deduplication_notes"] = notes

    doi = merged.get("doi")
    pmid = merged.get("pmid")
    title = merged.get("exact_title")
    merged["id"] = make_candidate_id(doi, pmid, title)
    return merged


def _match_reason(a: Dict[str, Any], b: Dict[str, Any], title_threshold: float) -> Optional[str]:
    """Returns 'doi', 'pmid', or 'title' for the first matching rule (in
    that priority order), or None if nothing matches."""
    a_doi, b_doi = a.get("doi"), b.get("doi")
    if a_doi and b_doi:
        return "doi" if a_doi == b_doi else None

    a_pmid, b_pmid = a.get("pmid"), b.get("pmid")
    if a_pmid and b_pmid:
        return "pmid" if a_pmid == b_pmid else None

    a_title = normalize_title_for_matching(a.get("exact_title"))
    b_title = normalize_title_for_matching(b.get("exact_title"))
    if not a_title or not b_title:
        return None
    ratio = difflib.SequenceMatcher(None, a_title, b_title).ratio()
    return "title" if ratio >= title_threshold else None


def _deduplicate_core(
    records: List[Dict[str, Any]],
    title_similarity_threshold: float,
) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    clusters: List[Dict[str, Any]] = []
    audit = {"doi_merges": 0, "pmid_merges": 0, "title_merges": 0}

    for record in records:
        merged_into: Optional[int] = None
        reason: Optional[str] = None
        for idx, cluster in enumerate(clusters):
            reason = _match_reason(cluster, record, title_similarity_threshold)
            if reason:
                merged_into = idx
                break
        if merged_into is None:
            clusters.append(dict(record))
        else:
            clusters[merged_into] = merge_candidates(clusters[merged_into], record, match_reason=reason)
            audit[f"{reason}_merges"] += 1

    return clusters, audit


def deduplicate(records: List[Dict[str, Any]],
                 title_similarity_threshold: float = 0.92) -> List[Dict[str, Any]]:
    """Merges duplicate candidates. Order of `records` matters as a
    tie-breaker: earlier records act as the merge base, so run PubMed
    records through before Crossref records to prefer PubMed's richer
    abstract/MeSH metadata when both sources agree on a field."""
    clusters, _audit = _deduplicate_core(records, title_similarity_threshold)
    return clusters


def deduplicate_with_audit(
    records: List[Dict[str, Any]],
    title_similarity_threshold: float = 0.92,
) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """Same as deduplicate(), but also returns an audit dict:
    {'doi_merges': N, 'pmid_merges': N, 'title_merges': N}."""
    return _deduplicate_core(records, title_similarity_threshold)
