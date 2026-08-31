# Scoring Rules (LOCKED)

This is the locked Research Radar scoring model. Component weights, tier
boundaries, and priority rules must not change as part of building the local
architecture. `scripts/validate_study.py` is the single source of truth for
recalculating these values — this document and the JSON schema describe the
same rules the code enforces.

## 1. Scientific Evidence — 50 points

| Component | Max |
|---|---|
| `study_design_quality` | 15 |
| `sample_strength` | 10 |
| `outcome_quality` | 8 |
| `statistical_robustness` | 7 |
| `replication_consistency` | 5 |
| `limitations_bias_risk` | 5 |
| **`scientific_score`** | **50** |

`scientific_score = study_design_quality + sample_strength + outcome_quality
+ statistical_robustness + replication_consistency + limitations_bias_risk`

## 2. YouTube Potential — 50 points

| Component | Max |
|---|---|
| `audience_relevance` | 10 |
| `curiosity_surprise` | 10 |
| `human_consequence` | 8 |
| `visual_storytelling` | 7 |
| `timeliness` | 5 |
| `title_thumbnail_potential` | 5 |
| `practical_emotional_relevance` | 5 |
| **`youtube_score`** | **50** |

`youtube_score = audience_relevance + curiosity_surprise + human_consequence
+ visual_storytelling + timeliness + title_thumbnail_potential +
practical_emotional_relevance`

## 3. Final Radar Score

`final_radar_score = scientific_score + youtube_score` (max 100)

## 4. Evidence Tier — derived from `scientific_score` (0–50)

| Tier | Range |
|---|---|
| A | 42–50 |
| B | 34–41 |
| C | 25–33 |
| D | below 25 |

## 5. Content Priority — derived from `youtube_score` (0–50)

| Priority | Range |
|---|---|
| VERY_HIGH | 43–50 |
| HIGH | 36–42 |
| MEDIUM | 28–35 |
| LOW | below 28 |

## 6. Production Priority — derived from Evidence Tier + Content Priority

| Production Priority | Condition |
|---|---|
| `PRIORITY_1` | Tier A or B **and** Content Priority VERY_HIGH |
| `PRIORITY_2` | Tier A or B **and** Content Priority HIGH |
| `PRIORITY_3` | Tier C **and** Content Priority VERY_HIGH |
| `NO_STANDARD_PRODUCTION_PRIORITY` | anything else |

**Tier D is not recommended for normal videos.** Tier D studies may still be
considered for editorial/debunking formats, e.g.:

- "Why this headline is misleading"
- "Why this study does not prove what people think"

These editorial formats are a distinct production track from the standard
Priority 1/2/3 pipeline and are never assigned a standard production
priority.

## 7. Headline Defensibility

`headline_defensibility` is one of `GREEN` / `YELLOW` / `RED`, independent of
`verification_status` — it grades whether the *proposed video headline* is
defensible given the study's actual findings, not whether the study itself
is trustworthy.

**Rule:** a `RED` proposed headline must not be allowed to score above 2 on
`title_thumbnail_potential`.

The validator must reject (`FAIL`) a study file if:

```
headline_defensibility == "RED" AND title_thumbnail_potential > 2
```

## 8. Ranking Eligibility

A study is `ranking_eligible` only if **all** of the following hold:

1. `verification_status == "GREEN"`
2. `publication_date` falls inside the active research window
   (`config/research_window.json`)
3. `validation_status == "PASS"` (i.e. the deterministic validator found no
   discrepancies)

`YELLOW` and `RED` studies are never ranking-eligible, regardless of score.

## 9. Determinism requirement

All of `scientific_score`, `youtube_score`, `final_radar_score`,
`evidence_tier`, `content_priority`, and `production_priority` **must be
recalculated by `scripts/validate_study.py` from the raw component values**.
Stored totals/classifications in a study JSON file are treated as claims to
verify, never as trusted input. Any disagreement between a stored value and
the recalculated value is a validation `FAIL`, reported explicitly — the
validator never silently corrects the file.
