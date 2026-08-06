# Divergence Metrics -- Methodology

## Research question

Are the Shahmukhi pages on punjabi-kavita.com transliterations of the
Gurmukhi pages, or drawn from separate printed sources? One known case
(Babu Firoz Din Sharaf, "Main Punjabi, Punjab De Rehan Wala") shows the two
versions differing in wording, not just script. This analysis checks
whether that is an isolated case or a pattern, using only metrics that do
not require reading Gurmukhi or Shahmukhi.

## Scope and data

- Input: the 211 matched pairs in output/poet_pairs.csv.
- Source: the poet-level pages already cached in data/raw/ from the
  original scrape. No new network requests were made for this analysis.
- One pair (Avtar Singh Pash) has a Shahmukhi page that returned a
  confirmed server error (HTTP 500) during scraping and was never cached.
  It is included in divergence_metrics.csv with blank metrics and a note,
  and excluded from the ratio distribution and rankings below.

### Important scope limitation: poet-level pages only, not poem-level pages

The pipeline only ever fetched the poet's landing page for each script, not
the individual poem sub-pages a "hub"-layout page links out to. For a
hub-layout page, the text compared here is the poet's bio plus the table of
contents of poem/collection titles on that landing page -- not the full
text of the poems themselves, which lives on pages this analysis has no
access to. For an "inline"-layout page, the poem text is embedded directly
in the cached page, so the comparison there is closer to actual content.

This matters directly for interpretation: when a pair has different page
layouts on the two sides (one hub, one inline -- see "layout_mismatch"
below), a large length difference can arise purely from that structural
difference (a table of contents vs. full text), with no need for the
underlying wording to differ at all.

## Method

For each pair:
1. Load both cached HTML pages.
2. Strip `<script>`/`<style>` tags, the site's fixed navigation container
   (class `pk-header-wrapper`) and `<footer>`. A small fixed set of literal
   nav/footer phrases is also stripped as a fallback, since a minority of
   pages (roughly 4% of ~421 checked) use an older template that does not
   wrap navigation in a recognizable container and would otherwise leak
   "Home Punjabi Poetry Sufi Poetry ... Contact Us"-style text into the
   count. This fallback is a plain substring removal of known fixed
   phrases; it does not attempt to detect or remove anything else.
3. Compute character count and whitespace-delimited word count of what's
   left, after collapsing all whitespace to single spaces.
4. word_ratio = shahmukhi_word_count / gurmukhi_word_count (also computed
   for characters, as char_ratio, but word_ratio is the metric used for
   flagging, per the interpretation rule below).
5. For pairs where poem_count is available on both sides (both hub-layout),
   compare the two sub-link counts directly. Where the two sides use
   different layouts, or a page never got cached, sub-link counts are not
   comparable -- see sublinks_match categories below.

## Interpretation rule

A pair is flagged high_divergence=True if word_ratio falls outside
0.8-1.25.

**This is a proxy, not a finding.** A length or word-count difference
cannot by itself distinguish between: a different source edition, a
partially-transcribed page, expansion/contraction from transliteration
between scripts, an encoding artifact, or (as noted above) simply a
different page layout on the two sides. This analysis does not conclude
anything about *why* a given pair diverges. output/divergence_metrics.csv
is a ranked list of candidates for human review, not a conclusion about
textual identity.

## Sub-link match breakdown

- both_inline: 115
- mismatch: 39
- layout_mismatch: 39
- match: 17
- missing_page: 1

`layout_mismatch` means the two sides use different page layouts (one hub,
one inline) -- these pairs are structurally incomparable on sub-link count,
and, per the scope limitation above, are also the pairs most likely to show
large length differences for reasons unrelated to wording.

## Word-ratio distribution (n=210)

- min: 0.1010
- Q1: 0.6194
- median: 1.0000
- Q3: 1.0406
- max: 99.5238
- flagged high_divergence (outside 0.8-1.25): 98 / 211

## Top 20 pairs by divergence

Ranked by max(word_ratio, 1/word_ratio), so both large expansions and large
contractions from Gurmukhi to Shahmukhi rank highly.

