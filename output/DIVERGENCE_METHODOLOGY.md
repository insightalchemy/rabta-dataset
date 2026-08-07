# Divergence Metrics -- Methodology

**CORRECTED (see output/CORRECTION.md).** A link-detection bug caused
fragment-suffixed hrefs (`Foo.php#Bar`) to be invisible to this pipeline,
so many pages were misclassified "inline" when they are actually "hub"
pages linking to unfetched sub-pages. This affects several numbers below:
the Sharaf like-for-like ratio reported later in this document as 0.0025
is wrong -- the corrected figure, with all pages actually fetched, is
**0.0644** (Gurmukhi 104,577 words across 10 sub-pages vs. Shahmukhi 6,739
words across a landing page + 1 sub-page). The 115-pair "inline/inline"
subset used throughout this document is also wrong -- 38 of those 115
pairs are actually hub on at least one side; the genuinely comparable
subset is **77 pairs**, and within it the "42 divergent pairs / 33
Gurmukhi-longer / 9 Shahmukhi-longer" split reported later is superseded
by a corrected **20 divergent pairs, all 20 Gurmukhi-longer, 0
Shahmukhi-longer** (output/divergence_inline_only_corrected.csv). See
output/CORRECTION.md for the full account, root cause, and what remains
unfetched (1,926 sub-pages). The text below is left as originally
published, for the audit trail, and should be read only in light of this
notice.

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

## Stratification: the layout confound

The first pass at this analysis (the "Top 20 by divergence" ranking earlier
in this document) ranked all 211 pairs together regardless of page layout.
Babu Firoz Din Sharaf, our one ground-truth case of known wording
divergence, ranked 17th of 210 in that pass. On inspection, Sharaf's pair
turned out to be layout-mismatched: his Gurmukhi page is hub-layout (a
table of contents linking to sub-pages) and his Shahmukhi page is
inline-layout (full text embedded directly). That structural difference
alone is enough to produce a large length gap, independent of whether the
underlying wording differs at all -- so his rank of 17 did not validate the
metric. It happened to also flag 39 other pairs sharing the
same structural mismatch, several of which occupied the very top of that
original ranking (e.g. a Dhammapada translation where one side is a 5-link
table of contents and the other is 18,810 words of embedded text).

**This is recorded here as a methodological finding in its own right: an
unstratified length-ratio comparison across a dataset with mixed page
layouts will surface page-architecture differences as if they were content
differences, and a single well-understood ground-truth case was what
exposed it.** The original unstratified ranking (above) should be treated
as uninterpretable and is retained in this document only for that reason,
not as a result to act on.

### Corrected approach: stratify by layout before ranking

Pairs were split into groups that are or are not directly comparable by
this length-based method:

- **inline/inline** (115 pairs) -- both sides have poem text embedded
  directly on the cached page. These are the only pairs where a length
  ratio plausibly reflects the compared pages' actual content rather than
  architecture. Output: output/divergence_inline_only.csv.
- **hub/inline** (39 pairs) -- one side is a table of contents,
  the other is full text. Not comparable by this method; reported
  separately, not ranked against the inline subset.
- **hub/hub, sub-link counts match** (17 pairs) and **hub/hub, sub-link
  counts differ** (39 pairs) -- both sides are tables of contents, so the
  text compared is bio + link-title text, not poem content. Also not
  comparable to the inline subset, and kept separate from each other since
  a matching sub-link count is at least a weak structural signal the
  mismatched group lacks.
- **missing page** (1 pair) -- Avtar Singh Pash, excluded entirely
  (confirmed server-side fetch failure, not an absence of content).

### Inline/inline word-ratio distribution (n=115)

- min: 0.2804
- Q1: 0.7233
- median: 1.0079
- Q3: 1.0336
- max: 6.2030
- outside 0.8-1.25: 42 / 115

Even restricted to the cleanest, most directly comparable subset, over a
third of pairs fall outside the 0.8-1.25 band. This does not confirm
different wording for any specific pair -- it means the inline/inline
subset still contains real candidates for human review, now without the
layout confound.

