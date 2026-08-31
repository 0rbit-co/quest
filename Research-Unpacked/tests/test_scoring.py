"""Tests locking in the Research Radar scoring/eligibility rules.

These tests exercise scripts/validate_study.py directly so that any future
change to the locked scoring model (config/scoring_rules.md) that breaks
these expectations is caught immediately.
"""
from __future__ import annotations

import copy

import pytest

from scripts.validate_study import (
    SCIENTIFIC_BOUNDS,
    YOUTUBE_BOUNDS,
    derive_content_priority,
    derive_evidence_tier,
    derive_production_priority,
    validate_study,
)

WINDOW = {"window_start": "2026-07-01", "window_end": "2026-08-31"}


def distribute(total: int, bounds: dict) -> dict:
    """Greedily fill components (in declared order) up to `total` points,
    respecting each component's max bound. Used only to build synthetic
    fixtures with a known, correct sum for testing."""
    remaining = total
    result = {}
    for key, bound in bounds.items():
        take = min(bound, remaining)
        result[key] = take
        remaining -= take
    if remaining != 0:
        raise ValueError(f"cannot distribute {total} points within bounds")
    return result


def base_study(**overrides) -> dict:
    scientific_total = overrides.pop("scientific_total", 37)
    youtube_total = overrides.pop("youtube_total", 45)

    scientific_components = distribute(scientific_total, SCIENTIFIC_BOUNDS)
    youtube_components = distribute(youtube_total, YOUTUBE_BOUNDS)

    scientific_score = sum(scientific_components.values())
    youtube_score = sum(youtube_components.values())
    final_radar_score = scientific_score + youtube_score
    evidence_tier = derive_evidence_tier(scientific_score)
    content_priority = derive_content_priority(youtube_score)
    production_priority = derive_production_priority(evidence_tier, content_priority)

    study = {
        "id": "test-study",
        "verification_status": "GREEN",
        "publication_date": "2026-07-15",
        "scientific_components": scientific_components,
        "youtube_components": youtube_components,
        "headline_defensibility": "GREEN",
        "scientific_score": scientific_score,
        "youtube_score": youtube_score,
        "final_radar_score": final_radar_score,
        "evidence_tier": evidence_tier,
        "content_priority": content_priority,
        "production_priority": production_priority,
        "validation_status": "PENDING",
    }
    study.update(overrides)
    return study


# ---------------------------------------------------------------------------
# Case 1: 37 scientific + 45 YouTube = 82 -> Tier B, VERY_HIGH, PRIORITY_1
# ---------------------------------------------------------------------------

def test_case_37_45_tier_b_very_high_priority_1():
    study = base_study(scientific_total=37, youtube_total=45)
    result = validate_study(study, window=WINDOW)

    assert result.passed, result.errors
    c = result.calculated
    assert c["scientific_score"] == 37
    assert c["youtube_score"] == 45
    assert c["final_radar_score"] == 82
    assert c["evidence_tier"] == "B"
    assert c["content_priority"] == "VERY_HIGH"
    assert c["production_priority"] == "PRIORITY_1"


# ---------------------------------------------------------------------------
# Case 2: 38 + 42 = 80 -> Tier B, HIGH, PRIORITY_2
# ---------------------------------------------------------------------------

def test_case_38_42_tier_b_high_priority_2():
    study = base_study(scientific_total=38, youtube_total=42)
    result = validate_study(study, window=WINDOW)

    assert result.passed, result.errors
    c = result.calculated
    assert c["scientific_score"] == 38
    assert c["youtube_score"] == 42
    assert c["final_radar_score"] == 80
    assert c["evidence_tier"] == "B"
    assert c["content_priority"] == "HIGH"
    assert c["production_priority"] == "PRIORITY_2"


# ---------------------------------------------------------------------------
# Case 3: 30 + 38 = 68 -> Tier C, HIGH, NO_STANDARD_PRODUCTION_PRIORITY
# ---------------------------------------------------------------------------

def test_case_30_38_tier_c_high_no_standard_priority():
    study = base_study(scientific_total=30, youtube_total=38)
    result = validate_study(study, window=WINDOW)

    assert result.passed, result.errors
    c = result.calculated
    assert c["scientific_score"] == 30
    assert c["youtube_score"] == 38
    assert c["final_radar_score"] == 68
    assert c["evidence_tier"] == "C"
    assert c["content_priority"] == "HIGH"
    assert c["production_priority"] == "NO_STANDARD_PRODUCTION_PRIORITY"


# ---------------------------------------------------------------------------
# Headline defensibility: RED headline + title_thumbnail_potential > 2 -> FAIL
# ---------------------------------------------------------------------------

