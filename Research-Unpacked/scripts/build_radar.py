#!/usr/bin/env python3
"""Build the Research Radar report from research/verified/.

Rules (locked, see config/scoring_rules.md and config/verification_rules.md):
  1. Every study is re-validated deterministically (validate_study.validate_study).
  2. Validation failures are excluded.
  3. YELLOW is excluded.
  4. RED is excluded.
  5. Studies whose publication_date falls outside the active research window
     are excluded.
  6. Remaining studies are ranked by final_radar_score, descending.
  7. The report NEVER pads the list to reach a round number (e.g. a "Top 10")
     — if 3 studies qualify, the report lists exactly 3.

Usage:
    python3 build_radar.py [--out PATH]
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.validate_study import (  # noqa: E402
    DEFAULT_VERIFIED_DIR,
    load_window,
    validate_study,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT_DIR / "reports"


def _load_all(verified_dir: Path) -> List[Dict[str, Any]]:
    studies = []
    for path in sorted(verified_dir.glob("*.json")):
        with open(path, "r", encoding="utf-8") as f:
            study = json.load(f)
        study["_source_path"] = str(path.relative_to(ROOT_DIR))
        studies.append(study)
    return studies


def build_eligible_pool(verified_dir: Path = DEFAULT_VERIFIED_DIR):
    """Returns (eligible_ranked, excluded) where excluded is a list of
    (study, reason) pairs for transparency."""
    window = load_window()
    studies = _load_all(verified_dir)

    eligible = []
    excluded = []

    for study in studies:
        result = validate_study(study, window=window)
        source = study.get("_source_path", study.get("id"))

        if not result.passed:
            excluded.append((study, result, f"validation FAILED ({source})"))
            continue

        verification_status = study.get("verification_status")
        if verification_status == "YELLOW":
            excluded.append((study, result, "verification_status is YELLOW"))
            continue
        if verification_status == "RED":
            excluded.append((study, result, "verification_status is RED"))
            continue

        if not result.calculated["inside_window"]:
            excluded.append(
                (study, result,
                 f"publication_date {study.get('publication_date')!r} is "
                 f"outside the active research window "
                 f"[{window['window_start']}, {window['window_end']}]")
            )
            continue

        eligible.append((study, result))

    eligible.sort(key=lambda pair: pair[1].calculated["final_radar_score"],
                   reverse=True)

    return eligible, excluded, window


def render_report(eligible, excluded, window) -> str:
    today = _dt.date.today().isoformat()
    lines: List[str] = []
    lines.append(f"# Research Radar — {today}")
    lines.append("")
    lines.append(
        f"Active research window: **{window['window_start']}** to "
        f"**{window['window_end']}** ({window.get('timezone', 'UTC')})"
    )
    lines.append("")
    lines.append(
        f"GREEN eligible pool: **{len(eligible)}** stud"
        f"{'y' if len(eligible) == 1 else 'ies'}. "
        "This report never pads the list to reach a round number — if fewer "
        "studies qualify, fewer are shown."
    )
    lines.append("")

    if not eligible:
        lines.append(
            "_No studies are currently ranking-eligible. A study becomes "
            "eligible only when verification_status is GREEN, "
            "publication_date falls inside the active research window, and "
            "deterministic validation PASSes._"
        )
        lines.append("")
    else:
        lines.append(
            "| Rank | Title | Sci. | YouTube | Final | Tier | Content Priority | "
            "Production Priority | Headline |"
        )
        lines.append(
            "|---|---|---|---|---|---|---|---|---|"
        )
        for rank, (study, result) in enumerate(eligible, start=1):
            c = result.calculated
            title = study.get("proposed_title") or study.get("exact_title") or study.get("id")
            lines.append(
                f"| {rank} | {title} | {c['scientific_score']} | "
                f"{c['youtube_score']} | {c['final_radar_score']} | "
                f"{c['evidence_tier']} | {c['content_priority']} | "
                f"{c['production_priority']} | {study.get('headline_defensibility')} |"
            )
        lines.append("")
        lines.append("## Detail")
        lines.append("")
        for rank, (study, result) in enumerate(eligible, start=1):
            c = result.calculated
            title = study.get("proposed_title") or study.get("exact_title") or study.get("id")
            lines.append(f"### {rank}. {title}")
            lines.append("")
            lines.append(f"- **id**: `{study.get('id')}`")
            lines.append(
                f"- **Scientific score**: {c['scientific_score']}/50  "
                f"**YouTube score**: {c['youtube_score']}/50  "
                f"**Final radar score**: {c['final_radar_score']}/100"
            )
            lines.append(
                f"- **Evidence tier**: {c['evidence_tier']}  "
                f"**Content priority**: {c['content_priority']}  "
                f"**Production priority**: {c['production_priority']}"
            )
            lines.append(f"- **Headline defensibility**: {study.get('headline_defensibility')}")
            lines.append(f"- **Proposed title**: {study.get('proposed_title') or '_none_'}")
            lines.append(f"- **Thumbnail text**: {study.get('thumbnail_text') or '_none_'}")
            lines.append(f"- **Why now**: {study.get('why_now') or '_none_'}")
            lines.append("")

    if excluded:
        lines.append("## Excluded from this Radar")
        lines.append("")
        lines.append("| id | reason |")
        lines.append("|---|---|")
        for study, result, reason in excluded:
            lines.append(f"| `{study.get('id')}` | {reason} |")
        lines.append("")

    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verified-dir", type=Path, default=DEFAULT_VERIFIED_DIR,
        help="Directory of study JSON files (default: research/verified/)",
    )
    parser.add_argument(
        "--out", type=Path, default=None,
        help="Output report path (default: reports/radar-<date>.md)",
    )
    args = parser.parse_args(argv)

    eligible, excluded, window = build_eligible_pool(args.verified_dir)
    report = render_report(eligible, excluded, window)

    out_path = args.out or (REPORTS_DIR / f"radar-{_dt.date.today().isoformat()}.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")

    print(report)
    print(f"\nWritten to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