### 20 largest divergences, inline/inline subset only

1. Tariq Gujjar -- word_ratio=6.203, gurmukhi_words=197, shahmukhi_words=1222
2. Gurjant Takipur -- word_ratio=6.0323, gurmukhi_words=248, shahmukhi_words=1496
3. Gurdit Singh Kundan -- word_ratio=5.1982, gurmukhi_words=111, shahmukhi_words=577
4. Karam Ali Shah -- word_ratio=4.0952, gurmukhi_words=147, shahmukhi_words=602
5. Sultan Kharvi -- word_ratio=0.2804, gurmukhi_words=2350, shahmukhi_words=659
6. Saleem Kashir -- word_ratio=0.309, gurmukhi_words=2401, shahmukhi_words=742
7. Sandeep Kumar -- word_ratio=0.3095, gurmukhi_words=168, shahmukhi_words=52
8. Jaswant Singh Wanta -- word_ratio=0.3191, gurmukhi_words=1310, shahmukhi_words=418
9. Prof Ashiq Raheel -- word_ratio=0.331, gurmukhi_words=1831, shahmukhi_words=606
10. Arif Abdul Mateen -- word_ratio=0.3454, gurmukhi_words=1847, shahmukhi_words=638
11. Amin Khayal -- word_ratio=0.3952, gurmukhi_words=1531, shahmukhi_words=605
12. Ikram Majeed -- word_ratio=0.4181, gurmukhi_words=1557, shahmukhi_words=651
13. Abdul Karim Qudsi -- word_ratio=0.4376, gurmukhi_words=1819, shahmukhi_words=796
14. Prof Sharab -- word_ratio=0.4446, gurmukhi_words=1264, shahmukhi_words=562
15. Sachal Sarmast -- word_ratio=0.4464, gurmukhi_words=1017, shahmukhi_words=454
16. Ahmed Saleem -- word_ratio=2.1542, gurmukhi_words=240, shahmukhi_words=517
17. Aashiq Chaudhari/Lahore -- word_ratio=0.469, gurmukhi_words=1275, shahmukhi_words=598
18. Alexander Pushkin -- word_ratio=0.4737, gurmukhi_words=342, shahmukhi_words=162
19. Iqbal Rahat -- word_ratio=0.4852, gurmukhi_words=1321, shahmukhi_words=641
20. Tanveer Bukhari -- word_ratio=0.4884, gurmukhi_words=2244, shahmukhi_words=1096

### 20 smallest divergences (ratio closest to 1.0), inline/inline subset only

1. Ahmed Rahi -- word_ratio=1.0, gurmukhi_words=180, shahmukhi_words=180
2. Qasoor Mand -- word_ratio=1.0, gurmukhi_words=145, shahmukhi_words=145
3. Kalidasa (Mahakavi) -- word_ratio=1.001, gurmukhi_words=12426, shahmukhi_words=12439
4. Akhtar Kashmiri -- word_ratio=0.9983, gurmukhi_words=598, shahmukhi_words=597
5. Akhtar Hussain Akhtar -- word_ratio=0.9982, gurmukhi_words=561, shahmukhi_words=560
6. Aliya Bukhari Hala -- word_ratio=1.0019, gurmukhi_words=527, shahmukhi_words=528
7. Najabat -- word_ratio=1.0024, gurmukhi_words=6588, shahmukhi_words=6604
8. Pir Muhammad -- word_ratio=1.0025, gurmukhi_words=4417, shahmukhi_words=4428
9. Abid Jafri -- word_ratio=0.9967, gurmukhi_words=306, shahmukhi_words=305
10. Saleem Dilawari -- word_ratio=0.9965, gurmukhi_words=853, shahmukhi_words=850
11. Irfan Sadiq -- word_ratio=0.9963, gurmukhi_words=536, shahmukhi_words=534
12. Sain Labhu Shah -- word_ratio=1.0042, gurmukhi_words=1658, shahmukhi_words=1665
13. Munsaf Mehni -- word_ratio=1.0046, gurmukhi_words=1507, shahmukhi_words=1514
14. Gurdas Ram Alam -- word_ratio=0.9938, gurmukhi_words=324, shahmukhi_words=322
15. Khushi -- word_ratio=1.0067, gurmukhi_words=1052, shahmukhi_words=1059
16. Keso Guni -- word_ratio=1.0079, gurmukhi_words=2023, shahmukhi_words=2039
17. Bakhat Ghulam -- word_ratio=1.0096, gurmukhi_words=208, shahmukhi_words=210
18. Ashraf Sharfi -- word_ratio=1.0105, gurmukhi_words=474, shahmukhi_words=479
19. Rahim Yar -- word_ratio=1.0111, gurmukhi_words=990, shahmukhi_words=1001
20. Hazrat Bu Ali Shah -- word_ratio=1.0118, gurmukhi_words=1520, shahmukhi_words=1538

