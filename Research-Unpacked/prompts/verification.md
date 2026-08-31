# Verification Prompt (V1 draft)

Purpose: move a candidate from `research/candidates/` to a
`verification_status` decision (`GREEN` / `YELLOW` / `RED`), by checking it
against a primary-tier source (see `config/sources.md`).

## Instructions to the model

You are verifying a candidate study record against its **primary research
source** — the peer-reviewed paper itself, its DOI record, PubMed entry, or
(explicitly labeled) preprint. A news article or press release is not a
valid source for this step, even if it is the only thing you have access to
— if you cannot reach a primary source, the correct output is `YELLOW`, not
a guess.

For each candidate:

1. Locate the primary source (`original_url`, `doi`, or `pmid`).
2. Check that `exact_title`, `journal`, `publication_date`, `study_design`,
   `sample_size`, `population`, `primary_outcome`, `main_result`,
   `effect_size`, `confidence_interval`, and `p_value` match what the paper
   actually reports. Correct any field that the discovery step got wrong.
3. Record `major_limitations` as stated by the authors (not your own
   opinion of the study).
4. Record `funding` and `conflicts_of_interest` if disclosed in the paper.
5. Write `verification_notes` describing exactly what you checked and
   against which source (e.g. "Checked abstract + methods + results against
   DOI 10.xxxx/xxxxx; press release's stated effect size matches Table 2").
6. Set `verification_status`:
   - `GREEN` — claims are traceable to the primary source.
   - `YELLOW` — primary source not accessible, or verification incomplete/
     ambiguous.
   - `RED` — primary source contradicts the claim, is retracted, or is not
     a primary research paper.
7. Assess `headline_defensibility` (`GREEN`/`YELLOW`/`RED`) for the
   currently `proposed_title` — independent of `verification_status`. A
   sensationalized headline on a solid `GREEN` study is still
   `headline_defensibility: RED`.

Do **not** assign scientific or YouTube component scores here — that is a
separate step (`prompts/scoring.md`). Do not compute `scientific_score`,
`youtube_score`, `final_radar_score`, `evidence_tier`, `content_priority`,
or `production_priority` — those are only ever produced by
`scripts/validate_study.py`.

If any fact cannot be confirmed from the primary source, set it to `null`
and add its field name to `provisional_fields` rather than guessing.
