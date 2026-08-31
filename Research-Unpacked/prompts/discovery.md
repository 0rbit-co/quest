# Discovery Prompt (V1 draft)

Purpose: turn news/press-release/RSS/search leads into `research/inbox/`
entries. This prompt is used by a human or an AI assistant manually in V1 —
no automation is wired up yet.

**Discovery must never assign `verification_status: GREEN`.** Its job is to
surface candidates and capture *why they might matter now*, not to confirm
the science.

## Instructions to the model

You are scanning discovery-tier sources (news articles, university press
releases, RSS feeds, search results) for newly published scientific studies
that could become Research Unpacked videos.

For each candidate, capture only what the discovery source actually states:

1. `exact_title` — the study/paper title as reported (may be the news
   headline's rendering of it — flag if not a direct paper title).
2. `original_url` — link to the paper if the discovery source provides one
   directly (DOI, publisher page, PubMed); otherwise leave `null` and record
   the news/press-release URL in `verification_notes` instead.
3. `journal`, `publication_date` — as reported, marked `provisional` if the
   discovery source doesn't cite them precisely.
4. `why_now` — one or two sentences on why this is timely (news hook, viral
   moment, seasonal relevance).
5. `media_date` — date the discovery source (news/press release) was
   published.

Do **not**:

- Assign `verification_status`. Leave it unset or `null` — verification is a
  separate step against a primary source (see `prompts/verification.md`).
- Assign any scientific or YouTube component scores.
- Invent a DOI, PMID, sample size, or effect size that the discovery source
  didn't state. Use `null` and add the field to `provisional_fields`.

Output one JSON object per candidate, conforming to
`schemas/study.schema.json`, with `verification_status` omitted or `null`
and all scoring fields `null`. Save to `research/inbox/`.
