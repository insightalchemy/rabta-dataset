import csv
import glob

from bs4 import BeautifulSoup

from common import DATA_PROCESSED, DATA_RAW, LOGS, OUTPUT, extract_content_links, now_iso

NAV_PHRASES = [
    "☰ Home Punjabi Poetry Sufi Poetry Urdu Poetry Hindi Poetry Translations",
    "☰ Home Punjabi Poetry Sufi Poetry Hindi Poetry Translations",
    "Home Punjabi Poetry Sufi Poetry Urdu Poetry Hindi Poetry Translations",
    "Home Punjabi Poetry Sufi Poetry Hindi Poetry Translations",
]
FOOTER_PHRASES = ["Contact Us...", "Contact Us"]


def load_body_text(soup_copy):
    for tag in soup_copy(["script", "style"]):
        tag.decompose()
    header = soup_copy.find(class_="pk-header-wrapper")
    if header:
        header.decompose()
    footer = soup_copy.find("footer")
    if footer:
        footer.decompose()
    text = soup_copy.get_text(" ", strip=True)
    for phrase in NAV_PHRASES + FOOTER_PHRASES:
        text = text.replace(phrase, " ")
    return " ".join(text.split())


def analyze_page(path, script, href):
    with open(path, encoding="utf-8") as f:
        html = f.read()
    soup_for_links = BeautifulSoup(html, "html.parser")
    links = extract_content_links(soup_for_links, script, href)
    layout = "hub" if len(links) > 0 else "inline"

    soup_for_text = BeautifulSoup(html, "html.parser")
    text = load_body_text(soup_for_text)
    words = len(text.split())
    chars = len(text)
    return layout, len(links), words, chars


def main():
    with open(DATA_PROCESSED / "poets_gurmukhi.csv", encoding="utf-8") as f:
        g_poets = list(csv.DictReader(f))
    with open(DATA_PROCESSED / "poets_shahmukhi.csv", encoding="utf-8") as f:
        s_poets = list(csv.DictReader(f))

    with open(OUTPUT / "poet_pairs.csv", encoding="utf-8") as f:
        old_pairs = list(csv.DictReader(f))
    with open(OUTPUT / "unmatched_gurmukhi.csv", encoding="utf-8") as f:
        old_unmatched_g = list(csv.DictReader(f))
    with open(OUTPUT / "unmatched_shahmukhi.csv", encoding="utf-8") as f:
        old_unmatched_s = list(csv.DictReader(f))
    with open(OUTPUT / "divergence_metrics.csv", encoding="utf-8") as f:
        old_divergence = {r["gurmukhi_href"]: r for r in csv.DictReader(f)}

    old_layout_g = {}
    old_words_g = {}
    for r in old_pairs:
        old_layout_g[r["gurmukhi_href"]] = r["page_layout_gurmukhi"]
    for r in old_unmatched_g:
        old_layout_g[r["href"]] = r["page_layout"]

    old_layout_s = {}
    for r in old_pairs:
        old_layout_s[r["shahmukhi_href"]] = r["page_layout_shahmukhi"]
    for r in old_unmatched_s:
        old_layout_s[r["href"]] = r["page_layout"]

    old_words_map = {}
    for href, r in old_divergence.items():
        if r["gurmukhi_word_count"] != "":
            old_words_map[("gurmukhi", href)] = int(r["gurmukhi_word_count"])
        if r["shahmukhi_word_count"] != "":
            old_words_map[("shahmukhi", r["shahmukhi_href"])] = int(r["shahmukhi_word_count"])

    print("=== PART 2: RECOMPUTING CLASSIFICATION AND WORD COUNTS ON EXISTING CACHE ===\n")

    new_results = {}
    reclassified = []
    for script, poets in [("gurmukhi", g_poets), ("shahmukhi", s_poets)]:
        for p in poets:
            href = p["href"]
            path = DATA_RAW / script / href
            if not path.exists():
                new_results[(script, href)] = ("missing", 0, None, None)
                continue
            layout, nlinks, words, chars = analyze_page(path, script, href)
            new_results[(script, href)] = (layout, nlinks, words, chars)

            old_layout = old_layout_g.get(href) if script == "gurmukhi" else old_layout_s.get(href)
            if old_layout is not None and old_layout != layout:
                reclassified.append((script, p["name_raw"], href, old_layout, layout, nlinks))

    print(f"Pages reclassified by fixed link-detection: {len(reclassified)}")
    g_reclass = [r for r in reclassified if r[0] == "gurmukhi"]
    s_reclass = [r for r in reclassified if r[0] == "shahmukhi"]
    print(f"  gurmukhi: {len(g_reclass)} (all {set(r[3]+'->'+r[4] for r in g_reclass)})")
    print(f"  shahmukhi: {len(s_reclass)} (all {set(r[3]+'->'+r[4] for r in s_reclass)})")

    word_count_changes = []
    for (script, href), (layout, nlinks, words, chars) in new_results.items():
        old_words = old_words_map.get((script, href))
        if old_words is not None and words is not None and old_words != words:
            word_count_changes.append((script, href, old_words, words))

    print(f"\nPages where the re-run word count differs from the previously published word count: "
          f"{len(word_count_changes)}")
    for c in word_count_changes[:20]:
        print(f"  {c}")
    if not word_count_changes:
        print("  None. The body-text extraction itself (get_text() after stripping nav/header/"
              "footer) was already capturing all text present in the pages we had cached -- it "
              "was not dropping content from fetched pages. The bug is entirely in link "
              "detection: fragment-suffixed hrefs like 'Foo.php#Bar' were invisible to the old "
              "`a[href$=\".php\"]` selector, so pages whose only outbound content links used "
              "that pattern were misclassified as inline, and the sub-pages those links point to "
              "were never fetched at all -- there is no missing text to recover from the pages "
              "already in cache.")

    g_computable = [v for k, v in new_results.items() if k[0] == "gurmukhi" and v[2] is not None]
    s_computable = [v for k, v in new_results.items() if k[0] == "shahmukhi" and v[2] is not None]
    g_under500 = sum(1 for v in g_computable if v[2] < 500)
    s_under500 = sum(1 for v in s_computable if v[2] < 500)
    g_under1000 = sum(1 for v in g_computable if v[2] < 1000)
    s_under1000 = sum(1 for v in s_computable if v[2] < 1000)

    print(f"\nRecomputed under-500-words: gurmukhi {g_under500}/{len(g_computable)} "
          f"({100*g_under500/len(g_computable):.1f}%), shahmukhi {s_under500}/{len(s_computable)} "
          f"({100*s_under500/len(s_computable):.1f}%)")
    print(f"Recomputed under-1000-words: gurmukhi {g_under1000}/{len(g_computable)} "
          f"({100*g_under1000/len(g_computable):.1f}%), shahmukhi {s_under1000}/{len(s_computable)} "
          f"({100*s_under1000/len(s_computable):.1f}%)")
    print("These percentages are numerically the same as previously published (word counts did "
          "not change on already-cached pages), but their VALIDITY as a content-depth measure is "
          "now known to be wrong for every reclassified page: a page can be 'thin' by word count "
          "purely because its actual content lives on an unfetched sub-page, not because the "
          "poet's page is genuinely short.")

    return {
        "new_results": new_results,
        "reclassified": reclassified,
        "g_reclass": g_reclass,
        "s_reclass": s_reclass,
        "word_count_changes": word_count_changes,
        "g_under500": g_under500, "g_total": len(g_computable),
        "s_under500": s_under500, "s_total": len(s_computable),
        "g_under1000": g_under1000, "s_under1000": s_under1000,
    }


if __name__ == "__main__":
    main()
