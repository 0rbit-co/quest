# Verification Rules (LOCKED)

These rules are locked for V1. They must not be changed as part of building
the local architecture. Any future change requires an explicit decision
outside of implementation work.

## Core principle

> **ORIGINAL RESEARCH PAPER = SOURCE OF TRUTH**

Discovery sources (news articles, university press releases, RSS feeds,
search results) are allowed to *surface* a candidate study. They are never
allowed to *verify* one.

- **Discovery sources** (news, press releases, RSS, search results) may be
  used to find candidates and to gauge public interest / timeliness. They
  populate `research/inbox/` and `research/candidates/`.
- **Verification** must trace every scientific claim back to the primary
  research artifact: the peer-reviewed paper, its DOI record, or (for
  preprints) the preprint server entry, explicitly labeled as a preprint.
  A press release's paraphrase of a result is never sufficient on its own.

## Verification statuses

| Status | Meaning |
|---|---|
| `GREEN` | The primary paper has been located and read (or its abstract/methods/results directly checked), and the claims in the study record are traceable to it. |
| `YELLOW` | The study is plausible and of interest, but verification against the primary paper is incomplete, ambiguous, or not yet possible (e.g. paper not yet accessible, embargoed, or claims partially unconfirmed). |
| `RED` | Verification failed: the primary paper contradicts the claim, cannot be found, has been retracted, or the "study" is not a primary research paper at all (e.g. it is itself a press release or opinion piece). |

## Eligibility gates

1. **Only `GREEN` studies, published inside the active research window, may
   become ranking-eligible** for the Radar. Window boundaries are defined in
   `config/research_window.json`.
2. **`YELLOW` must never enter the ranked Radar.** It may remain in
   `research/candidates/` pending further verification.
3. **`RED` must never enter normal production recommendations.** It is
   archived to `research/rejected/` for audit purposes. `RED` studies may
   still be used for specific *editorial* formats that debunk or contextualize
   a misleading headline (see `config/scoring_rules.md`, Tier D handling) —
   but they are never treated as a validated scientific source.

## Verification is not the same thing as usefulness

`verification_status` is strictly about whether the underlying science claim
is trustworthy. It must be kept **separate** from:

- **`evidence_tier`** — how strong the science is (derived from the
  scientific score; see `scoring_rules.md`). A `GREEN` study can still be
  weak evidence (Tier D); a well-verified null result is still `GREEN`.
- **`content_priority`** — how promising the study is for a video (derived
  from the YouTube score). This is independent of scientific strength.
- **`production_priority`** — the combined recommendation for whether/how to
  produce a video, derived from both `evidence_tier` and `content_priority`.

A study can be `GREEN` (trustworthy) and still score low on YouTube
potential, and vice versa. Never collapse these into a single number by hand
— the deterministic validator (`scripts/validate_study.py`) is the only
component allowed to derive `evidence_tier`, `content_priority`, and
`production_priority` from the component scores.

## Required verification evidence

A study record moving to `GREEN` should have `verification_notes` describing
what was checked against the primary source (e.g. "abstract, methods, and
results section checked against DOI record; press release headline compares
correctly to reported effect size"). Missing or empty `verification_notes`
on a `GREEN` record is a red flag for manual review, even though the
deterministic validator (V1) does not currently enforce non-empty notes as a
hard failure.
