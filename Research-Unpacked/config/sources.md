# Source Policy

Defines which kinds of sources are permitted at each pipeline stage. This is
policy/config for V1 — no scraping or API integration is implemented yet
(that is Stage 2). This file governs how Stage 2 sources will eventually be
classified once they're built.

## Discovery-tier sources (allowed to surface candidates only)

These may populate `research/inbox/` and inform `content_priority` /
`why_now`, but **must never** be the basis for `verification_status ==
GREEN`:

- News articles / science journalism
- University or institutional press releases
- RSS feeds from journals, preprint servers, or aggregators
- General web search results
- Social media mentions (signal for timeliness/curiosity only)

## Primary/verification-tier sources (required for GREEN)

At least one of these must be directly checked before a study can be marked
`GREEN`:

- The peer-reviewed journal article itself (publisher page or PDF)
- The DOI resolver record (https://doi.org/...) pointing to the above
- PubMed / PubMed Central (PMID/PMCID) record
- A preprint server entry (e.g. medRxiv, bioRxiv), explicitly noted as a
  preprint in `verification_notes` — preprints should be weighted
  conservatively in `replication_consistency` and `limitations_bias_risk`

A source that merely *describes* the paper (news article, press release,
blog summary) is never sufficient by itself, even if it quotes the paper
directly.

## Active research window

The "selected research window" referenced in the verification and scoring
rules is configured in `config/research_window.json` (machine-readable, used
by `scripts/validate_study.py` and `scripts/build_radar.py`). Update that
file to move the window forward; this document records the *policy*, not the
current dates.

## Stage 2 (not yet built)

Automated discovery (scraping, RSS polling, scheduled search) will populate
`research/inbox/` programmatically in a later stage. It will still be
subject to the same rule above: automation may only ever produce
`YELLOW`/candidate records. Promotion to `GREEN` still requires a primary
source check, whether performed by a human or an explicit verification step
against a primary-tier source.
