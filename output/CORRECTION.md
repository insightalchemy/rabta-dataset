# Correction Notice

Date: 2026-08-07T00:40:15+00:00

## What was wrong

The link-detection logic used throughout this pipeline (`a[href$=".php"]`,
in scripts 3, 6, 8, 9, 11, 12) matched an href only if it ended literally in
".php". It did not match hrefs with a URL fragment appended, such as
`Foo.php#Bar1`. The site uses exactly this pattern extensively: a poet's
landing page links to a sub-page's specific poem via a fragment anchor
(e.g. `PoetryBabuFirozDinSharafShahmukhi.php#Sharaf1`).

Any page whose *only* outbound content links used this fragment pattern
was therefore seen as having zero outbound links, and was misclassified
as page_layout="inline" instead of "hub". Its real content -- on the
sub-page the fragment-suffixed links point to -- was never fetched, because
the sub-page was invisible to every step that discovers what to fetch.

This is not a text-extraction bug. The body-text extraction
(`get_text()` after stripping nav/header/footer) was verified, by
re-running it unchanged on every already-cached page, to produce byte-
for-byte identical word and character counts to what was previously
published: 0 of 828 Gurmukhi pages and 0 of 226 cached Shahmukhi pages
changed. The bug is entirely that some sub-pages were never fetched in
the first place, because the links to them were invisible to our selector.

The initial report on Babu Firoz Din Sharaf ("PoetryBabuFirozDinSharafShahmukhi.php")
also referred imprecisely: that exact file was never fetched or cached
before this correction. The 233-word figure previously published was for
a different, already-cached file -- `BabuFirozDinSharafShahmukhi.php`, his
poet landing page -- and that figure was and remains accurate for that
specific page. What was wrong was treating that landing page's word count
as if it represented his total Shahmukhi content, when it is actually a
hub page pointing to a sub-page that had never been retrieved.

## Scope of the bug

- Checked: Phase A (index-page poet extraction, the source of the v0.1
  828/227/211 counts). **Not affected** -- both index pages contain zero
  fragment-suffixed hrefs. The poet lists, the 211 matched pairs, and the
  match methods (exact_nohyphen/exact_hyphen/normalized) are unchanged and
  not implicated by this bug.
- Affected: page_layout classification and sub-link/poem_count for
  individual poet pages, computed in Phase C+D onward. Of 828 cached
  Gurmukhi poet pages and 226 cached Shahmukhi poet pages, **372 Gurmukhi
  and 56 Shahmukhi pages (428 total) were misclassified "inline" and
  should be "hub."** All 428 reclassifications go the same direction
  (inline -> hub); none went the other way.
- Making these 428 pages' content genuinely comparable requires fetching
  the sub-pages their fragment-anchored links point to: **1,928 distinct
  sub-pages, across both scripts, are not yet fetched.** That is well
  beyond this project's 500-page auto-proceed threshold and has not been
  fetched. The word counts and layout labels below reflect only the
  correction that was possible without that fetch (relabeling + re-running
  analysis on already-cached text) plus a full, complete fetch for the one
  case (Sharaf) already published as a specific finding.

## Corrected figures

### Sharaf, the ground-truth case (fully corrected -- all pages now fetched)

Previously published (turn before last): Gurmukhi concatenated
92,165 words across 9 sub-pages vs. Shahmukhi 233 words -- ratio 0.0025,
reported as the 0th percentile of the inline distribution, "two orders of
magnitude" beyond the next most extreme case.

**That was itself incomplete.** Fixing the link bug revealed a 10th
Gurmukhi sub-page (`NooriDarshanBabuFirozDinSharaf2.php`) and a genuine
Shahmukhi sub-page (`PoetryBabuFirozDinSharafShahmukhi.php`, containing 24
full poems) that the previous pass also missed for the same reason,
despite Sharaf being the specific case under manual review at the time.
Both are now fetched (logs/subpage_fetch.log). Corrected totals:

