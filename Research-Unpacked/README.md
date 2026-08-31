# Research Unpacked — Research Radar V1

Research Unpacked turns freshly published scientific studies into a ranked,
defensible pipeline of video-worthy stories. This is the **V1 local
architecture**: project structure, configuration, schema, and deterministic
validation. It does **not** include web scraping, API polling, or scheduled
automation — those are Stage 2.

## Pipeline (conceptual)

```
Discovery            Verification           Scoring              Radar
(news, press,   ->   (primary source   ->   (locked rubric,  ->  (deterministic
 RSS, search)         is source of           50 + 50 pts)         rank + report)
                      truth)
```

```
research/inbox/       raw discovery leads, no verification claims yet
research/candidates/  leads being checked against the primary paper
research/verified/    fully verified + scored study records (validator input)
research/rejected/    RED / disqualified studies, kept for audit trail
reports/              generated Radar markdown reports
videos/               downstream production folders (ideas, scripts, published)
```

## Why a deterministic validator?

Scores, tiers, and priorities in this system are the output of arithmetic and
threshold rules — not judgment calls. An AI assistant (or a human) can make an
arithmetic slip, mislabel a tier, or let a weak headline slip through. This
project treats every AI-produced study record as **untrusted input**:

- `scripts/validate_study.py` recalculates every score, tier, and priority
  from the raw component numbers and compares the result to what's stored in
  the file. Any mismatch is a hard `FAIL` — nothing is silently corrected.
- `scripts/build_radar.py` only builds the Radar report from studies that
  pass validation, are `GREEN`, and fall inside the active research window.
  It never pads the list to reach a round number.

## Directory map

| Path | Purpose |
|---|---|
| `config/verification_rules.md` | Locked rules for GREEN / YELLOW / RED verification |
| `config/scoring_rules.md` | Locked 50+50 scoring model, tiers, priorities |
| `config/sources.md` | Discovery vs. verification source policy |
| `config/research_window.json` | The active publication window used for ranking eligibility |
| `schemas/study.schema.json` | JSON Schema for a study record |
| `prompts/` | Prompt templates used in the discovery/verification/scoring phases |
| `scripts/validate_study.py` | Deterministic recalculation + validation of one study file |
| `scripts/build_radar.py` | Builds `reports/` from `research/verified/` |
| `tests/test_scoring.py` | Unit tests locking in the scoring/eligibility rules |

## Running V1

```bash
# Validate a single study file
python3 scripts/validate_study.py research/verified/depression-hippocampal-neurogenesis.json

# Validate every study in research/verified/
python3 scripts/validate_study.py research/verified/*.json

# Build the Radar report from research/verified/
python3 scripts/build_radar.py

# Run the test suite
python3 -m pytest tests/ -v
```

## Status

V1 (this step): structure, config, schema, deterministic scoring/eligibility
validation, report generation, seed data. **No scraping, no scheduling, no
network calls.** Stage 2 will add discovery automation on top of this
foundation without changing the locked verification or scoring rules.
