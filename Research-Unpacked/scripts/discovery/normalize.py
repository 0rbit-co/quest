"""Normalizes raw PubMed/Crossref records into one candidate format.

Every candidate produced here is verification_status=YELLOW,
ranking_eligible=False, with null scoring fields — discovery never
verifies or scores anything (see config/verification_rules.md,
config/scoring_rules.md, both locked and untouched by this stage).
"""
from __future__ import annotations

import hashlib
import html
import re
from typing import Any, Dict, List, Optional

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.validate_study import SCIENTIFIC_BOUNDS, YOUTUBE_BOUNDS  # noqa: E402

DISCOVERY_VERIFICATION_NOTES = "Discovery metadata only. Primary-source verification required."

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def normalize_doi(doi: Optional[str]) -> Optional[str]:
    if not doi:
        return None
    d = doi.strip()
    d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d, flags=re.IGNORECASE)
    d = re.sub(r"^doi:\s*", "", d, flags=re.IGNORECASE)
    d = d.strip().strip(".").lower()
    return d or None


def normalize_title_for_matching(title: Optional[str]) -> str:
    if not title:
        return ""
    t = html.unescape(title)
    t = _TAG_RE.sub(" ", t)
    t = re.sub(r"[^a-z0-9\s]", " ", t.lower())
    t = _WS_RE.sub(" ", t).strip()
    return t


def _strip_jats(text: Optional[str]) -> Optional[str]:
    if not text:
        return None
    cleaned = html.unescape(_TAG_RE.sub(" ", text))
    cleaned = _WS_RE.sub(" ", cleaned).strip()
    return cleaned or None


def make_candidate_id(doi: Optional[str], pmid: Optional[str], title: Optional[str]) -> str:
    if doi:
        slug = re.sub(r"[^a-z0-9]+", "-", doi.lower()).strip("-")
        return f"doi-{slug}"
    if pmid:
        return f"pmid-{pmid}"
    basis = normalize_title_for_matching(title) or "untitled"
    slug = re.sub(r"\s+", "-", basis)[:60].strip("-") or "untitled"
    digest = hashlib.sha1(basis.encode("utf-8")).hexdigest()[:8]
    return f"title-{slug}-{digest}"


def _empty_components(bounds: Dict[str, int]) -> Dict[str, None]:
    return {key: None for key in bounds}


def _base_candidate(discovered_at: str) -> Dict[str, Any]:
    return {
        "discovered_at": discovered_at,
        "verification_status": "YELLOW",
        "verification_notes": DISCOVERY_VERIFICATION_NOTES,
        "ranking_eligible": False,
        "scientific_components": _empty_components(SCIENTIFIC_BOUNDS),
        "youtube_components": _empty_components(YOUTUBE_BOUNDS),
        "scientific_score": None,
        "youtube_score": None,
        "final_radar_score": None,
        "evidence_tier": None,
        "content_priority": None,
        "production_priority": None,
        "headline_defensibility": None,
        "proposed_title": None,
        "thumbnail_text": None,
        "best_video_angle": None,
        "validation_status": "PENDING",
        "discovery_filter_status": None,
        "discovery_filter_reason": None,
        "deduplication_notes": [],
    }


def normalize_pubmed_record(raw: Dict[str, Any], discovered_at: str) -> Dict[str, Any]:
    doi = normalize_doi(raw.get("doi"))
    pmid = raw.get("pmid")
    title = raw.get("title")

    candidate = _base_candidate(discovered_at)
    publication_types = list(raw.get("publication_types") or [])
    candidate.update({
        "id": make_candidate_id(doi, pmid, title),
        "discovery_sources": ["PUBMED"],
        "exact_title": title,
        "journal": raw.get("journal"),
        "publication_date": raw.get("publication_date"),
        "doi": doi,
        "pmid": pmid,
        "original_url": raw.get("original_url"),
        "publication_status": publication_types[0] if publication_types else None,
        "publication_types": publication_types,
        "abstract": raw.get("abstract"),
        "authors": list(raw.get("authors") or []),
        "mesh_terms": list(raw.get("mesh_terms") or []),
        "publisher": None,
    })
    candidate["provisional_fields"] = _provisional_fields(candidate)
    return candidate


