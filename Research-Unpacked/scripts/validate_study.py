#!/usr/bin/env python3
"""Deterministic validator for Research Radar study records.

This script is the single source of truth for scoring arithmetic and
classification. It NEVER trusts totals, tiers, or priorities written into a
study JSON file — it recalculates every one of them from the raw component
values and reports any disagreement as a hard FAIL. It never silently
corrects a file.

Usage:
    python3 validate_study.py [FILE ...]

With no arguments, validates every *.json file in research/verified/.
Exit code is 0 if every file PASSes, 1 otherwise.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_WINDOW_CONFIG = ROOT_DIR / "config" / "research_window.json"
DEFAULT_VERIFIED_DIR = ROOT_DIR / "research" / "verified"

# ---------------------------------------------------------------------------
# Locked scoring model (config/scoring_rules.md). Do not change these values
# as part of ordinary implementation work.
# ---------------------------------------------------------------------------

SCIENTIFIC_BOUNDS: Dict[str, int] = {
    "study_design_quality": 15,
    "sample_strength": 10,
    "outcome_quality": 8,
    "statistical_robustness": 7,
    "replication_consistency": 5,
    "limitations_bias_risk": 5,
}
SCIENTIFIC_MAX = sum(SCIENTIFIC_BOUNDS.values())  # 50

YOUTUBE_BOUNDS: Dict[str, int] = {
    "audience_relevance": 10,
    "curiosity_surprise": 10,
    "human_consequence": 8,
    "visual_storytelling": 7,
    "timeliness": 5,
    "title_thumbnail_potential": 5,
    "practical_emotional_relevance": 5,
}
YOUTUBE_MAX = sum(YOUTUBE_BOUNDS.values())  # 50

EVIDENCE_TIERS = [
    ("A", 42, 50),
    ("B", 34, 41),
    ("C", 25, 33),
    ("D", 0, 24),
]

CONTENT_PRIORITIES = [
    ("VERY_HIGH", 43, 50),
    ("HIGH", 36, 42),
    ("MEDIUM", 28, 35),
    ("LOW", 0, 27),
]

VALID_VERIFICATION_STATUSES = {"GREEN", "YELLOW", "RED"}
VALID_HEADLINE_STATUSES = {"GREEN", "YELLOW", "RED"}
HEADLINE_RED_TITLE_CAP = 2


# ---------------------------------------------------------------------------
# Pure derivation functions
# ---------------------------------------------------------------------------

def _is_clean_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def check_components(components: Any, bounds: Dict[str, int], label: str,
                      errors: List[str]) -> Optional[int]:
    """Validate a component dict against its bounds and return the sum, or
    None if any component is missing/invalid (in which case a score cannot
    be reliably calculated)."""
    if not isinstance(components, dict):
        errors.append(f"{label} must be an object, got {type(components).__name__}")
        return None

    complete = True
    total = 0
    for key, bound in bounds.items():
        if key not in components:
            errors.append(f"{label}.{key} is missing")
            complete = False
            continue
        value = components[key]
        if value is None:
            errors.append(f"{label}.{key} is null (not yet scored)")
            complete = False
            continue
        if not _is_clean_int(value):
            errors.append(f"{label}.{key} must be an integer, got {value!r}")
            complete = False
            continue
        if value < 0 or value > bound:
            errors.append(
                f"{label}.{key} = {value} is out of bounds [0, {bound}]"
            )
            complete = False
            continue
        total += value

    unexpected = set(components.keys()) - set(bounds.keys())
    if unexpected:
        errors.append(f"{label} has unexpected fields: {sorted(unexpected)}")
        complete = False

    return total if complete else None


def derive_evidence_tier(scientific_score: Optional[int]) -> Optional[str]:
    if scientific_score is None:
        return None
    for tier, low, high in EVIDENCE_TIERS:
        if low <= scientific_score <= high:
            return tier
    raise ValueError(f"scientific_score {scientific_score} out of range 0-50")


def derive_content_priority(youtube_score: Optional[int]) -> Optional[str]:
    if youtube_score is None:
        return None
    for priority, low, high in CONTENT_PRIORITIES:
        if low <= youtube_score <= high:
            return priority
    raise ValueError(f"youtube_score {youtube_score} out of range 0-50")


def derive_production_priority(evidence_tier: Optional[str],
                                content_priority: Optional[str]) -> Optional[str]:
    if evidence_tier is None or content_priority is None:
        return None
    if evidence_tier in ("A", "B") and content_priority == "VERY_HIGH":
        return "PRIORITY_1"
    if evidence_tier in ("A", "B") and content_priority == "HIGH":
        return "PRIORITY_2"
    if evidence_tier == "C" and content_priority == "VERY_HIGH":
        return "PRIORITY_3"
    return "NO_STANDARD_PRODUCTION_PRIORITY"


def load_window(window_path: Path = DEFAULT_WINDOW_CONFIG) -> Dict[str, str]:
    with open(window_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _parse_date(value: Optional[str]) -> Optional[_dt.date]:
    if not value:
        return None
    try:
        return _dt.date.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def is_inside_window(publication_date: Optional[str],
                      window: Dict[str, str]) -> bool:
    pub = _parse_date(publication_date)
    start = _parse_date(window.get("window_start"))
    end = _parse_date(window.get("window_end"))
    if pub is None or start is None or end is None:
        return False
    return start <= pub <= end


# ---------------------------------------------------------------------------
# Full study validation
# ---------------------------------------------------------------------------

@dataclass
class ValidationResult:
    study_id: Optional[str]
    passed: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    calculated: Dict[str, Any] = field(default_factory=dict)

    @property
    def status(self) -> str:
        return "PASS" if self.passed else "FAIL"


def validate_study(study: Dict[str, Any],
                    window: Optional[Dict[str, str]] = None) -> ValidationResult:
    errors: List[str] = []
    warnings: List[str] = []

    if window is None:
        window = load_window()

    study_id = study.get("id")

    # --- A/B: recalculate component sums, checking bounds (G) -------------
    calc_scientific = check_components(
        study.get("scientific_components"), SCIENTIFIC_BOUNDS,
        "scientific_components", errors,
    )
    calc_youtube = check_components(
        study.get("youtube_components"), YOUTUBE_BOUNDS,
        "youtube_components", errors,
    )

    # --- C: recalculate final radar score -----------------------------
    calc_final = (
        calc_scientific + calc_youtube
        if calc_scientific is not None and calc_youtube is not None
        else None
    )

    # --- D/E/F: derive tier / content priority / production priority ---
    calc_tier = derive_evidence_tier(calc_scientific)
    calc_content_priority = derive_content_priority(calc_youtube)
    calc_production_priority = derive_production_priority(
        calc_tier, calc_content_priority
    )

    # --- Compare stored values against recalculated values -------------
    def compare(field_name: str, calculated_value: Any) -> None:
        stored_value = study.get(field_name)
        if calculated_value is None:
            if stored_value is not None:
                errors.append(
                    f"{field_name} is stored as {stored_value!r} but cannot be "
                    "verified because required component scores are "
                    "missing/invalid (see errors above)"
                )
            return
        if stored_value != calculated_value:
            errors.append(
                f"{field_name} mismatch: stored={stored_value!r} "
                f"calculated={calculated_value!r}"
            )

    compare("scientific_score", calc_scientific)
    compare("youtube_score", calc_youtube)
    compare("final_radar_score", calc_final)
    compare("evidence_tier", calc_tier)
    compare("content_priority", calc_content_priority)
    compare("production_priority", calc_production_priority)

    # --- H: headline defensibility rule ---------------------------------
    headline_defensibility = study.get("headline_defensibility")
    if headline_defensibility not in VALID_HEADLINE_STATUSES:
        errors.append(
            f"headline_defensibility must be one of {sorted(VALID_HEADLINE_STATUSES)}, "
            f"got {headline_defensibility!r}"
        )
    youtube_components = study.get("youtube_components") or {}
    title_thumbnail_potential = youtube_components.get("title_thumbnail_potential")
    if (
        headline_defensibility == "RED"
        and isinstance(title_thumbnail_potential, int)
        and not isinstance(title_thumbnail_potential, bool)
        and title_thumbnail_potential > HEADLINE_RED_TITLE_CAP
    ):
        errors.append(
            "headline_defensibility is RED but youtube_components."
            f"title_thumbnail_potential = {title_thumbnail_potential} exceeds "
            f"the cap of {HEADLINE_RED_TITLE_CAP}"
        )

    # --- verification_status sanity ------------------------------------
    verification_status = study.get("verification_status")
    if verification_status not in VALID_VERIFICATION_STATUSES:
        errors.append(
            f"verification_status must be one of {sorted(VALID_VERIFICATION_STATUSES)}, "
            f"got {verification_status!r}"
        )

    # --- overall PASS/FAIL (J) ------------------------------------------
    passed = len(errors) == 0

    # --- stored validation_status is itself just a claim ----------------
    stored_validation_status = study.get("validation_status")
    computed_validation_status = "PASS" if passed else "FAIL"
    if stored_validation_status not in (None, "PENDING", computed_validation_status):
        warnings.append(
            f"validation_status stored as {stored_validation_status!r} but "
            f"recalculation determined {computed_validation_status!r}"
        )

    # --- I: ranking eligibility (computed, never trusted from the file) -
    publication_date = study.get("publication_date")
    inside_window = is_inside_window(publication_date, window)
    ranking_eligible = (
        verification_status == "GREEN"
        and inside_window
        and computed_validation_status == "PASS"
    )
    if verification_status == "GREEN" and not inside_window:
        warnings.append(
            "ranking_eligible is FALSE: publication_date "
            f"{publication_date!r} is not inside the active research window "
            f"[{window.get('window_start')}, {window.get('window_end')}]"
        )

    calculated = {
        "scientific_score": calc_scientific,
        "youtube_score": calc_youtube,
        "final_radar_score": calc_final,
        "evidence_tier": calc_tier,
        "content_priority": calc_content_priority,
        "production_priority": calc_production_priority,
        "validation_status": computed_validation_status,
        "ranking_eligible": ranking_eligible,
        "inside_window": inside_window,
    }

    return ValidationResult(
        study_id=study_id,
        passed=passed,
        errors=errors,
        warnings=warnings,
        calculated=calculated,
    )


def validate_file(path: Path,
                   window: Optional[Dict[str, str]] = None) -> ValidationResult:
    with open(path, "r", encoding="utf-8") as f:
        study = json.load(f)
    return validate_study(study, window=window)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _print_result(path: Path, result: ValidationResult) -> None:
    print(f"\n{path}")
    print(f"  id: {result.study_id}")
    print(f"  result: {result.status}")
    c = result.calculated
    print(
        f"  scientific_score={c['scientific_score']} "
        f"youtube_score={c['youtube_score']} "
        f"final_radar_score={c['final_radar_score']}"
    )
    print(
        f"  evidence_tier={c['evidence_tier']} "
        f"content_priority={c['content_priority']} "
        f"production_priority={c['production_priority']}"
    )
    print(f"  ranking_eligible={c['ranking_eligible']}")
    if result.errors:
        print("  errors:")
        for e in result.errors:
            print(f"    - {e}")
    if result.warnings:
        print("  warnings:")
        for w in result.warnings:
            print(f"    - {w}")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "files", nargs="*",
        help="Study JSON files to validate. Defaults to research/verified/*.json",
    )
    args = parser.parse_args(argv)

    if args.files:
        paths = [Path(p) for p in args.files]
    else:
        paths = sorted(DEFAULT_VERIFIED_DIR.glob("*.json"))

    if not paths:
        print("No study files found to validate.")
        return 0

    window = load_window()
    all_passed = True
    for path in paths:
        result = validate_file(path, window=window)
        _print_result(path, result)
        if not result.passed:
            all_passed = False

    print()
    print("=" * 60)
    print("ALL PASS" if all_passed else "AT LEAST ONE FILE FAILED")
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
