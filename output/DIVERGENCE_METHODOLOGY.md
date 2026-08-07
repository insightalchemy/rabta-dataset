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

### Part 3: Sharaf, like-for-like

Sharaf's 9 Gurmukhi sub-pages (the pages his hub landing page links to,
fetched specifically for this check -- see logs/subpage_fetch.log) were
concatenated and compared against his Shahmukhi inline page as a genuinely
like-for-like measurement, removing the hub/inline layout confound entirely.

Per-sub-page counts:

- AudioBabuFirozDinSharaf.php: 614 chars, 115 words, 2 headings, 0 paragraphs
- Bhajanawali-Babu-Firoz-Din-Sharaf.php: 3300 chars, 716 words, 12 headings, 11 paragraphs
- Chonvein-Baint-Babu-Firoz-Din-Sharaf.php: 4524 chars, 931 words, 2 headings, 2 paragraphs
- JoganBabuFirozDinSharaf.php: 17705 chars, 3735 words, 32 headings, 31 paragraphs
- Laalaan-Dian-Lariaan-Babu-Firoz-Din-Sharaf.php: 103936 chars, 20958 words, 45 headings, 71 paragraphs
- NooriDarshanBabuFirozDinSharaf.php: 48345 chars, 10432 words, 36 headings, 27 paragraphs
- PoetryBabuFirozDinSharaf.php: 81812 chars, 17605 words, 81 headings, 80 paragraphs
- Rubaaiyaan-Babu-Firoz-Din-Sharaf.php: 5878 chars, 1214 words, 41 headings, 40 paragraphs
- SunehriKalianBabuFirozDinSharaf.php: 179790 chars, 36459 words, 105 headings, 104 paragraphs

- Concatenated Gurmukhi total: 445912 chars, 92165 words
- Shahmukhi inline page total: 1333 chars, 233 words
- word_ratio (shahmukhi/gurmukhi): 0.0025
- char_ratio (shahmukhi/gurmukhi): 0.0030

Placed within the 115-pair inline/inline distribution (min=0.2804,
median=1.0079,
max=6.2030), Sharaf's ratio of
0.0025 sits at the 0.0th
percentile -- **far outside** the 0.8-1.25 band used throughout this study,
and in fact below every one of the 115 inline/inline pairs. Once the layout
confound is removed, Sharaf is not a borderline or typical case: his is the
most extreme length disparity found anywhere in this dataset by two orders
of magnitude.

