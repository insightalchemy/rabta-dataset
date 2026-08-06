import csv
import statistics

from bs4 import BeautifulSoup

from common import DATA_RAW, OUTPUT

NAV_PHRASES = [
    "☰ Home Punjabi Poetry Sufi Poetry Urdu Poetry Hindi Poetry Translations",
    "☰ Home Punjabi Poetry Sufi Poetry Hindi Poetry Translations",
    "Home Punjabi Poetry Sufi Poetry Urdu Poetry Hindi Poetry Translations",
    "Home Punjabi Poetry Sufi Poetry Hindi Poetry Translations",
]
FOOTER_PHRASES = ["Contact Us...", "Contact Us"]

LOW_RATIO = 0.8
HIGH_RATIO = 1.25


def load_body_text(html_path):
    with open(html_path, encoding="utf-8") as f:
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

    text = " ".join(text.split())
    return text


def metrics_for(html_path):
    if not html_path.exists():
        return None
    text = load_body_text(html_path)
    char_count = len(text)
    word_count = len(text.split())
    return char_count, word_count


def sublinks_match_label(g_layout, s_layout, g_poems, s_poems):
    if g_layout == "missing" or s_layout == "missing":
        return "missing_page"
    if g_layout != s_layout:
        return "layout_mismatch"
    if g_layout == "hub" and s_layout == "hub":
        g_n = int(g_poems) if g_poems not in (None, "") else None
        s_n = int(s_poems) if s_poems not in (None, "") else None
        if g_n is None or s_n is None:
            return "missing_page"
        return "match" if g_n == s_n else "mismatch"
    return "both_inline"