### Why hub-layout pairs still can't be properly compared

The text available for a hub-layout page is the poet's bio plus the table
of contents of poem/collection titles -- not the poems themselves, which
live on sub-pages this pipeline never fetched. Making a hub-layout pair
genuinely comparable requires fetching those sub-pages and using their
concatenated text instead of the landing page's table of contents. That is
a separate, explicitly network-touching step gated on its own confirmation
(see the fetch-count check before any such fetch is run), not something
resolved by re-analysis of already-cached data.

## Part 3 and Part 4: the Sharaf like-for-like case and the tightened inline finding

**Note: this section reflects the corrected numbers after the link-
detection bug described in output/CORRECTION.md was fixed. An earlier
version of this section, based on incomplete data (a missing Gurmukhi
sub-page and the entire missing Shahmukhi sub-page), reported a ratio of
0.0025; that was wrong. See output/CORRECTION.md for the full account.**

### Part 3: Sharaf, like-for-like

All of Sharaf's Gurmukhi sub-pages (10, discovered via the
corrected fragment-aware link extractor -- see logs/subpage_fetch.log) and
all of his Shahmukhi sub-pages were fetched and concatenated with each
side's landing page, for a genuinely complete like-for-like measurement.

Per-page counts (Gurmukhi):

- AudioBabuFirozDinSharaf.php: 614 chars, 115 words, 2 headings, 0 paragraphs
- Bhajanawali-Babu-Firoz-Din-Sharaf.php: 3300 chars, 716 words, 12 headings, 11 paragraphs
- Chonvein-Baint-Babu-Firoz-Din-Sharaf.php: 4524 chars, 931 words, 2 headings, 2 paragraphs
- JoganBabuFirozDinSharaf.php: 17705 chars, 3735 words, 32 headings, 31 paragraphs
- Laalaan-Dian-Lariaan-Babu-Firoz-Din-Sharaf.php: 103936 chars, 20958 words, 45 headings, 71 paragraphs
- NooriDarshanBabuFirozDinSharaf.php: 48345 chars, 10432 words, 36 headings, 27 paragraphs
- NooriDarshanBabuFirozDinSharaf2.php: 58850 chars, 12412 words, 31 headings, 28 paragraphs
- PoetryBabuFirozDinSharaf.php: 81812 chars, 17605 words, 81 headings, 80 paragraphs
- Rubaaiyaan-Babu-Firoz-Din-Sharaf.php: 5878 chars, 1214 words, 41 headings, 40 paragraphs
- SunehriKalianBabuFirozDinSharaf.php: 179790 chars, 36459 words, 105 headings, 104 paragraphs

- Concatenated Gurmukhi total: 504763 chars, 104577 words
- Concatenated Shahmukhi total: 31408 chars, 6739 words
- word_ratio (shahmukhi/gurmukhi): 0.0644
- char_ratio (shahmukhi/gurmukhi): 0.0622

