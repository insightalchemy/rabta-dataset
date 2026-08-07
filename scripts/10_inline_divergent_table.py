import csv

from common import OUTPUT


def main():
    with open(OUTPUT / "divergence_inline_only.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    divergent = [r for r in rows if r["high_divergence"] == "True"]
    divergent.sort(key=lambda r: float(r["word_ratio_shahmukhi_over_gurmukhi"]))

    gurmukhi_longer = 0
    shahmukhi_longer = 0
    table_rows = []
    for r in divergent:
        g_words = int(r["gurmukhi_word_count"])
        s_words = int(r["shahmukhi_word_count"])
        longer = "gurmukhi" if g_words > s_words else "shahmukhi"
        if longer == "gurmukhi":
            gurmukhi_longer += 1
        else:
            shahmukhi_longer += 1
        table_rows.append((r["gurmukhi_name_raw"], g_words, s_words,
                            r["word_ratio_shahmukhi_over_gurmukhi"], longer))

    print(f"=== PART 4: {len(divergent)} DIVERGENT INLINE/INLINE PAIRS ===\n")
    print(f"{'name':35s} {'gurmukhi_words':>14s} {'shahmukhi_words':>15s} {'ratio':>8s}  longer_side")
    for name, g, s, ratio, longer in table_rows:
        print(f"{name:35s} {g:14d} {s:15d} {ratio:>8s}  {longer}")

    print(f"\ngurmukhi longer: {gurmukhi_longer} / {len(divergent)}")
    print(f"shahmukhi longer: {shahmukhi_longer} / {len(divergent)}")

    return table_rows, gurmukhi_longer, shahmukhi_longer


if __name__ == "__main__":
    main()