**Poem-level breakdown.** A structural marker is available and was used
instead of reading either script: heading (`<h1>`-`<h4>`) and paragraph
(`<p>`) tag counts, which do not require interpreting any text content.
Gurmukhi sub-pages consistently pair one heading with one paragraph (a
one-heading-one-poem convention, off by a small constant per page for the
page's own title heading), totaling 356
headings and 366 paragraphs
across the 9 sub-pages -- consistent with roughly 350-360 individual poems.
The Shahmukhi page, by the same mechanical measure, has only
3 headings and 2
paragraphs total -- matching its two bio paragraphs, not a set of poem
bodies. The 24 short lines visible under a "Poetry Babu Firoz Din Sharaf"
heading on the Shahmukhi page are plain text, not individually tagged
paragraphs, and are not followed by verse content of any length.

By this structural marker, the Shahmukhi page does not contain a number of
poems comparable to the Gurmukhi side -- it contains a list of titles, not
poem bodies. This is reported as a structural fact from tag counts, not a
conclusion about why the two versions differ or what the title list
represents; matching those titles against specific Gurmukhi poems would
require transliteration, which is out of scope for this analysis.

### Part 4: tightening the inline finding

The 115-pair inline/inline subset is the only subset in this study where
the comparison is like-for-like without a known confound (unlike Sharaf,
these pairs did not require fetching additional sub-pages, since both
sides already have poem text embedded directly on the cached page). Of
these, 42 pairs (the same ones flagged high_divergence=True
earlier) are the most interesting group so far.

| poet | gurmukhi_words | shahmukhi_words | ratio | longer side |
|---|---|---|---|---|
| Sultan Kharvi | 2350 | 659 | 0.2804 | gurmukhi |
| Saleem Kashir | 2401 | 742 | 0.309 | gurmukhi |
| Sandeep Kumar | 168 | 52 | 0.3095 | gurmukhi |
| Jaswant Singh Wanta | 1310 | 418 | 0.3191 | gurmukhi |
| Prof Ashiq Raheel | 1831 | 606 | 0.331 | gurmukhi |
| Arif Abdul Mateen | 1847 | 638 | 0.3454 | gurmukhi |
| Amin Khayal | 1531 | 605 | 0.3952 | gurmukhi |
| Ikram Majeed | 1557 | 651 | 0.4181 | gurmukhi |
| Abdul Karim Qudsi | 1819 | 796 | 0.4376 | gurmukhi |
| Prof Sharab | 1264 | 562 | 0.4446 | gurmukhi |
| Sachal Sarmast | 1017 | 454 | 0.4464 | gurmukhi |
| Aashiq Chaudhari/Lahore | 1275 | 598 | 0.469 | gurmukhi |
| Alexander Pushkin | 342 | 162 | 0.4737 | gurmukhi |
| Iqbal Rahat | 1321 | 641 | 0.4852 | gurmukhi |
| Tanveer Bukhari | 2244 | 1096 | 0.4884 | gurmukhi |
| Wasif Ali Wasif | 1025 | 526 | 0.5132 | gurmukhi |
| Imran Saleem | 1251 | 677 | 0.5412 | gurmukhi |
| Sant Rein | 1187 | 653 | 0.5501 | gurmukhi |
| Gual Das | 387 | 217 | 0.5607 | gurmukhi |
| Akbar Qazmi | 873 | 491 | 0.5624 | gurmukhi |
| Lala Kirpa Sagar | 257 | 147 | 0.572 | gurmukhi |
| Karnail Singh Paras | 372 | 216 | 0.5806 | gurmukhi |
| Umar Ghani | 2040 | 1185 | 0.5809 | gurmukhi |
| Sadhu Ishar Das Udasi | 1824 | 1062 | 0.5822 | gurmukhi |
| Chanan Jethuwalia | 172 | 102 | 0.593 | gurmukhi |
| Ghulam Mustafa Bismil | 1894 | 1140 | 0.6019 | gurmukhi |
| Gurnam Singh Teer | 315 | 195 | 0.619 | gurmukhi |
| Baba Najmi | 611 | 399 | 0.653 | gurmukhi |
| Afzal Sahir | 347 | 251 | 0.7233 | gurmukhi |
| Sant Wali Ram | 377 | 274 | 0.7268 | gurmukhi |
| Fida Bukhari | 682 | 513 | 0.7522 | gurmukhi |
| Subramanya Bharathi | 348 | 265 | 0.7615 | gurmukhi |
| Habib Jalib | 310 | 245 | 0.7903 | gurmukhi |
| Yamla Jatt | 304 | 389 | 1.2796 | shahmukhi |
| Bishan Singh Upashak | 182 | 237 | 1.3022 | shahmukhi |
| Surjit Rampuri | 126 | 168 | 1.3333 | shahmukhi |
| Sidhu Dhandiwal | 199 | 395 | 1.9849 | shahmukhi |
| Ahmed Saleem | 240 | 517 | 2.1542 | shahmukhi |
| Karam Ali Shah | 147 | 602 | 4.0952 | shahmukhi |
| Gurdit Singh Kundan | 111 | 577 | 5.1982 | shahmukhi |
| Gurjant Takipur | 248 | 1496 | 6.0323 | shahmukhi |
| Tariq Gujjar | 197 | 1222 | 6.203 | shahmukhi |

Directional split: **33 of 42** (79%)
have the Gurmukhi side longer; **9 of 42**
(21%) have the Shahmukhi side
longer. This directional imbalance is a structural fact worth recording:
within the cleanest comparable subset in this dataset, when the two
versions diverge in length, the Gurmukhi version is longer roughly four
times as often as the Shahmukhi version is. Length alone cannot say why --
a different source edition, partial content, or omitted material could all
produce this pattern, and this analysis does not attempt to choose among
them.
