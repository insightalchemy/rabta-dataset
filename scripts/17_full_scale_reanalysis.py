import csv
import statistics

from bs4 import BeautifulSoup

from common import DATA_PROCESSED, DATA_RAW, OUTPUT, extract_content_links, now_iso

NAV_PHRASES = [
    "☰ Home Punjabi Poetry Sufi Poetry Urdu Poetry Hindi Poetry Translations",
    "☰ Home Punjabi Poetry Sufi Poetry Hindi Poetry Translations",
    "Home Punjabi Poetry Sufi Poetry Urdu Poetry Hindi Poetry Translations",
    "Home Punjabi Poetry Sufi Poetry Hindi Poetry Translations",
]
FOOTER_PHRASES = ["Contact Us...", "Contact Us"]

LOW_RATIO = 0.8
HIGH_RATIO = 1.25


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


def poet_total(script, href):
    """Returns (total_words, total_chars, complete) where complete=False if
    the landing page is a hub page and at least one of its direct sub-links
    could not be found in the sub-page cache."""
    landing_path = DATA_RAW / script / href
    if not landing_path.exists():
        return None, None, False

    with open(landing_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    links = extract_content_links(soup, script, href)

    texts = [load_body_text(landing_path)]
    complete = True
    for link in sorted(links):
        sub_path = DATA_RAW / "subpages" / script / link
        if sub_path.exists():
            texts.append(load_body_text(sub_path))
        else:
            complete = False

    combined = " ".join(texts)
    return len(combined.split()), len(combined), complete


def main():
    with open(OUTPUT / "poet_pairs.csv", encoding="utf-8") as f:
        pairs = list(csv.DictReader(f))

    rows = []
    for p in pairs:
        g_words, g_chars, g_complete = poet_total("gurmukhi", p["gurmukhi_href"])
        s_words, s_chars, s_complete = poet_total("shahmukhi", p["shahmukhi_href"])

        comparable = g_words is not None and s_words is not None and g_words > 0
        ratio = (s_words / g_words) if comparable else None

        rows.append({
            "gurmukhi_name_raw": p["gurmukhi_name_raw"],
            "gurmukhi_href": p["gurmukhi_href"],
            "shahmukhi_href": p["shahmukhi_href"],
            "gurmukhi_total_words": g_words if g_words is not None else "",
            "shahmukhi_total_words": s_words if s_words is not None else "",
            "gurmukhi_total_chars": g_chars if g_chars is not None else "",
            "shahmukhi_total_chars": s_chars if s_chars is not None else "",
            "gurmukhi_complete": g_complete,
            "shahmukhi_complete": s_complete,
            "comparable": comparable,
            "word_ratio_shahmukhi_over_gurmukhi": round(ratio, 4) if ratio is not None else "",
            "high_divergence": (not (LOW_RATIO <= ratio <= HIGH_RATIO)) if ratio is not None else "",
        })

    out_path = OUTPUT / "coverage_full_scale.csv"
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    comparable_rows = [r for r in rows if r["comparable"]]
    not_comparable = [r for r in rows if not r["comparable"]]
    incomplete = [r for r in comparable_rows if not (r["gurmukhi_complete"] and r["shahmukhi_complete"])]

    print(f"Wrote {out_path} ({len(rows)} rows)")
    print(f"\n1. COMPARABLE PAIRS: {len(comparable_rows)} / {len(rows)} (was 77 before this fetch)")
    print(f"   Not comparable: {len(not_comparable)}")
    for r in not_comparable:
        print(f"     {r['gurmukhi_name_raw']}: gurmukhi_words={r['gurmukhi_total_words']}, "
              f"shahmukhi_words={r['shahmukhi_total_words']}")
    print(f"   Of the comparable pairs, {len(incomplete)} rely on at least one page whose sub-page "
          f"set is known incomplete (a direct sub-link failed to fetch -- 4 known failures "
          f"across the whole corpus). These are included but flagged gurmukhi_complete/"
          f"shahmukhi_complete=False in the CSV; treat their ratio as a lower bound on true "
          f"content, not exact.")
    for r in incomplete:
        print(f"     {r['gurmukhi_name_raw']}: gurmukhi_complete={r['gurmukhi_complete']}, "
              f"shahmukhi_complete={r['shahmukhi_complete']}")

    ratios = sorted(r["word_ratio_shahmukhi_over_gurmukhi"] for r in comparable_rows)
    q = statistics.quantiles(ratios, n=4)
    outside = sum(1 for r in ratios if not (LOW_RATIO <= r <= HIGH_RATIO))

    print(f"\n2. WORD-RATIO DISTRIBUTION (n={len(ratios)})")
    print(f"   min: {ratios[0]:.4f}")
    print(f"   Q1: {q[0]:.4f}")
    print(f"   median: {q[1]:.4f}")
    print(f"   Q3: {q[2]:.4f}")
    print(f"   max: {ratios[-1]:.4f}")

    print(f"\n3. OUTSIDE 0.8-1.25: {outside} / {len(ratios)} ({100*outside/len(ratios):.1f}%)")

    divergent = [r for r in comparable_rows if r["high_divergence"]]
    g_longer = [r for r in divergent if r["gurmukhi_total_words"] > r["shahmukhi_total_words"]]
    s_longer = [r for r in divergent if r["shahmukhi_total_words"] > r["gurmukhi_total_words"]]

    print(f"\n4. DIRECTIONAL SPLIT (n={len(divergent)} divergent pairs)")
    print(f"   Gurmukhi longer: {len(g_longer)} ({100*len(g_longer)/len(divergent):.1f}%)")
    print(f"   Shahmukhi longer: {len(s_longer)} ({100*len(s_longer)/len(divergent):.1f}%)")
    if s_longer:
        print(f"   Shahmukhi-longer pairs (individually):")
        for r in s_longer:
            print(f"     {r['gurmukhi_name_raw']}: gurmukhi={r['gurmukhi_total_words']}, "
                  f"shahmukhi={r['shahmukhi_total_words']}, ratio={r['word_ratio_shahmukhi_over_gurmukhi']}")
    else:
        print("   No Shahmukhi-longer pairs found -- the 100% Gurmukhi-longer pattern holds at full scale.")

    sharaf = next((r for r in comparable_rows if "Sharaf" in r["gurmukhi_name_raw"] and "Babu Firoz" in r["gurmukhi_name_raw"]), None)
    if sharaf:
        rank = ratios.index(sharaf["word_ratio_shahmukhi_over_gurmukhi"]) + 1
        percentile = 100 * (rank - 1) / len(ratios)
        print(f"\n5. SHARAF'S RANK: ratio={sharaf['word_ratio_shahmukhi_over_gurmukhi']}, "
              f"rank {rank} of {len(ratios)} (1=lowest), {percentile:.1f}th percentile")

    ranked_by_divergence = sorted(
        comparable_rows,
        key=lambda r: max(r["word_ratio_shahmukhi_over_gurmukhi"], 1 / r["word_ratio_shahmukhi_over_gurmukhi"]) if r["word_ratio_shahmukhi_over_gurmukhi"] > 0 else float("inf"),
        reverse=True,
    )
    closest_to_one = sorted(comparable_rows, key=lambda r: abs(r["word_ratio_shahmukhi_over_gurmukhi"] - 1.0))

    print(f"\n6. 20 LARGEST DIVERGENCES")
    for i, r in enumerate(ranked_by_divergence[:20], start=1):
        print(f"   {i}. {r['gurmukhi_name_raw']}: gurmukhi={r['gurmukhi_total_words']}, "
              f"shahmukhi={r['shahmukhi_total_words']}, ratio={r['word_ratio_shahmukhi_over_gurmukhi']}"
              f"{' [INCOMPLETE]' if not (r['gurmukhi_complete'] and r['shahmukhi_complete']) else ''}")

    print(f"\n   20 SMALLEST DIVERGENCES (ratio closest to 1.0)")
    for i, r in enumerate(closest_to_one[:20], start=1):
        print(f"   {i}. {r['gurmukhi_name_raw']}: gurmukhi={r['gurmukhi_total_words']}, "
              f"shahmukhi={r['shahmukhi_total_words']}, ratio={r['word_ratio_shahmukhi_over_gurmukhi']}")

    return {
        "rows": rows, "comparable_rows": comparable_rows, "not_comparable": not_comparable,
        "incomplete": incomplete, "ratios": ratios, "q": q, "outside": outside,
        "divergent": divergent, "g_longer": g_longer, "s_longer": s_longer,
        "sharaf": sharaf, "ranked_by_divergence": ranked_by_divergence,
        "closest_to_one": closest_to_one,
    }


if __name__ == "__main__":
    main()