def test_red_headline_with_title_score_above_cap_fails():
    study = base_study(scientific_total=37, youtube_total=45)
    # distribute(45, YOUTUBE_BOUNDS) fills title_thumbnail_potential to 5
    assert study["youtube_components"]["title_thumbnail_potential"] == 5
    study["headline_defensibility"] = "RED"

    result = validate_study(study, window=WINDOW)

    assert not result.passed
    assert any("headline_defensibility is RED" in e for e in result.errors)


def test_red_headline_with_title_score_at_cap_is_allowed():
    study = base_study(scientific_total=37, youtube_total=40)
    study["youtube_components"]["title_thumbnail_potential"] = 2
    # keep total consistent after editing the component directly
    study["youtube_score"] = sum(study["youtube_components"].values())
    study["final_radar_score"] = study["scientific_score"] + study["youtube_score"]
    study["content_priority"] = derive_content_priority(study["youtube_score"])
    study["production_priority"] = derive_production_priority(
        study["evidence_tier"], study["content_priority"]
    )
    study["headline_defensibility"] = "RED"

    result = validate_study(study, window=WINDOW)

    assert result.passed, result.errors


# ---------------------------------------------------------------------------
# YELLOW verification -> ranking_eligible FALSE (even if otherwise valid)
# ---------------------------------------------------------------------------

def test_yellow_verification_is_not_ranking_eligible():
    study = base_study(verification_status="YELLOW")
    result = validate_study(study, window=WINDOW)

    assert result.passed, result.errors
    assert result.calculated["ranking_eligible"] is False


# ---------------------------------------------------------------------------
# GREEN but outside the active window -> ranking_eligible FALSE
# ---------------------------------------------------------------------------

def test_green_outside_window_is_not_ranking_eligible():
    study = base_study(verification_status="GREEN", publication_date="2020-01-01")
    result = validate_study(study, window=WINDOW)

    assert result.passed, result.errors
    assert result.calculated["ranking_eligible"] is False


def test_green_inside_window_is_ranking_eligible():
    study = base_study(verification_status="GREEN", publication_date="2026-07-15")
    result = validate_study(study, window=WINDOW)

    assert result.passed, result.errors
    assert result.calculated["ranking_eligible"] is True


# ---------------------------------------------------------------------------
# Wrong manually stored total -> validation FAIL, reported not corrected
# ---------------------------------------------------------------------------

def test_wrong_manually_stored_total_fails_and_is_not_silently_corrected():
    study = base_study(scientific_total=37, youtube_total=45)
    original = copy.deepcopy(study)
    study["final_radar_score"] = 999  # deliberately wrong

    result = validate_study(study, window=WINDOW)

    assert not result.passed
    assert any("final_radar_score mismatch" in e for e in result.errors)
    # the validator must not mutate the input in place
    assert study["final_radar_score"] == 999
    assert original["final_radar_score"] != 999


def test_wrong_stored_evidence_tier_fails():
    study = base_study(scientific_total=37, youtube_total=45)
    study["evidence_tier"] = "A"  # actually B for scientific_score=37

    result = validate_study(study, window=WINDOW)

    assert not result.passed
    assert any("evidence_tier mismatch" in e for e in result.errors)


# ---------------------------------------------------------------------------
# Component bound enforcement
# ---------------------------------------------------------------------------

def test_component_exceeding_its_bound_fails():
    study = base_study(scientific_total=37, youtube_total=45)
    study["scientific_components"]["study_design_quality"] = 16  # max is 15

    result = validate_study(study, window=WINDOW)

    assert not result.passed
    assert any(
        "study_design_quality" in e and "out of bounds" in e for e in result.errors
    )


def test_missing_component_fails_and_reports_incomplete():
    study = base_study(scientific_total=37, youtube_total=45)
    del study["scientific_components"]["sample_strength"]

    result = validate_study(study, window=WINDOW)

    assert not result.passed
    assert result.calculated["scientific_score"] is None
    assert any("sample_strength is missing" in e for e in result.errors)


# ---------------------------------------------------------------------------
# Pure derivation function boundary checks (Tier / Content Priority tables)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "score,expected_tier",
    [(50, "A"), (42, "A"), (41, "B"), (34, "B"), (33, "C"), (25, "C"), (24, "D"), (0, "D")],
)
def test_evidence_tier_boundaries(score, expected_tier):
    assert derive_evidence_tier(score) == expected_tier


@pytest.mark.parametrize(
    "score,expected_priority",
    [
        (50, "VERY_HIGH"), (43, "VERY_HIGH"),
        (42, "HIGH"), (36, "HIGH"),
        (35, "MEDIUM"), (28, "MEDIUM"),
        (27, "LOW"), (0, "LOW"),
    ],
)
def test_content_priority_boundaries(score, expected_priority):
    assert derive_content_priority(score) == expected_priority
