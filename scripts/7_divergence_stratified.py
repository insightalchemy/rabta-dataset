import csv
import statistics

from common import OUTPUT

LOW_RATIO = 0.8
HIGH_RATIO = 1.25


def load_rows():
    with open(OUTPUT / "divergence_metrics.csv", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def ratio_stats(rows):
    ratios = sorted(float(r["word_ratio_shahmukhi_over_gurmukhi"]) for r in rows
                     if r["word_ratio_shahmukhi_over_gurmukhi"] != "")
    if not ratios:
        return None
    q = statistics.quantiles(ratios, n=4) if len(ratios) >= 2 else [ratios[0]] * 3
    outside = sum(1 for r in ratios if not (LOW_RATIO <= r <= HIGH_RATIO))
    return {
        "n": len(ratios),
        "min": ratios[0],
        "q1": q[0],
        "median": q[1],
        "q3": q[2],
        "max": ratios[-1],
        "outside": outside,
    }


def fmt_row(r):
    return (f"{r['gurmukhi_name_raw']} -- word_ratio={r['word_ratio_shahmukhi_over_gurmukhi']}, "
            f"gurmukhi_words={r['gurmukhi_word_count']}, shahmukhi_words={r['shahmukhi_word_count']}")


def main():
    rows = load_rows()

    inline_rows = [r for r in rows if r["sublinks_match"] == "both_inline"]
    layout_mismatch_rows = [r for r in rows if r["sublinks_match"] == "layout_mismatch"]
    hub_hub_match_rows = [r for r in rows if r["sublinks_match"] == "match"]
    hub_hub_mismatch_rows = [r for r in rows if r["sublinks_match"] == "mismatch"]
    missing_rows = [r for r in rows if r["sublinks_match"] == "missing_page"]

    out_path = OUTPUT / "divergence_inline_only.csv"
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(inline_rows[0].keys()))
        writer.writeheader()
        writer.writerows(inline_rows)

    stats = ratio_stats(inline_rows)
    ranked = sorted(
        inline_rows,
        key=lambda r: max(float(r["word_ratio_shahmukhi_over_gurmukhi"]), 1 / float(r["word_ratio_shahmukhi_over_gurmukhi"])),
        reverse=True,
    )
    closest_to_one = sorted(
        inline_rows,
        key=lambda r: abs(float(r["word_ratio_shahmukhi_over_gurmukhi"]) - 1.0),
    )

    print(f"Wrote {out_path} ({len(inline_rows)} rows)")
    print(f"\n=== INLINE-ONLY WORD-RATIO DISTRIBUTION (n={stats['n']}) ===")
    print(f"  min: {stats['min']:.4f}")
    print(f"  Q1:  {stats['q1']:.4f}")
    print(f"  median: {stats['median']:.4f}")
    print(f"  Q3:  {stats['q3']:.4f}")
    print(f"  max: {stats['max']:.4f}")
    print(f"  outside {LOW_RATIO}-{HIGH_RATIO}: {stats['outside']} / {stats['n']}")

    print(f"\n=== 20 LARGEST DIVERGENCES (inline-only subset) ===")
    for i, r in enumerate(ranked[:20], start=1):
        print(f"  {i}. {fmt_row(r)}")

    print(f"\n=== 20 SMALLEST DIVERGENCES, ratio closest to 1.0 (inline-only subset) ===")
    for i, r in enumerate(closest_to_one[:20], start=1):
        print(f"  {i}. {fmt_row(r)}")

    print(f"\n=== NOT COMPARABLE TO INLINE SUBSET -- shown separately, not ranked together ===")
    print(f"\n--- layout_mismatch (one side hub, one side inline): {len(layout_mismatch_rows)} pairs ---")
    for r in sorted(layout_mismatch_rows, key=lambda r: r["gurmukhi_name_raw"]):
        print(f"  {fmt_row(r)}, layout=({r['page_layout_gurmukhi']}/{r['page_layout_shahmukhi']})")

    print(f"\n--- hub-hub, sub-link counts MATCH: {len(hub_hub_match_rows)} pairs ---")
    for r in sorted(hub_hub_match_rows, key=lambda r: r["gurmukhi_name_raw"]):
        print(f"  {fmt_row(r)}, sublinks=({r['poem_sublinks_gurmukhi']}/{r['poem_sublinks_shahmukhi']})")

    print(f"\n--- hub-hub, sub-link counts DIFFER: {len(hub_hub_mismatch_rows)} pairs ---")
    for r in sorted(hub_hub_mismatch_rows, key=lambda r: r["gurmukhi_name_raw"]):
        print(f"  {fmt_row(r)}, sublinks=({r['poem_sublinks_gurmukhi']}/{r['poem_sublinks_shahmukhi']})")

    print(f"\n--- missing page: {len(missing_rows)} pair(s) ---")
    for r in missing_rows:
        print(f"  {r['gurmukhi_name_raw']}: {r['note']}")

    write_methodology_section(stats, ranked, closest_to_one, layout_mismatch_rows,
                               hub_hub_match_rows, hub_hub_mismatch_rows, missing_rows)


