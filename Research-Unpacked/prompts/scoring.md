# Scoring Prompt (V1 draft)

Purpose: assign the raw component scores defined in
`config/scoring_rules.md`. This prompt produces the *inputs* to the
deterministic model — it never computes totals, tiers, or priorities itself.

## Instructions to the model

You are scoring a study that already has `verification_status` set (from
`prompts/verification.md`). Score only the raw components below, each as an
integer within its stated bound. Do not compute sums, tiers, or priorities —
`scripts/validate_study.py` does that, and will `FAIL` the file if your
totals disagree with the recalculated ones.

### Scientific Evidence components (see `config/scoring_rules.md` §1)

- `study_design_quality` (0–15)
- `sample_strength` (0–10)
- `outcome_quality` (0–8)
- `statistical_robustness` (0–7)
- `replication_consistency` (0–5)
- `limitations_bias_risk` (0–5)

### YouTube Potential components (see `config/scoring_rules.md` §2)

- `audience_relevance` (0–10)
- `curiosity_surprise` (0–10)
- `human_consequence` (0–8)
- `visual_storytelling` (0–7)
- `timeliness` (0–5)
- `title_thumbnail_potential` (0–5)
- `practical_emotional_relevance` (0–5)

### Headline defensibility constraint

If `headline_defensibility == "RED"`, `title_thumbnail_potential` must be
`<= 2`. Do not score above that ceiling for a RED headline — the validator
will reject the file if you do.

### Editorial fields (not scores)

Also propose, as drafts (these belong in `provisional_fields` unless you are
highly confident):

- `proposed_title`
- `thumbnail_text`
- `best_video_angle`

## After scoring

Leave `scientific_score`, `youtube_score`, `final_radar_score`,
`evidence_tier`, `content_priority`, `production_priority`, and
`validation_status` for the validator to fill in / verify. If you do write
them yourself, they are treated as a claim, not a fact — run
`python3 scripts/validate_study.py <file>` before moving the record into
`research/verified/`.