Placed within the 77-pair inline/inline distribution (the corrected
subset, restricted to pairs confirmed to have zero outbound content links
of any kind on either side -- min=0.2804,
median=1.0096,
max=1.1636), Sharaf's ratio of
0.0644 sits at the 0.0th
percentile -- still **outside** the 0.8-1.25 band used throughout this
study, and still below every one of the 77 inline/inline pairs.
Sharaf remains the most extreme divergence found in this dataset, though
the corrected margin (roughly 4x beyond the next most extreme case) is far
smaller than the incorrect 0.0025 figure implied.

**Poem-level breakdown.** A structural marker is available and was used
instead of reading either script: heading (`<h1>`-`<h4>`) and paragraph
(`<p>`) tag counts, which do not require interpreting any text content.
Gurmukhi sub-pages consistently pair one heading with one paragraph (a
one-heading-one-poem convention, off by a small constant per page for the
page's own title heading), totaling 387
headings and 394 paragraphs
across the 10 sub-pages -- consistent with roughly 350-360
individual poems. The Shahmukhi side, by the same mechanical measure, has
48 headings and 45
paragraphs total across its landing page and sub-page combined -- the
sub-page alone (`PoetryBabuFirozDinSharafShahmukhi.php`) contributes a
substantial share of these, confirming it holds real poem bodies rather
than another title list.

### Part 4: tightening the inline finding

The 77-pair inline/inline subset (corrected) is the only subset in
this study where the comparison is like-for-like without a known confound
-- both sides confirmed to have zero outbound content links, including
fragment-suffixed ones. Of these, 20 pairs (flagged
high_divergence=True) are the most interesting group.

| poet | gurmukhi_words | shahmukhi_words | ratio | longer side |
|---|---|---|---|---|
| Sultan Kharvi | 2350 | 659 | 0.2804 | gurmukhi |
| Saleem Kashir | 2401 | 742 | 0.309 | gurmukhi |
| Jaswant Singh Wanta | 1310 | 418 | 0.3191 | gurmukhi |
| Prof Ashiq Raheel | 1831 | 606 | 0.331 | gurmukhi |
| Arif Abdul Mateen | 1847 | 638 | 0.3454 | gurmukhi |
| Amin Khayal | 1531 | 605 | 0.3952 | gurmukhi |
| Ikram Majeed | 1557 | 651 | 0.4181 | gurmukhi |
| Abdul Karim Qudsi | 1819 | 796 | 0.4376 | gurmukhi |
| Prof Sharab | 1264 | 562 | 0.4446 | gurmukhi |
| Aashiq Chaudhari/Lahore | 1275 | 598 | 0.469 | gurmukhi |
| Iqbal Rahat | 1321 | 641 | 0.4852 | gurmukhi |
| Tanveer Bukhari | 2244 | 1096 | 0.4884 | gurmukhi |
| Wasif Ali Wasif | 1025 | 526 | 0.5132 | gurmukhi |
| Imran Saleem | 1251 | 677 | 0.5412 | gurmukhi |
| Gual Das | 387 | 217 | 0.5607 | gurmukhi |
| Akbar Qazmi | 873 | 491 | 0.5624 | gurmukhi |
| Umar Ghani | 2040 | 1185 | 0.5809 | gurmukhi |
| Sadhu Ishar Das Udasi | 1824 | 1062 | 0.5822 | gurmukhi |
| Ghulam Mustafa Bismil | 1894 | 1140 | 0.6019 | gurmukhi |
| Fida Bukhari | 682 | 513 | 0.7522 | gurmukhi |

Directional split: **20 of 20** (100%)
have the Gurmukhi side longer; **0 of 20**
(0%) have the Shahmukhi side
longer -- none run the other direction.
This directional imbalance is a structural fact worth recording: within
the cleanest comparable subset in this dataset, divergence runs
exclusively toward the
Gurmukhi version being longer. Length alone cannot say why -- a different
source edition, partial content, or omitted material could all produce
this pattern, and this analysis does not attempt to choose among them.

## Full-scale corrected results (all sub-pages fetched)

Generated: 2026-08-07T03:50:29+00:00

**This supersedes the partial-coverage results elsewhere in this document.**
Following the correction described in output/CORRECTION.md, all 1,926
previously-missing sub-pages were fetched (1,922 succeeded, 4 failed --
see logs/subpage_fetch_status.log). Word counts below are now the total
content of each poet's page plus all of its direct sub-pages, on both
sides, for both scripts -- not a landing-page-only or proxy measure.

### 1. Pairs now properly comparable

**210 of 211** pairs are comparable on a unified
word-count basis (was 77 before this fetch). Not comparable:

- Avtar Singh Pash: gurmukhi_words=34525, shahmukhi_words=n/a

3 comparable pairs rely on a page with a known-incomplete
sub-page set (one of the 4 sub-page fetch failures affects them directly):

- Charan Singh Safri: gurmukhi_complete=False, shahmukhi_complete=True
- Shaheed Bhagat Singh: gurmukhi_complete=True, shahmukhi_complete=False
- Shiv Kumar Batalvi: gurmukhi_complete=True, shahmukhi_complete=False

These are included in all statistics below but should be read as a lower
bound on that side's true word count, not an exact figure.

### 2 & 3. Word-ratio distribution (n=210)

- min: 0.0060
- Q1: 0.4373
- median: 0.9285
- Q3: 1.0098
- max: 149.1096
- outside 0.8-1.25: **92 / 210 (43.8%)**

### 4. Directional split -- does 100% Gurmukhi-longer hold at full scale?

**No. It breaks down.** Of 92 divergent pairs:
- Gurmukhi longer: 87 (94.6%)
- Shahmukhi longer: 5 (5.4%)

The Shahmukhi-longer pairs, individually -- these are the most
analytically interesting pairs in the dataset, exactly the cases the
partial-coverage analysis could not see:

- Ahsaan Bajwa: gurmukhi=2426, shahmukhi=8134, ratio=3.3528
- Balvir Dhillon: gurmukhi=73, shahmukhi=10885, ratio=149.1096
- Shah Muhammad: gurmukhi=5667, shahmukhi=11341, ratio=2.0012
- Shiv Kumar Batalvi: gurmukhi=59978, shahmukhi=93727, ratio=1.5627 [Shahmukhi side has an incomplete sub-page set -- treat with extra caution]
- Vidhata Singh Teer: gurmukhi=1867, shahmukhi=18962, ratio=10.1564

### 5. Where Sharaf ranks now

Sharaf's corrected ratio is **0.0639**, ranking **8
of 210** (1 = most Gurmukhi-heavy). He is no longer the single
most extreme case in the dataset -- 7 pairs now show a more
extreme divergence than his, visible only because their sub-pages are now
fetched. He remains a clear, real outlier, just not the most extreme one.

### 6. 20 largest and 20 smallest divergences

Largest (ranked by max(ratio, 1/ratio)):

1. Kartar Singh Kalaswalia: gurmukhi=137249, shahmukhi=826, ratio=0.006
2. Balvir Dhillon: gurmukhi=73, shahmukhi=10885, ratio=149.1096
3. Rozy Singh: gurmukhi=9407, shahmukhi=74, ratio=0.0079
4. Harvinder Singh Chandigarh: gurmukhi=25159, shahmukhi=325, ratio=0.0129
5. Sughra Sadaf (Dr.): gurmukhi=6951, shahmukhi=205, ratio=0.0295
6. Prof Mohan Singh: gurmukhi=58248, shahmukhi=2105, ratio=0.0361
7. Harbhajan Singh Dr: gurmukhi=115016, shahmukhi=5408, ratio=0.047
8. Miran Shah Jalandhari: gurmukhi=20657, shahmukhi=996, ratio=0.0482
9. Babu Firoz Din Sharaf: gurmukhi=105463, shahmukhi=6739, ratio=0.0639
10. Faiz Ahmed Faiz: gurmukhi=5339, shahmukhi=341, ratio=0.0639
11. Rauf Sheikh: gurmukhi=13705, shahmukhi=940, ratio=0.0686
12. Harinder Singh Mehboob: gurmukhi=120248, shahmukhi=9617, ratio=0.08
13. Gurmukh Singh Musafir: gurmukhi=33963, shahmukhi=3103, ratio=0.0914
14. Vidhata Singh Teer: gurmukhi=1867, shahmukhi=18962, ratio=10.1564
15. Prof Puran Singh: gurmukhi=10269, shahmukhi=1027, ratio=0.1
16. Jarnail Singh Arshi: gurmukhi=14478, shahmukhi=1450, ratio=0.1002
17. Charan Singh Safri: gurmukhi=21091, shahmukhi=2406, ratio=0.1141 [incomplete data]
18. Hazara Singh Gurdaspuri: gurmukhi=9838, shahmukhi=1139, ratio=0.1158
19. Khwaja Ghulam Farid: gurmukhi=43464, shahmukhi=5245, ratio=0.1207
20. Guru Arjan Dev Ji: gurmukhi=27501, shahmukhi=3712, ratio=0.135

Smallest (ratio closest to 1.0):

1. Muhammad Boota Gujrati: gurmukhi=2864, shahmukhi=2865, ratio=1.0003
2. Sant Jai Dev: gurmukhi=15108, shahmukhi=15113, ratio=1.0003
3. Kartar Singh Duggal: gurmukhi=1568, shahmukhi=1567, ratio=0.9994
4. Fard Faqir: gurmukhi=5377, shahmukhi=5373, ratio=0.9993
5. Kalidasa (Mahakavi): gurmukhi=12426, shahmukhi=12439, ratio=1.001
6. Zubair Ahmad: gurmukhi=1438, shahmukhi=1440, ratio=1.0014
7. Akhtar Kashmiri: gurmukhi=598, shahmukhi=597, ratio=0.9983
8. Akhtar Hussain Akhtar: gurmukhi=561, shahmukhi=560, ratio=0.9982
9. Aliya Bukhari Hala: gurmukhi=527, shahmukhi=528, ratio=1.0019
10. Najabat: gurmukhi=6588, shahmukhi=6604, ratio=1.0024
11. Fazal Shah: gurmukhi=18164, shahmukhi=18210, ratio=1.0025
12. Kalidas Gujranwalia: gurmukhi=2364, shahmukhi=2370, ratio=1.0025
13. Mian Mohd Bakhsh: gurmukhi=7576, shahmukhi=7557, ratio=0.9975
14. Pir Muhammad: gurmukhi=4417, shahmukhi=4428, ratio=1.0025
15. Abid Jafri: gurmukhi=1894, shahmukhi=1899, ratio=1.0026
16. Anant Prakash Udasin: gurmukhi=1719, shahmukhi=1714, ratio=0.9971
17. Barkat Ram Yuman: gurmukhi=3715, shahmukhi=3727, ratio=1.0032
18. Saleem Dilawari: gurmukhi=853, shahmukhi=850, ratio=0.9965
19. Irfan Sadiq: gurmukhi=536, shahmukhi=534, ratio=0.9963
20. Sain Labhu Shah: gurmukhi=1658, shahmukhi=1665, ratio=1.0042

### What this does and does not establish

Word count is a proxy for content volume, not a measure of textual
identity. A large or small ratio does not by itself indicate a different
source edition, partial transcription, or any other specific cause --
this analysis does not conclude why any pair diverges, at this scale or
any other. The 323 further sub-pages discovered but not fetched (235
Gurmukhi, 88 Shahmukhi -- linked from the newly-fetched sub-pages
themselves) mean even these totals are not a final, exhaustive count for
every hub-layout poet; they are the most complete figures available from
this project to date, not a claim of completeness.