MARKER = "## Stratification: the layout confound"


def write_methodology_section(stats, ranked, closest_to_one, layout_mismatch_rows,
                               hub_hub_match_rows, hub_hub_mismatch_rows, missing_rows):
    top20_lines = "\n".join(f"{i}. {fmt_row(r)}" for i, r in enumerate(ranked[:20], start=1))
    bottom20_lines = "\n".join(f"{i}. {fmt_row(r)}" for i, r in enumerate(closest_to_one[:20], start=1))

    section = f"""{MARKER}

The first pass at this analysis (the "Top 20 by divergence" ranking earlier
in this document) ranked all 211 pairs together regardless of page layout.
Babu Firoz Din Sharaf, our one ground-truth case of known wording
divergence, ranked 17th of 210 in that pass. On inspection, Sharaf's pair
turned out to be layout-mismatched: his Gurmukhi page is hub-layout (a
table of contents linking to sub-pages) and his Shahmukhi page is
inline-layout (full text embedded directly). That structural difference
alone is enough to produce a large length gap, independent of whether the
underlying wording differs at all -- so his rank of 17 did not validate the
metric. It happened to also flag {len(layout_mismatch_rows)} other pairs sharing the
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

- **inline/inline** ({stats['n']} pairs) -- both sides have poem text embedded
  directly on the cached page. These are the only pairs where a length
  ratio plausibly reflects the compared pages' actual content rather than
  architecture. Output: output/divergence_inline_only.csv.
- **hub/inline** ({len(layout_mismatch_rows)} pairs) -- one side is a table of contents,
  the other is full text. Not comparable by this method; reported
  separately, not ranked against the inline subset.
- **hub/hub, sub-link counts match** ({len(hub_hub_match_rows)} pairs) and **hub/hub, sub-link
  counts differ** ({len(hub_hub_mismatch_rows)} pairs) -- both sides are tables of contents, so the
  text compared is bio + link-title text, not poem content. Also not
  comparable to the inline subset, and kept separate from each other since
  a matching sub-link count is at least a weak structural signal the
  mismatched group lacks.
- **missing page** ({len(missing_rows)} pair) -- Avtar Singh Pash, excluded entirely
  (confirmed server-side fetch failure, not an absence of content).

### Inline/inline word-ratio distribution (n={stats['n']})

- min: {stats['min']:.4f}
- Q1: {stats['q1']:.4f}
- median: {stats['median']:.4f}
- Q3: {stats['q3']:.4f}
- max: {stats['max']:.4f}
- outside 0.8-1.25: {stats['outside']} / {stats['n']}

Even restricted to the cleanest, most directly comparable subset, over a
third of pairs fall outside the 0.8-1.25 band. This does not confirm
different wording for any specific pair -- it means the inline/inline
subset still contains real candidates for human review, now without the
layout confound.

### 20 largest divergences, inline/inline subset only

{top20_lines}

### 20 smallest divergences (ratio closest to 1.0), inline/inline subset only

{bottom20_lines}

### Why hub-layout pairs still can't be properly compared

The text available for a hub-layout page is the poet's bio plus the table
of contents of poem/collection titles -- not the poems themselves, which
live on sub-pages this pipeline never fetched. Making a hub-layout pair
genuinely comparable requires fetching those sub-pages and using their
concatenated text instead of the landing page's table of contents. That is
a separate, explicitly network-touching step gated on its own confirmation
(see the fetch-count check before any such fetch is run), not something
resolved by re-analysis of already-cached data.
"""

    path = OUTPUT / "DIVERGENCE_METHODOLOGY.md"
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        if MARKER in existing:
            existing = existing[: existing.index(MARKER)]
        content = existing.rstrip("\n") + "\n\n" + section
    else:
        content = section
    path.write_text(content, encoding="utf-8")
    print(f"\nUpdated {path}")


if __name__ == "__main__":
    main()
