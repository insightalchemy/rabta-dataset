import csv
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from common import DATA_PROCESSED, DATA_RAW, LOGS, OUTPUT, log_line

MATCH_LOG = LOGS / "match_and_analyze.log"

GURMUKHI_NAV_HREFS = {
    "PunjabiPoetry.php", "Punjabi-Sufi-Poetry.php", "Urdu-Poetry.php",
    "Hindi-Poetry.php", "Translations.php", "pkcontactus.php",
}
SHAHMUKHI_NAV_HREFS = {
    "indexShahmukhi.php", "PunjabiPoetryShahmukhi.php", "PunjabiSufiPoetryShahmukhi.php",
    "HindiPoetryShahmukhi.php", "TranslationsShahmukhi.php", "pkcontactus.php",
}


def normalize_href_for_page(href, base_host="punjabi-kavita.com"):
    if href.startswith("http://") or href.startswith("https://"):
        parsed = urlparse(href)
        host = parsed.netloc.lower().replace("www.", "")
        if host != base_host:
            return None
        href = parsed.path
    return href.lstrip("/")


def count_content_links(html_path, script):
    with open(html_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    nav = GURMUKHI_NAV_HREFS if script == "gurmukhi" else SHAHMUKHI_NAV_HREFS
    seen = set()
    for a in soup.select("a[href$='.php']"):
        href = a.get("href")
        norm = normalize_href_for_page(href)
        if norm is None:
            continue
        if norm in nav:
            continue
        if script == "gurmukhi" and norm.endswith("Shahmukhi.php"):
            continue
        seen.add(norm)
    return len(seen)


def classify_page(script, href):
    html_path = DATA_RAW / script / href
    if not html_path.exists():
        return "missing", None
    n = count_content_links(html_path, script)
    if n > 0:
        return "hub", n
    return "inline", None


def load_rows(csv_name):
    with open(DATA_PROCESSED / csv_name, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def normalize_stem(stem):
    return stem.lower().replace("-", "")


def stem_of(href):
    assert href.endswith(".php")
    return href[: -len(".php")]


def main():
    g_rows = load_rows("poets_gurmukhi.csv")
    s_rows = load_rows("poets_shahmukhi.csv")

    classification = {}
    for script, rows in [("gurmukhi", g_rows), ("shahmukhi", s_rows)]:
        for r in rows:
            classification[(script, r["href"])] = classify_page(script, r["href"])

    s_href_set = {r["href"] for r in s_rows}
    s_by_href = {r["href"]: r for r in s_rows}

    s_norm_map = {}
    for r in s_rows:
        norm = normalize_stem(stem_of(r["href"]))
        s_norm_map.setdefault(norm, []).append(r["href"])
    collisions = {k: v for k, v in s_norm_map.items() if len(v) > 1}
    if collisions:
        log_line(MATCH_LOG, "NORMALIZED_COLLISIONS", collisions)
        print(f"WARNING: {len(collisions)} normalized-stem collisions on the Shahmukhi "
              f"side -- logged and left unmatched rather than guessed at: {collisions}")

    matched_shahmukhi_hrefs = set()
    matched_gurmukhi_hrefs = set()
    pairs = []
    unmatched_gurmukhi = []
    method_counts = {"exact_nohyphen": 0, "exact_hyphen": 0, "normalized": 0, "unmatched": 0}
    multi_matched_shahmukhi = {}
    normalized_audit_rows = []

    for g in g_rows:
        g_href = g["href"]
        g_stem = stem_of(g_href)
        candidate1 = g_stem + "Shahmukhi.php"
        candidate2 = g_stem + "-Shahmukhi.php"
        norm_g = normalize_stem(g_stem)
        candidate3_key = norm_g + "shahmukhi"

        match_href = None
        method = "unmatched"
        if candidate1 in s_href_set:
            match_href = candidate1
            method = "exact_nohyphen"
        elif candidate2 in s_href_set:
            match_href = candidate2
            method = "exact_hyphen"
        elif candidate3_key in s_norm_map and len(s_norm_map[candidate3_key]) == 1:
            match_href = s_norm_map[candidate3_key][0]
            method = "normalized"

        method_counts[method] += 1

        if match_href is None:
            unmatched_gurmukhi.append(g)
            continue

        if method == "normalized":
            s_stem = stem_of(match_href)
            norm_s = normalize_stem(s_stem)
            suspicious = not (norm_s.endswith("shahmukhi") and norm_s[: -len("shahmukhi")] == norm_g)
            normalized_audit_rows.append({
                "gurmukhi_stem": g_stem,
                "shahmukhi_stem": s_stem,
                "gurmukhi_normalized": norm_g,
                "shahmukhi_normalized": norm_s,
                "suspicious": suspicious,
            })

        if match_href in matched_shahmukhi_hrefs:
            multi_matched_shahmukhi.setdefault(match_href, []).append(g_href)
        matched_shahmukhi_hrefs.add(match_href)
        matched_gurmukhi_hrefs.add(g_href)

        s = s_by_href[match_href]
        g_layout, g_poems = classification[("gurmukhi", g_href)]
        s_layout, s_poems = classification[("shahmukhi", s["href"])]
        pairs.append({
            "gurmukhi_name_raw": g["name_raw"],
            "gurmukhi_href": g_href,
            "gurmukhi_url": g["url"],
            "shahmukhi_name_raw": s["name_raw"],
            "shahmukhi_href": s["href"],
            "shahmukhi_url": s["url"],
            "match_method": method,
            "page_layout_gurmukhi": g_layout,
            "poem_count_gurmukhi": g_poems if g_poems is not None else "",
            "page_layout_shahmukhi": s_layout,
            "poem_count_shahmukhi": s_poems if s_poems is not None else "",
        })

    if multi_matched_shahmukhi:
        log_line(MATCH_LOG, "MULTI_MATCHED_SHAHMUKHI_HREFS", multi_matched_shahmukhi)
        print(f"WARNING: {len(multi_matched_shahmukhi)} Shahmukhi hrefs were matched by "
              f"more than one Gurmukhi entry -- logged, all such pairs still written: "
              f"{multi_matched_shahmukhi}")

    unmatched_shahmukhi = [s for s in s_rows if s["href"] not in matched_shahmukhi_hrefs]

    pairs_path = OUTPUT / "poet_pairs.csv"
    with open(pairs_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "gurmukhi_name_raw", "gurmukhi_href", "gurmukhi_url",
            "shahmukhi_name_raw", "shahmukhi_href", "shahmukhi_url",
            "match_method", "page_layout_gurmukhi", "poem_count_gurmukhi",
            "page_layout_shahmukhi", "poem_count_shahmukhi",
        ])
        writer.writeheader()
        writer.writerows(pairs)

    def write_unmatched(path, rows, script):
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "name_raw", "href", "url", "script", "ambiguous", "page_layout", "poem_count",
            ])
            writer.writeheader()
            for r in rows:
                layout, poems = classification[(script, r["href"])]
                writer.writerow({
                    "name_raw": r["name_raw"],
                    "href": r["href"],
                    "url": r["url"],
                    "script": r["script"],
                    "ambiguous": r["ambiguous"],
                    "page_layout": layout,
                    "poem_count": poems if poems is not None else "",
                })

    unmatched_g_path = OUTPUT / "unmatched_gurmukhi.csv"
    unmatched_s_path = OUTPUT / "unmatched_shahmukhi.csv"
    write_unmatched(unmatched_g_path, unmatched_gurmukhi, "gurmukhi")
    write_unmatched(unmatched_s_path, unmatched_shahmukhi, "shahmukhi")

    audit_path = OUTPUT / "match_audit.csv"
    with open(audit_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "gurmukhi_stem", "shahmukhi_stem", "gurmukhi_normalized",
            "shahmukhi_normalized", "suspicious",
        ])
        writer.writeheader()
        writer.writerows(normalized_audit_rows)
    suspicious_rows = [r for r in normalized_audit_rows if r["suspicious"]]

    def breakdown(script, rows):
        counts = {"hub": 0, "inline": 0, "missing": 0}
        for r in rows:
            layout, _ = classification[(script, r["href"])]
            counts[layout] += 1
        return counts

    g_breakdown = breakdown("gurmukhi", g_rows)
    s_breakdown = breakdown("shahmukhi", s_rows)

    def pct(n, total):
        return 100 * n / total if total else 0

    g_total = len(g_rows)
    s_total = len(s_rows)
    g_hub_pct = pct(g_breakdown["hub"], g_total)
    s_hub_pct = pct(s_breakdown["hub"], s_total)

    def cross_tab(script, rows, matched_hrefs):
        table = {"hub": {True: 0, False: 0}, "inline": {True: 0, False: 0}, "missing": {True: 0, False: 0}}
        for r in rows:
            layout, _ = classification[(script, r["href"])]
            both = r["href"] in matched_hrefs
            table[layout][both] += 1
        return table

    g_cross = cross_tab("gurmukhi", g_rows, matched_gurmukhi_hrefs)
    s_cross = cross_tab("shahmukhi", s_rows, matched_shahmukhi_hrefs)

    print(f"Matching complete. method_counts={method_counts}")
    print(f"Pairs matched: {len(pairs)}")
    print(f"Unmatched Gurmukhi: {len(unmatched_gurmukhi)}, Unmatched Shahmukhi: {len(unmatched_shahmukhi)}")
    print(f"Wrote {pairs_path}, {unmatched_g_path}, {unmatched_s_path}, {audit_path}")

    print(f"\n=== NORMALIZED-MATCH AUDIT ({len(normalized_audit_rows)} rows) ===")
    print(f"Suspicious (differ by more than hyphenation alone): {len(suspicious_rows)}")
    if len(suspicious_rows) > 10:
        print(f"*** {len(suspicious_rows)} SUSPICIOUS NORMALIZED MATCHES -- above the 10-row "
              f"threshold, review output/match_audit.csv before trusting the normalized-match "
              f"portion of the dataset. ***")
    elif suspicious_rows:
        print(f"{len(suspicious_rows)} suspicious row(s) found -- see output/match_audit.csv:")
        for r in suspicious_rows:
            print(f"   {r}")
    else:
        print("None found -- every normalized match differs from its pair by hyphenation only.")

    print(f"\n=== PAGE LAYOUT BREAKDOWN ===")
    print(f"Gurmukhi ({g_total} total): hub={g_breakdown['hub']} ({g_hub_pct:.1f}%), "
          f"inline={g_breakdown['inline']} ({pct(g_breakdown['inline'], g_total):.1f}%), "
          f"missing={g_breakdown['missing']}")
    print(f"Shahmukhi ({s_total} total): hub={s_breakdown['hub']} ({s_hub_pct:.1f}%), "
          f"inline={s_breakdown['inline']} ({pct(s_breakdown['inline'], s_total):.1f}%), "
          f"missing={s_breakdown['missing']}")
    if abs(g_hub_pct - s_hub_pct) > 15:
        print(f"*** NOTABLE DIFFERENCE: hub-layout share differs by "
              f"{abs(g_hub_pct - s_hub_pct):.1f} percentage points between Gurmukhi and "
              f"Shahmukhi -- may indicate the two sides were built at different times or by "
              f"different methods. ***")

    print(f"\n=== CROSS-TAB: page_layout x both_scripts ===")
    print("Gurmukhi:")
    for layout in ["hub", "inline", "missing"]:
        print(f"   {layout}: both_scripts=True: {g_cross[layout][True]}, both_scripts=False: {g_cross[layout][False]}")
    print("Shahmukhi:")
    for layout in ["hub", "inline", "missing"]:
        print(f"   {layout}: both_scripts=True: {s_cross[layout][True]}, both_scripts=False: {s_cross[layout][False]}")

    log_line(MATCH_LOG, "METHOD_COUNTS", method_counts)
    log_line(MATCH_LOG, "PAGE_LAYOUT_BREAKDOWN", "gurmukhi", g_breakdown, "shahmukhi", s_breakdown)
    log_line(MATCH_LOG, "PAGE_LAYOUT_X_BOTH_SCRIPTS_CROSS_TAB", "gurmukhi", g_cross, "shahmukhi", s_cross)
    log_line(MATCH_LOG, "SUSPICIOUS_NORMALIZED_MATCHES", len(suspicious_rows))


if __name__ == "__main__":
    main()
