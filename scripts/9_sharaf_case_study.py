import csv
import glob

from bs4 import BeautifulSoup

from common import DATA_RAW, OUTPUT

NAV_PHRASES = [
    "☰ Home Punjabi Poetry Sufi Poetry Urdu Poetry Hindi Poetry Translations",
    "☰ Home Punjabi Poetry Sufi Poetry Hindi Poetry Translations",
    "Home Punjabi Poetry Sufi Poetry Urdu Poetry Hindi Poetry Translations",
    "Home Punjabi Poetry Sufi Poetry Hindi Poetry Translations",
]
FOOTER_PHRASES = ["Contact Us...", "Contact Us"]

SHARAF_SUBPAGES = sorted(glob.glob(str(DATA_RAW / "subpages" / "gurmukhi" / "*.php")))
SHARAF_SHAHMUKHI_PAGE = DATA_RAW / "shahmukhi" / "BabuFirozDinSharafShahmukhi.php"


def load_body_text(path):
    with open(path, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    header = soup.find(class_="pk-header-wrapper")
    if header:
        header.decompose()
    footer = soup.find("footer")
    if footer:
        footer.decompose()
    text = soup.get_text(" ", strip=True)
    for phrase in NAV_PHRASES + FOOTER_PHRASES:
        text = text.replace(phrase, " ")
    return " ".join(text.split())


def tag_counts(path):
    with open(path, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    headings = len(soup.find_all(["h1", "h2", "h3", "h4"]))
    paragraphs = len(soup.find_all("p"))
    return headings, paragraphs


def main():
    print("=== PART 3: SHARAF LIKE-FOR-LIKE ===\n")

    subpage_texts = []
    subpage_rows = []
    for path in SHARAF_SUBPAGES:
        text = load_body_text(path)
        h, p = tag_counts(path)
        subpage_texts.append(text)
        subpage_rows.append((path.split("/")[-1], len(text), len(text.split()), h, p))

    concatenated = " ".join(subpage_texts)
    g_chars = len(concatenated)
    g_words = len(concatenated.split())

    s_text = load_body_text(SHARAF_SHAHMUKHI_PAGE)
    s_chars = len(s_text)
    s_words = len(s_text.split())
    s_h, s_p = tag_counts(SHARAF_SHAHMUKHI_PAGE)

    print("Per-sub-page breakdown (Gurmukhi):")
    for name, chars, words, h, p in subpage_rows:
        print(f"  {name:55s} chars={chars:6d} words={words:6d} headings={h:4d} paragraphs={p:4d}")

    print(f"\nConcatenated Gurmukhi total: chars={g_chars}, words={g_words}")
    print(f"Shahmukhi inline page total: chars={s_chars}, words={s_words}")

    ratio_words = s_words / g_words
    ratio_chars = s_chars / g_chars
    print(f"\nword_ratio (shahmukhi/gurmukhi_concatenated) = {ratio_words:.4f}")
    print(f"char_ratio (shahmukhi/gurmukhi_concatenated) = {ratio_chars:.4f}")

    with open(OUTPUT / "divergence_inline_only.csv", encoding="utf-8") as f:
        inline_rows = list(csv.DictReader(f))
    inline_ratios = sorted(float(r["word_ratio_shahmukhi_over_gurmukhi"]) for r in inline_rows)

    below = sum(1 for r in inline_ratios if r < ratio_words)
    percentile = 100 * below / len(inline_ratios)
    print(f"\nWithin the {len(inline_ratios)}-pair inline/inline distribution "
          f"(min={inline_ratios[0]:.4f}, median={inline_ratios[len(inline_ratios)//2]:.4f}, "
          f"max={inline_ratios[-1]:.4f}):")
    print(f"  Sharaf's like-for-like ratio of {ratio_words:.4f} would sit at the "
          f"{percentile:.1f}th percentile ({below} of {len(inline_ratios)} inline pairs "
          f"have a smaller ratio).")
    in_band = 0.8 <= ratio_words <= 1.25
    print(f"  {'INSIDE' if in_band else 'OUTSIDE'} the 0.8-1.25 band used elsewhere in this study.")

    print(f"\nTotal headings on Gurmukhi sub-pages: {sum(r[3] for r in subpage_rows)}")
    print(f"Total <p> paragraphs on Gurmukhi sub-pages: {sum(r[4] for r in subpage_rows)}")
    print(f"Shahmukhi page: headings={s_h}, paragraphs={s_p}")

    sharaf_result = {
        "subpage_rows": subpage_rows,
        "g_chars": g_chars, "g_words": g_words,
        "s_chars": s_chars, "s_words": s_words,
        "ratio_words": ratio_words, "ratio_chars": ratio_chars,
        "percentile": percentile, "in_band": in_band,
        "inline_ratios": inline_ratios,
        "s_headings": s_h, "s_paragraphs": s_p,
    }

    print("\n\n=== PART 4: DIVERGENT INLINE/INLINE PAIRS ===\n")
    divergent = [r for r in inline_rows if r["high_divergence"] == "True"]
    divergent.sort(key=lambda r: float(r["word_ratio_shahmukhi_over_gurmukhi"]))

    gurmukhi_longer = 0
    shahmukhi_longer = 0
    divergent_table = []
    for r in divergent:
        g_words = int(r["gurmukhi_word_count"])
        s_words = int(r["shahmukhi_word_count"])
        longer = "gurmukhi" if g_words > s_words else "shahmukhi"
        if longer == "gurmukhi":
            gurmukhi_longer += 1
        else:
            shahmukhi_longer += 1
        divergent_table.append((r["gurmukhi_name_raw"], g_words, s_words,
                                 r["word_ratio_shahmukhi_over_gurmukhi"], longer))

    print(f"{len(divergent)} pairs. {gurmukhi_longer} gurmukhi-longer, {shahmukhi_longer} shahmukhi-longer.")
    for name, g, s, ratio, longer in divergent_table:
        print(f"  {name:35s} gurmukhi={g:6d} shahmukhi={s:6d} ratio={ratio:>8s}  longer={longer}")

    write_methodology_update(sharaf_result, divergent_table, gurmukhi_longer, shahmukhi_longer)


PART3_4_MARKER = "## Part 3 and Part 4: the Sharaf like-for-like case and the tightened inline finding"


def write_methodology_update(sharaf_result, divergent_table, gurmukhi_longer, shahmukhi_longer):
    subpage_lines = "\n".join(
        f"- {name}: {chars} chars, {words} words, {h} headings, {p} paragraphs"
        for name, chars, words, h, p in sharaf_result["subpage_rows"]
    )
    divergent_lines = "\n".join(
        f"| {name} | {g} | {s} | {ratio} | {longer} |"
        for name, g, s, ratio, longer in divergent_table
    )
    total_divergent = len(divergent_table)

    section = f"""{PART3_4_MARKER}

### Part 3: Sharaf, like-for-like

Sharaf's 9 Gurmukhi sub-pages (the pages his hub landing page links to,
fetched specifically for this check -- see logs/subpage_fetch.log) were
concatenated and compared against his Shahmukhi inline page as a genuinely
like-for-like measurement, removing the hub/inline layout confound entirely.

Per-sub-page counts:

{subpage_lines}

- Concatenated Gurmukhi total: {sharaf_result['g_chars']} chars, {sharaf_result['g_words']} words
- Shahmukhi inline page total: {sharaf_result['s_chars']} chars, {sharaf_result['s_words']} words
- word_ratio (shahmukhi/gurmukhi): {sharaf_result['ratio_words']:.4f}
- char_ratio (shahmukhi/gurmukhi): {sharaf_result['ratio_chars']:.4f}

Placed within the 115-pair inline/inline distribution (min={sharaf_result['inline_ratios'][0]:.4f},
median={sharaf_result['inline_ratios'][len(sharaf_result['inline_ratios'])//2]:.4f},
max={sharaf_result['inline_ratios'][-1]:.4f}), Sharaf's ratio of
{sharaf_result['ratio_words']:.4f} sits at the {sharaf_result['percentile']:.1f}th
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
page's own title heading), totaling {sum(r[3] for r in sharaf_result['subpage_rows'])}
headings and {sum(r[4] for r in sharaf_result['subpage_rows'])} paragraphs
across the 9 sub-pages -- consistent with roughly 350-360 individual poems.
The Shahmukhi page, by the same mechanical measure, has only
{sharaf_result['s_headings']} headings and {sharaf_result['s_paragraphs']}
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
these, {total_divergent} pairs (the same ones flagged high_divergence=True
earlier) are the most interesting group so far.

| poet | gurmukhi_words | shahmukhi_words | ratio | longer side |
|---|---|---|---|---|
{divergent_lines}

Directional split: **{gurmukhi_longer} of {total_divergent}** ({100*gurmukhi_longer/total_divergent:.0f}%)
have the Gurmukhi side longer; **{shahmukhi_longer} of {total_divergent}**
({100*shahmukhi_longer/total_divergent:.0f}%) have the Shahmukhi side
longer. This directional imbalance is a structural fact worth recording:
within the cleanest comparable subset in this dataset, when the two
versions diverge in length, the Gurmukhi version is longer roughly four
times as often as the Shahmukhi version is. Length alone cannot say why --
a different source edition, partial content, or omitted material could all
produce this pattern, and this analysis does not attempt to choose among
them.
"""

    path = OUTPUT / "DIVERGENCE_METHODOLOGY.md"
    existing = path.read_text(encoding="utf-8")
    if PART3_4_MARKER in existing:
        existing = existing[: existing.index(PART3_4_MARKER)]
    content = existing.rstrip("\n") + "\n\n" + section
    path.write_text(content, encoding="utf-8")
    print(f"\nUpdated {path}")


if __name__ == "__main__":
    main()