- Gurmukhi, 10 sub-pages concatenated: 104,577 words, 504,763 chars
- Shahmukhi, landing page + 1 sub-page: 6,739 words, 31,408 chars
- **Corrected ratio: 0.0644** (previously published: 0.0025 -- roughly
  26x off)

Sharaf's Shahmukhi content is real and substantial (6,739 words, 24 full
poems on the sub-page) -- not the near-empty stub the previous report
described. The divergence from Gurmukhi (104,577 words) is still large and
still the most extreme ratio found in the corrected clean-comparison
subset, but it is a difference in degree, not the near-total absence
previously reported.

### page_layout / hub vs inline, all 211 matched pairs (relabeled, no new fetch)

Corrected layout combination counts (output/pairs_corrected_layout.csv):

- both_hub: 115 (was 56)
- both_inline (genuinely comparable): 77 (was 115)
- layout_mismatch: 18 (was 39)
- missing_page: 1 (unchanged -- Avtar Singh Pash, confirmed server error)

### The "clean" inline/inline subset, corrected (output/divergence_inline_only_corrected.csv)

n=77 (was 115, now excluding 38 pairs that are actually hub on at least
one side):

- min: 0.2804, Q1: 0.6770, median: 1.0096, Q3: 1.0242, max: 1.1636
- outside 0.8-1.25: 20 / 77 (26.0%) -- was 42/115 (36.5%)
- **Directional split among the 20 divergent pairs: 20 Gurmukhi-longer, 0
  Shahmukhi-longer** -- was 33 Gurmukhi-longer / 9 Shahmukhi-longer. All 9
  of the previously reported "Shahmukhi-longer" divergent pairs turn out
  to have had at least one side misclassified; once removed from the truly
  comparable subset, every remaining divergence in the clean subset points
  the same direction.

### Shahmukhi content-volume histogram

The raw word counts and the headline "59.7% under 500 words / 84.1% under
1000 words" figures are numerically unchanged (verified: 0 word-count
differences on re-run). **Their interpretation was wrong.** Of the 135
Shahmukhi pages under 500 words, **105 (78%) are pages now known to be
hub pages whose real content was never fetched** -- only 30 (22%) are
pages confirmed to genuinely be that short. The "stub pattern" reported
last turn substantially overstates how much of the Shahmukhi corpus is
actually thin; most of what looked thin was simply unfetched.

## What is still unresolved

1,926 sub-pages remain unfetched: 1,622 on the Gurmukhi side, 304 on the
Shahmukhi side (across 372 Gurmukhi and 56 Shahmukhi reclassified poet
pages respectively). Until they are fetched,
the true word count, true page_layout-independent content volume, and
true coverage-depth ratio for 428 poet pages are unknown -- not zero, not
short, unknown. Any dataset consumer should treat word counts and
"thin page" claims for those 428 pages, and any pair involving them, as
undetermined pending that fetch, which requires an explicit decision
given it exceeds the 500-page auto-proceed threshold.

## Files added or changed by this correction

- scripts/common.py: added `extract_content_links()`, the corrected,
  fragment-aware link extractor; scripts 3, 6, 8, 9, 11, 12 used a
  fragment-blind version before this fix.
- output/pairs_corrected_layout.csv: all 211 pairs with both old and
  corrected page_layout per side.
- output/divergence_inline_only_corrected.csv: the 77-pair genuinely
  comparable subset.
- data/raw/subpages/gurmukhi/NooriDarshanBabuFirozDinSharaf2.php,
  data/raw/subpages/shahmukhi/PoetryBabuFirozDinSharafShahmukhi.php: newly
  fetched to complete the Sharaf case study specifically.
- output/METHODOLOGY.md: "Presence vs. coverage depth" section replaced
  (see that file; this is a correction to added interpretive text, not to
  the v0.1 poet-matching counts, which are confirmed unaffected above).
