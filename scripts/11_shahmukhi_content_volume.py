import csv

from bs4 import BeautifulSoup

from common import DATA_PROCESSED, DATA_RAW, OUTPUT

NAV_PHRASES = [
    "☰ Home Punjabi Poetry Sufi Poetry Urdu Poetry Hindi Poetry Translations",
    "☰ Home Punjabi Poetry Sufi Poetry Hindi Poetry Translations",
    "Home Punjabi Poetry Sufi Poetry Urdu Poetry Hindi Poetry Translations",
    "Home Punjabi Poetry Sufi Poetry Hindi Poetry Translations",
]
FOOTER_PHRASES = ["Contact Us...", "Contact Us"]

SHAHMUKHI_NAV_HREFS = {
    "indexShahmukhi.php", "PunjabiPoetryShahmukhi.php", "PunjabiSufiPoetryShahmukhi.php",
    "HindiPoetryShahmukhi.php", "TranslationsShahmukhi.php", "pkcontactus.php",
}

BUCKETS = [
    (0, 100), (100, 250), (250, 500), (500, 1000),
    (1000, 2000), (2000, 5000), (5000, float("inf")),
]


def normalize_href_for_page(href, base_host="punjabi-kavita.com"):
    from urllib.parse import urlparse
    if href.startswith("http://") or href.startswith("https://"):
        parsed = urlparse(href)
        host = parsed.netloc.lower().replace("www.", "")
        if host != base_host:
            return None
        href = parsed.path
    return href.lstrip("/")


def count_content_links(soup):
    seen = set()
    for a in soup.select("a[href$='.php']"):
        href = a.get("href")
        norm = normalize_href_for_page(href)
        if norm is None:
            continue
        if norm in SHAHMUKHI_NAV_HREFS:
            continue
        seen.add(norm)
    return len(seen)


def analyze(html_path):
    with open(html_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    sublinks = count_content_links(soup)
    headings = len(soup.find_all(["h1", "h2", "h3", "h4"]))
    paragraphs = len(soup.find_all("p"))

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
    word_count = len(text.split())

    layout = "hub" if sublinks > 0 else "inline"
    return word_count, headings, paragraphs, layout


def bucket_label(lo, hi):
    if hi == float("inf"):
        return f"{lo}+"
    return f"{lo}-{hi - 1}"


def main():
    with open(DATA_PROCESSED / "poets_shahmukhi.csv", encoding="utf-8") as f:
        poets = list(csv.DictReader(f))

    rows = []
    for p in poets:
        html_path = DATA_RAW / "shahmukhi" / p["href"]
        if not html_path.exists():
            rows.append({
                "name_raw": p["name_raw"], "href": p["href"],
                "word_count": "", "heading_count": "", "paragraph_count": "",
                "page_layout": "missing",
            })
            continue
        word_count, headings, paragraphs, layout = analyze(html_path)
        rows.append({
            "name_raw": p["name_raw"], "href": p["href"],
            "word_count": word_count, "heading_count": headings,
            "paragraph_count": paragraphs, "page_layout": layout,
        })

    out_path = OUTPUT / "shahmukhi_content_volume.csv"
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "name_raw", "href", "word_count", "heading_count", "paragraph_count", "page_layout",
        ])
        writer.writeheader()
        writer.writerows(rows)

    computable = [r for r in rows if r["word_count"] != ""]
    missing = [r for r in rows if r["word_count"] == ""]

    print(f"Wrote {out_path} ({len(rows)} rows, {len(computable)} computable, {len(missing)} missing)")

    counts = []
    for lo, hi in BUCKETS:
        n = sum(1 for r in computable if lo <= r["word_count"] < hi)
        counts.append(n)

    print(f"\n=== SHAHMUKHI CONTENT VOLUME HISTOGRAM (n={len(computable)}) ===")
    for (lo, hi), n in zip(BUCKETS, counts):
        pct = 100 * n / len(computable)
        bar = "#" * round(pct / 2)
        print(f"  {bucket_label(lo, hi):>10s} words: {n:4d} ({pct:5.1f}%)  {bar}")

    under_500 = sum(1 for r in computable if r["word_count"] < 500)
    under_1000 = sum(1 for r in computable if r["word_count"] < 1000)
    print(f"\nUnder 500 words:  {under_500} / {len(computable)} ({100*under_500/len(computable):.1f}%)")
    print(f"Under 1000 words: {under_1000} / {len(computable)} ({100*under_1000/len(computable):.1f}%)")

    hub_words = [r["word_count"] for r in computable if r["page_layout"] == "hub"]
    inline_words = [r["word_count"] for r in computable if r["page_layout"] == "inline"]
    print(f"\nBy layout: hub n={len(hub_words)} (median words={sorted(hub_words)[len(hub_words)//2] if hub_words else 'n/a'}), "
          f"inline n={len(inline_words)} (median words={sorted(inline_words)[len(inline_words)//2] if inline_words else 'n/a'})")

    sharaf = next((r for r in rows if r["href"] == "BabuFirozDinSharafShahmukhi.php"), None)
    if sharaf:
        rank = sorted(r["word_count"] for r in computable).index(sharaf["word_count"]) + 1
        print(f"\nSharaf's Shahmukhi word count ({sharaf['word_count']}) ranks {rank} of "
              f"{len(computable)} (1 = shortest).")


if __name__ == "__main__":
    main()
