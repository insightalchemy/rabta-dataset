import csv
import statistics

from common import OUTPUT, now_iso

LOW_RATIO = 0.8
HIGH_RATIO = 1.25
MARKER = "## Full-scale corrected results (all sub-pages fetched)"


def main():
    with open(OUTPUT / "coverage_full_scale.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    comparable = [r for r in rows if r["comparable"] == "True"]
    not_comparable = [r for r in rows if r["comparable"] != "True"]
    incomplete = [r for r in comparable if not (r["gurmukhi_complete"] == "True" and r["shahmukhi_complete"] == "True")]

    ratios = sorted(float(r["word_ratio_shahmukhi_over_gurmukhi"]) for r in comparable)
    q = statistics.quantiles(ratios, n=4)
    outside = sum(1 for r in ratios if not (LOW_RATIO <= r <= HIGH_RATIO))

    divergent = [r for r in comparable if r["high_divergence"] == "True"]
    g_longer = [r for r in divergent if int(r["gurmukhi_total_words"]) > int(r["shahmukhi_total_words"])]
    s_longer = [r for r in divergent if int(r["shahmukhi_total_words"]) > int(r["gurmukhi_total_words"])]

    sharaf = next(r for r in comparable if "Babu Firoz Din Sharaf" in r["gurmukhi_name_raw"])
    sharaf_ratio = float(sharaf["word_ratio_shahmukhi_over_gurmukhi"])
    sharaf_rank = ratios.index(sharaf_ratio) + 1

    def divergence_score(r):
        ratio = float(r["word_ratio_shahmukhi_over_gurmukhi"])
        return max(ratio, 1 / ratio) if ratio > 0 else float("inf")

    ranked = sorted(comparable, key=divergence_score, reverse=True)
    closest = sorted(comparable, key=lambda r: abs(float(r["word_ratio_shahmukhi_over_gurmukhi"]) - 1.0))

    top20_lines = "\n".join(
        f"{i}. {r['gurmukhi_name_raw']}: gurmukhi={r['gurmukhi_total_words']}, "
        f"shahmukhi={r['shahmukhi_total_words']}, ratio={r['word_ratio_shahmukhi_over_gurmukhi']}"
        + (" [incomplete data]" if r in incomplete else "")
        for i, r in enumerate(ranked[:20], start=1)
    )
    bottom20_lines = "\n".join(
        f"{i}. {r['gurmukhi_name_raw']}: gurmukhi={r['gurmukhi_total_words']}, "
        f"shahmukhi={r['shahmukhi_total_words']}, ratio={r['word_ratio_shahmukhi_over_gurmukhi']}"
        for i, r in enumerate(closest[:20], start=1)
    )
    s_longer_lines = "\n".join(
        f"- {r['gurmukhi_name_raw']}: gurmukhi={r['gurmukhi_total_words']}, "
        f"shahmukhi={r['shahmukhi_total_words']}, ratio={r['word_ratio_shahmukhi_over_gurmukhi']}"
        + (" [Shahmukhi side has an incomplete sub-page set -- treat with extra caution]"
           if r in incomplete else "")
        for r in s_longer
    )
    not_comparable_lines = "\n".join(
        f"- {r['gurmukhi_name_raw']}: gurmukhi_words={r['gurmukhi_total_words'] or 'n/a'}, "
        f"shahmukhi_words={r['shahmukhi_total_words'] or 'n/a'}"
        for r in not_comparable
    )
    incomplete_lines = "\n".join(
        f"- {r['gurmukhi_name_raw']}: gurmukhi_complete={r['gurmukhi_complete']}, "
        f"shahmukhi_complete={r['shahmukhi_complete']}"
        for r in incomplete
    )

    section = f"""{MARKER}

Generated: {now_iso()}

**This supersedes the partial-coverage results elsewhere in this document.**
Following the correction described in output/CORRECTION.md, all 1,926
previously-missing sub-pages were fetched (1,922 succeeded, 4 failed --
see logs/subpage_fetch_status.log). Word counts below are now the total
content of each poet's page plus all of its direct sub-pages, on both
sides, for both scripts -- not a landing-page-only or proxy measure.

### 1. Pairs now properly comparable

**{len(comparable)} of {len(rows)}** pairs are comparable on a unified
word-count basis (was 77 before this fetch). Not comparable:

{not_comparable_lines}

{len(incomplete)} comparable pairs rely on a page with a known-incomplete
sub-page set (one of the 4 sub-page fetch failures affects them directly):

{incomplete_lines}

These are included in all statistics below but should be read as a lower
bound on that side's true word count, not an exact figure.

### 2 & 3. Word-ratio distribution (n={len(comparable)})

- min: {ratios[0]:.4f}
- Q1: {q[0]:.4f}
- median: {q[1]:.4f}
- Q3: {q[2]:.4f}
- max: {ratios[-1]:.4f}
- outside {LOW_RATIO}-{HIGH_RATIO}: **{outside} / {len(comparable)} ({100*outside/len(comparable):.1f}%)**

### 4. Directional split -- does 100% Gurmukhi-longer hold at full scale?

**No. It breaks down.** Of {len(divergent)} divergent pairs:
- Gurmukhi longer: {len(g_longer)} ({100*len(g_longer)/len(divergent):.1f}%)
- Shahmukhi longer: {len(s_longer)} ({100*len(s_longer)/len(divergent):.1f}%)

The Shahmukhi-longer pairs, individually -- these are the most
analytically interesting pairs in the dataset, exactly the cases the
partial-coverage analysis could not see:

{s_longer_lines}

### 5. Where Sharaf ranks now

Sharaf's corrected ratio is **{sharaf_ratio:.4f}**, ranking **{sharaf_rank}
of {len(ratios)}** (1 = most Gurmukhi-heavy). He is no longer the single
most extreme case in the dataset -- {sharaf_rank - 1} pairs now show a more
extreme divergence than his, visible only because their sub-pages are now
fetched. He remains a clear, real outlier, just not the most extreme one.

### 6. 20 largest and 20 smallest divergences

Largest (ranked by max(ratio, 1/ratio)):

{top20_lines}

Smallest (ratio closest to 1.0):

{bottom20_lines}

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
"""

    for path_name in ["METHODOLOGY.md", "DIVERGENCE_METHODOLOGY.md"]:
        path = OUTPUT / path_name
        existing = path.read_text(encoding="utf-8")
        if MARKER in existing:
            existing = existing[: existing.index(MARKER)]
        content = existing.rstrip("\n") + "\n\n" + section
        path.write_text(content, encoding="utf-8")
        print(f"Updated {path}")


if __name__ == "__main__":
    main()