def _crossref_date(work: Dict[str, Any]) -> Optional[str]:
    for key in ("published", "published-print", "published-online"):
        parts = (work.get(key) or {}).get("date-parts")
        if parts and parts[0]:
            p = parts[0]
            year = p[0] if len(p) > 0 else None
            month = p[1] if len(p) > 1 else 1
            day = p[2] if len(p) > 2 else 1
            if year:
                try:
                    return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
                except (ValueError, TypeError):
                    continue
    return None


def _crossref_authors(work: Dict[str, Any]) -> List[str]:
    authors = []
    for a in work.get("author") or []:
        family = a.get("family")
        given = a.get("given")
        if family:
            authors.append(f"{family} {given}" if given else family)
        elif a.get("name"):
            authors.append(a["name"])
    return authors


def normalize_crossref_record(raw: Dict[str, Any], discovered_at: str) -> Dict[str, Any]:
    doi = normalize_doi(raw.get("DOI"))
    title_list = raw.get("title") or []
    title = title_list[0] if title_list else None
    container = raw.get("container-title") or []
    journal = container[0] if container else None
    work_type = raw.get("type")

    candidate = _base_candidate(discovered_at)
    candidate.update({
        "id": make_candidate_id(doi, None, title),
        "discovery_sources": ["CROSSREF"],
        "exact_title": title,
        "journal": journal,
        "publication_date": _crossref_date(raw),
        "doi": doi,
        "pmid": None,
        "original_url": raw.get("URL"),
        "publication_status": work_type,
        "publication_types": [work_type] if work_type else [],
        "abstract": _strip_jats(raw.get("abstract")),
        "authors": _crossref_authors(raw),
        "mesh_terms": [],
        "publisher": raw.get("publisher"),
    })
    candidate["provisional_fields"] = _provisional_fields(candidate)
    return candidate


_OPTIONAL_BIBLIOGRAPHIC_FIELDS = (
    "journal", "publication_date", "doi", "pmid", "original_url",
    "publication_status", "abstract",
)


def _provisional_fields(candidate: Dict[str, Any]) -> List[str]:
    fields = [f for f in _OPTIONAL_BIBLIOGRAPHIC_FIELDS if not candidate.get(f)]
    fields += [
        "scientific_components", "youtube_components", "headline_defensibility",
        "proposed_title", "thumbnail_text", "best_video_angle",
    ]
    return fields


# ---------------------------------------------------------------------------
# Fast discovery filter (section 7): conservative reject of obvious
# non-target publication types. Never rejects on uncertainty.
# ---------------------------------------------------------------------------

def apply_fast_filter(candidate: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Sets discovery_filter_status ('kept'/'rejected') and
    discovery_filter_reason on the candidate (mutated in place, also
    returned). Never changes verification_status — rejection here is a
    discovery-stage triage decision, not a verification decision."""
    reject_terms = [t.lower() for t in config.get("reject_publication_types", [])]
    types_text = " ".join(candidate.get("publication_types") or []).lower()

    if types_text:
        for term in reject_terms:
            if term in types_text:
                candidate["discovery_filter_status"] = "rejected"
                candidate["discovery_filter_reason"] = (
                    f"publication type matches reject term '{term}' "
                    f"(reported type(s): {candidate.get('publication_types')})"
                )
                return candidate

    mesh_terms = {m.lower() for m in candidate.get("mesh_terms") or []}
    if mesh_terms and "animals" in mesh_terms and "humans" not in mesh_terms:
        candidate["discovery_filter_status"] = "rejected"
        candidate["discovery_filter_reason"] = (
            "MeSH terms include 'Animals' without 'Humans' — identifiable as animal-only"
        )
        return candidate

    candidate["discovery_filter_status"] = "kept"
    candidate["discovery_filter_reason"] = (
        "no reject criteria matched; kept conservatively as YELLOW"
        if not types_text and not mesh_terms
        else "no reject criteria matched"
    )
    return candidate