def main():
    with open(OUTPUT / "poet_pairs.csv", encoding="utf-8") as f:
        pairs = list(csv.DictReader(f))

    out_rows = []
    for p in pairs:
        g_path = DATA_RAW / "gurmukhi" / p["gurmukhi_href"]
        s_path = DATA_RAW / "shahmukhi" / p["shahmukhi_href"]

        g_metrics = metrics_for(g_path)
        s_metrics = metrics_for(s_path)

        row = {
            "gurmukhi_name_raw": p["gurmukhi_name_raw"],
            "shahmukhi_name_raw": p["shahmukhi_name_raw"],
            "gurmukhi_href": p["gurmukhi_href"],
            "shahmukhi_href": p["shahmukhi_href"],
            "page_layout_gurmukhi": p["page_layout_gurmukhi"],
            "page_layout_shahmukhi": p["page_layout_shahmukhi"],
            "poem_sublinks_gurmukhi": p["poem_count_gurmukhi"],
            "poem_sublinks_shahmukhi": p["poem_count_shahmukhi"],
            "sublinks_match": sublinks_match_label(
                p["page_layout_gurmukhi"], p["page_layout_shahmukhi"],
                p["poem_count_gurmukhi"], p["poem_count_shahmukhi"],
            ),
            "gurmukhi_char_count": "",
            "shahmukhi_char_count": "",
            "gurmukhi_word_count": "",
            "shahmukhi_word_count": "",
            "char_ratio_shahmukhi_over_gurmukhi": "",
            "word_ratio_shahmukhi_over_gurmukhi": "",
            "high_divergence": "",
            "note": "",
        }

        if g_metrics is None or s_metrics is None:
            row["note"] = "one or both pages not cached (fetch failure) -- ratio not computable"
            out_rows.append(row)
            continue

        g_chars, g_words = g_metrics
        s_chars, s_words = s_metrics
        row["gurmukhi_char_count"] = g_chars
        row["shahmukhi_char_count"] = s_chars
        row["gurmukhi_word_count"] = g_words
        row["shahmukhi_word_count"] = s_words

        if g_words == 0:
            row["note"] = "gurmukhi word count is zero -- ratio not computable"
            out_rows.append(row)
            continue

        char_ratio = s_chars / g_chars if g_chars else None
        word_ratio = s_words / g_words

        row["char_ratio_shahmukhi_over_gurmukhi"] = round(char_ratio, 4) if char_ratio is not None else ""
        row["word_ratio_shahmukhi_over_gurmukhi"] = round(word_ratio, 4)
        row["high_divergence"] = not (LOW_RATIO <= word_ratio <= HIGH_RATIO)

        out_rows.append(row)

    out_path = OUTPUT / "divergence_metrics.csv"
    fieldnames = [
        "gurmukhi_name_raw", "shahmukhi_name_raw", "gurmukhi_href", "shahmukhi_href",
        "page_layout_gurmukhi", "page_layout_shahmukhi",
        "poem_sublinks_gurmukhi", "poem_sublinks_shahmukhi", "sublinks_match",
        "gurmukhi_char_count", "shahmukhi_char_count",
        "gurmukhi_word_count", "shahmukhi_word_count",
        "char_ratio_shahmukhi_over_gurmukhi", "word_ratio_shahmukhi_over_gurmukhi",
        "high_divergence", "note",
    ]
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    computable = [r for r in out_rows if r["word_ratio_shahmukhi_over_gurmukhi"] != ""]
    not_computable = [r for r in out_rows if r["word_ratio_shahmukhi_over_gurmukhi"] == ""]

    sublink_counts = {}
    for r in out_rows:
        sublink_counts[r["sublinks_match"]] = sublink_counts.get(r["sublinks_match"], 0) + 1

    ratios = sorted(r["word_ratio_shahmukhi_over_gurmukhi"] for r in computable)
    q = statistics.quantiles(ratios, n=4) if len(ratios) >= 2 else [ratios[0]] * 3

    def divergence_score(r):
        ratio = r["word_ratio_shahmukhi_over_gurmukhi"]
        return max(ratio, 1 / ratio) if ratio > 0 else float("inf")

    ranked = sorted(computable, key=divergence_score, reverse=True)

    high_div_count = sum(1 for r in out_rows if r["high_divergence"] is True)

    print(f"Wrote {out_path} ({len(out_rows)} rows, {len(computable)} with computable ratios, "
          f"{len(not_computable)} not computable)")

    print("\n=== SUBLINK MATCH BREAKDOWN ===")
    for label, count in sorted(sublink_counts.items(), key=lambda x: -x[1]):
        print(f"  {label}: {count}")

    print(f"\n=== WORD-RATIO DISTRIBUTION (n={len(ratios)}) ===")
    print(f"  min: {ratios[0]:.4f}")
    print(f"  Q1:  {q[0]:.4f}")
    print(f"  median (Q2): {q[1]:.4f}")
    print(f"  Q3:  {q[2]:.4f}")
    print(f"  max: {ratios[-1]:.4f}")
    print(f"  high_divergence flagged (outside {LOW_RATIO}-{HIGH_RATIO}): {high_div_count} / {len(out_rows)}")

    print(f"\n=== TOP 20 BY DIVERGENCE ===")
    for i, r in enumerate(ranked[:20], start=1):
        print(f"  {i}. {r['gurmukhi_name_raw']} -- word_ratio={r['word_ratio_shahmukhi_over_gurmukhi']}, "
              f"gurmukhi_words={r['gurmukhi_word_count']}, shahmukhi_words={r['shahmukhi_word_count']}, "
              f"layout=({r['page_layout_gurmukhi']}/{r['page_layout_shahmukhi']})")

    print(f"\n=== SHARAF GROUND-TRUTH CHECK ===")
    sharaf_rows = [r for r in out_rows if "sharaf" in r["gurmukhi_name_raw"].lower()
                   and "babu firoz din" in r["gurmukhi_name_raw"].lower()]
    if not sharaf_rows:
        print("  Babu Firoz Din Sharaf not found in poet_pairs.csv")
    else:
        for r in sharaf_rows:
            if r["word_ratio_shahmukhi_over_gurmukhi"] == "":
                print(f"  {r['gurmukhi_name_raw']}: ratio not computable ({r['note']})")
                continue
            rank = ranked.index(r) + 1
            print(f"  {r['gurmukhi_name_raw']}: rank {rank} of {len(ranked)} by divergence")
            print(f"    word_ratio={r['word_ratio_shahmukhi_over_gurmukhi']}, "
                  f"gurmukhi_words={r['gurmukhi_word_count']}, shahmukhi_words={r['shahmukhi_word_count']}")
            print(f"    page_layout: gurmukhi={r['page_layout_gurmukhi']}, shahmukhi={r['page_layout_shahmukhi']}")
            if r["page_layout_gurmukhi"] != r["page_layout_shahmukhi"]:
                print(f"    NOTE: the two sides use different page layouts (hub vs inline). "
                      f"This alone is sufficient to produce a length mismatch, independent of "
                      f"whether the underlying poem wording also differs.")

    top20_layout_mismatch = sum(
        1 for r in ranked[:20] if r["page_layout_gurmukhi"] != r["page_layout_shahmukhi"]
    )

    sharaf_block = "Babu Firoz Din Sharaf not found in poet_pairs.csv."
    for r in sharaf_rows:
        if r["word_ratio_shahmukhi_over_gurmukhi"] == "":
            sharaf_block = f"Ratio not computable ({r['note']})."
            break
        rank = ranked.index(r) + 1
        sharaf_block = (
            f"Rank {rank} of {len(ranked)} by divergence score. "
            f"word_ratio={r['word_ratio_shahmukhi_over_gurmukhi']} "
            f"(gurmukhi_words={r['gurmukhi_word_count']}, shahmukhi_words={r['shahmukhi_word_count']}). "
            f"page_layout: gurmukhi={r['page_layout_gurmukhi']}, shahmukhi={r['page_layout_shahmukhi']}."
        )
        if r["page_layout_gurmukhi"] != r["page_layout_shahmukhi"]:
            sharaf_block += (
                " The two sides use different page layouts (hub vs inline), which by itself "
                "is sufficient to produce a length mismatch independent of whether the "
                "underlying poem wording also differs. Sharaf's high rank confirms the metric "
                "picks up *some* real signal, but does not by itself confirm that the signal is "
                "specifically a wording difference rather than this structural one."
            )

    top20_lines = "\n".join(
        f"{i}. {r['gurmukhi_name_raw']} -- word_ratio={r['word_ratio_shahmukhi_over_gurmukhi']}, "
        f"gurmukhi_words={r['gurmukhi_word_count']}, shahmukhi_words={r['shahmukhi_word_count']}, "
        f"layout=({r['page_layout_gurmukhi']}/{r['page_layout_shahmukhi']})"
        for i, r in enumerate(ranked[:20], start=1)
    )

    sublink_lines = "\n".join(
        f"- {label}: {count}" for label, count in sorted(sublink_counts.items(), key=lambda x: -x[1])
    )

    methodology = f"""# Divergence Metrics -- Methodology

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

{sublink_lines}

`layout_mismatch` means the two sides use different page layouts (one hub,
one inline) -- these pairs are structurally incomparable on sub-link count,
and, per the scope limitation above, are also the pairs most likely to show
large length differences for reasons unrelated to wording.

## Word-ratio distribution (n={len(ratios)})

- min: {ratios[0]:.4f}
- Q1: {q[0]:.4f}
- median: {q[1]:.4f}
- Q3: {q[2]:.4f}
- max: {ratios[-1]:.4f}
- flagged high_divergence (outside {LOW_RATIO}-{HIGH_RATIO}): {high_div_count} / {len(out_rows)}

## Top 20 pairs by divergence

Ranked by max(word_ratio, 1/word_ratio), so both large expansions and large
contractions from Gurmukhi to Shahmukhi rank highly.

{top20_lines}

{top20_layout_mismatch} of these top 20 are layout_mismatch pairs (one hub,
one inline) -- consistent with the scope limitation above: a meaningful share
of the largest length differences in this ranking coincide with a structural
difference between the two pages, not necessarily a wording difference. This
is an observed pattern in our own data (the page_layout columns), not an
inference about why any specific pair diverges.

## Ground-truth check: Babu Firoz Din Sharaf

{sharaf_block}

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
"""

    methodology_path = OUTPUT / "DIVERGENCE_METHODOLOGY.md"
    methodology_path.write_text(methodology, encoding="utf-8")
    print(f"\nWrote {methodology_path}")


if __name__ == "__main__":
    main()