1. Mahatma Buddha -- word_ratio=99.5238, gurmukhi_words=189, shahmukhi_words=18810, layout=(hub/inline)
2. Sant Jai Dev -- word_ratio=76.1551, gurmukhi_words=187, shahmukhi_words=14241, layout=(hub/hub)
3. Muqbal (Heer) -- word_ratio=24.7709, gurmukhi_words=851, shahmukhi_words=21080, layout=(hub/inline)
4. Sayyed Shah Murad -- word_ratio=11.8981, gurmukhi_words=108, shahmukhi_words=1285, layout=(hub/inline)
5. Kishan Singh Arif -- word_ratio=10.8743, gurmukhi_words=358, shahmukhi_words=3893, layout=(hub/inline)
6. Rozy Singh -- word_ratio=0.101, gurmukhi_words=485, shahmukhi_words=49, layout=(inline/hub)
7. Miran Shah Jalandhari -- word_ratio=0.1049, gurmukhi_words=1812, shahmukhi_words=190, layout=(hub/hub)
8. Hidayatullah -- word_ratio=7.6892, gurmukhi_words=74, shahmukhi_words=569, layout=(hub/inline)
9. Khwaja Ghulam Farid -- word_ratio=0.1596, gurmukhi_words=1579, shahmukhi_words=252, layout=(hub/hub)
10. Tariq Gujjar -- word_ratio=6.203, gurmukhi_words=197, shahmukhi_words=1222, layout=(inline/inline)
11. Gurjant Takipur -- word_ratio=6.0323, gurmukhi_words=248, shahmukhi_words=1496, layout=(inline/inline)
12. Gurdit Singh Kundan -- word_ratio=5.1982, gurmukhi_words=111, shahmukhi_words=577, layout=(inline/inline)
13. Baba Sheikh Farid -- word_ratio=0.2087, gurmukhi_words=1404, shahmukhi_words=293, layout=(hub/hub)
14. Zafar Iqbal -- word_ratio=4.6762, gurmukhi_words=244, shahmukhi_words=1141, layout=(hub/inline)
15. Sughra Sadaf (Dr.) -- word_ratio=0.2298, gurmukhi_words=692, shahmukhi_words=159, layout=(inline/hub)
16. Karam Ali Shah -- word_ratio=4.0952, gurmukhi_words=147, shahmukhi_words=602, layout=(inline/inline)
17. Babu Firoz Din Sharaf -- word_ratio=0.263, gurmukhi_words=886, shahmukhi_words=233, layout=(hub/inline)
18. Sultan Kharvi -- word_ratio=0.2804, gurmukhi_words=2350, shahmukhi_words=659, layout=(inline/inline)
19. Saleem Kashir -- word_ratio=0.309, gurmukhi_words=2401, shahmukhi_words=742, layout=(inline/inline)
20. Sandeep Kumar -- word_ratio=0.3095, gurmukhi_words=168, shahmukhi_words=52, layout=(inline/inline)

9 of these top 20 are layout_mismatch pairs (one hub,
one inline) -- consistent with the scope limitation above: a meaningful share
of the largest length differences in this ranking coincide with a structural
difference between the two pages, not necessarily a wording difference. This
is an observed pattern in our own data (the page_layout columns), not an
inference about why any specific pair diverges.

## Ground-truth check: Babu Firoz Din Sharaf

Rank 17 of 210 by divergence score. word_ratio=0.263 (gurmukhi_words=886, shahmukhi_words=233). page_layout: gurmukhi=hub, shahmukhi=inline. The two sides use different page layouts (hub vs inline), which by itself is sufficient to produce a length mismatch independent of whether the underlying poem wording also differs. Sharaf's high rank confirms the metric picks up *some* real signal, but does not by itself confirm that the signal is specifically a wording difference rather than this structural one.

## Limitations

- Length-based metrics are a proxy for content difference, not a measure of
  it. Two pages can have identical word counts and completely different
  content, or genuinely different word counts and be faithful editions that
  simply render differently in Shahmukhi vs. Gurmukhi typesetting.
- This analysis cannot read Gurmukhi or Shahmukhi and made no attempt to
  align, diff, or interpret the actual text of either version.
- Comparisons are poet-page-level, not poem-level (see scope limitation
  above); a hub-layout page's text is dominated by its table of contents,
  not full poem text.
- The nav/footer stripping fallback is a fixed literal-phrase removal for
  a known minority template variant; it may leave small amounts of residual
  navigation text in edge cases not covered by the two known phrasings.
- One pair (Avtar Singh Pash) is excluded from all ratio statistics due to
  a confirmed server-side fetch failure on the Shahmukhi side, not an
  absence of content.
