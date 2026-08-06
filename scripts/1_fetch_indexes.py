import csv
import sys
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from common import (
    BASE_URL,
    DATA_PROCESSED,
    DATA_RAW,
    LOGS,
    RateLimiter,
    fetch_cached,
    log_line,
    now_iso,
)

INDEX_LOG = LOGS / "index_fetch.log"
EXCLUDED_LOG = LOGS / "excluded_links.txt"

GURMUKHI_URL = urljoin(BASE_URL, "PunjabiPoetry.php")
GURMUKHI_CACHE = DATA_RAW / "gurmukhi" / "PunjabiPoetry.php.html"
SHAHMUKHI_URL = urljoin(BASE_URL, "PunjabiPoetryShahmukhi.php")
SHAHMUKHI_CACHE = DATA_RAW / "shahmukhi" / "PunjabiPoetryShahmukhi.php.html"

MIN_POETS = 200
MAX_POETS = 1000

GURMUKHI_EXCLUSIONS = {}
for href in [
    "punjabikavitainnews.php", "Punjabi-Poetry.php", "Poems-On-Farmers-Workers.php",
    "Kirti-Kisan-Morcha.php", "Poems-On-Festivals-Seasons.php", "Poems-On-Mother.php",
    "Poems-On-Baisakhi.php", "Ghadar-Lehar-Di-Kavita.php", "PoemsForChildren.php",
    "Punjabi-Barah-Maha.php", "Patriotic-Poetry-Punjabi.php", "Punjabi-Ghazlan.php",
    "Punjabi-Humorous-Poems.php", "Punjabi-Vaaran.php", "Punjabi-Lok-Kaav.php",
    "Selected-Kafian.php", "Punjabi-Kissa-Sahit.php", "Audio-Punjabi-Poetry.php",
    "Stories-In-Poetry.php", "Poems-On-Daughters.php", "Punjabi-Dohre.php",
    "Punjabi-Geet.php", "Poems-On-Punjab-Punjabi.php", "TeeanTeejDeean.php",
    "Punjabi-Akhaan.php",
]:
    GURMUKHI_EXCLUSIONS[href] = "themed_anthology_or_genre_page"

GURMUKHI_EXCLUSIONS["Punjabi-Alochana.php"] = "literary_criticism_page"

GURMUKHI_EXCLUSIONS["Urdu-Poetry.php"] = "urdu_poetry_section_header"
for href in [
    "Ahmed-Faraz.php", "Akbar-Allahabadi.php", "Allah-Yar-Khan-Jogi.php",
    "Bahadur-Shah-Zafar.php", "Dr-Muhammad-Iqbal.php", "Faiz-Ahmed-Faiz.php",
    "Firaq-Gorakhpuri.php", "Habib-Jalib-Urdu.php", "Ibn-e-Insha.php",
    "Janak-Raj-Kanwal.php", "UrduPoetryFarid.php", "Krishan-Betab.php",
    "Majaz-Lakhnavi.php", "Majrooh-Sultanpuri.php", "Mir-Taqi-Mir.php",
    "Mirza-Ghalib.php", "Nazeer-Akbarabadi.php", "Qateel-Shifai.php",
    "Sahir-Ludhianvi.php", "Sarvarinder-Goyal.php", "Seemab-Akbarabadi.php",
]:
    GURMUKHI_EXCLUSIONS[href] = "urdu_poetry_section_poet"

GURMUKHI_EXCLUSIONS["Hindi-Poetry.php"] = "hindi_poetry_section_header"
for href in [
    "Amir-Khusro.php", "Amrit-Rai.php", "Bhagat-Dhanna-Ji.php", "Bhagat-Kabir.php",
    "Bhagat-Namdev.php", "BhagatRamanandJi.php", "Bhagat-Ravidas.php", "Surdas.php",
    "Bhagat-Trilochan-Ji.php", "Sant-Meera-Bai.php", "Giridhar-Kavirai.php",
    "Gopal-Das-Neeraj.php", "Guru-Teg-Bahadur-Ji.php", "Hansram-Bajpeyi.php",
    "Dushyant-Kumar.php", "Harivansh-Rai-Bachchan.php", "Mahadevi-Verma.php",
    "Rahim.php", "Ram-Prasad-Bismil.php", "Raskhan.php",
]:
    GURMUKHI_EXCLUSIONS[href] = "hindi_poetry_section_poet"

GURMUKHI_EXCLUSIONS["Translations.php"] = "translations_page"

SHAHMUKHI_EXCLUSIONS = {}
for href in [
    "PunjabiLokKaavShahmukhi.php", "PunjabiGhazlanShahmukhi.php",
    "PunjabiBarahMahaShahmukhi.php", "PunjabiVaaranShahmukhi.php",
    "PunjabiKafianShahmukhi.php", "PunjabiDohreShahmukhi.php",
]:
    SHAHMUKHI_EXCLUSIONS[href] = "genre_category_page"

SHAHMUKHI_EXCLUSIONS["HindiPoetryShahmukhi.php"] = "hindi_poetry_section_header"
for href in [
    "AmirKhusroShahmukhi.php", "AmritRaiShahmukhi.php", "BhagatKabirShahmukhi.php",
    "BhagatNamdevShahmukhi.php", "BhagatRavidasShahmukhi.php", "BhagatSurdasShahmukhi.php",
    "DushyantKumarShahmukhi.php", "GiridharKaviraiShahmukhi.php",
    "GopalDasNeerajShahmukhi.php", "GuruTegBahadurJiShahmukhi.php",
    "HansramBajpeyiShahmukhi.php", "HarivanshRaiBachchanShahmukhi.php",
    "MahadeviVermaShahmukhi.php", "RahimShahmukhi.php", "RamPrasadBismilShahmukhi.php",
    "RaskhanShahmukhi.php", "SantMeeraBaiShahmukhi.php",
]:
    SHAHMUKHI_EXCLUSIONS[href] = "hindi_poetry_section_poet"

SHAHMUKHI_EXCLUSIONS["TranslationsShahmukhi.php"] = "translations_page"


def is_external(href):
    return href.startswith("http://") or href.startswith("https://")


def external_reason(href):
    if "punjabikahani" in href:
        return "external_subdomain_short_stories"
    if "hindi-kavita.com" in href:
        return "external_subdomain_hindi_kavita_site"
    return "external_domain_unspecified"


def extract_gurmukhi(soup):
    anchors = soup.select("div.section > div.right li a[href$='.php']")
    main_entries = []
    seen = set()
    for a in anchors:
        href = a.get("href")
        if href in seen:
            continue
        seen.add(href)
        main_entries.append((a.get_text(strip=True), href))

    other_anchors = soup.select("div.section > div.full li a[href$='.php']")
    ambiguous_entries = []
    excluded = []
    other_seen = set()
    for a in other_anchors:
        href = a.get("href")
        if href in seen or href in other_seen:
            continue
        other_seen.add(href)
        if is_external(href):
            excluded.append((href, external_reason(href), a.get_text(strip=True)))
        elif href in GURMUKHI_EXCLUSIONS:
            excluded.append((href, GURMUKHI_EXCLUSIONS[href], a.get_text(strip=True)))
        else:
            ambiguous_entries.append((a.get_text(strip=True), href))

    return main_entries, ambiguous_entries, excluded


def extract_shahmukhi(soup):
    blocks = soup.select("div.section > div.full")
    sizes = [len(b.select("li a[href$='.php']")) for b in blocks]
    main_idx = sizes.index(max(sizes))
    print(
        f"[shahmukhi] selected div.full block {main_idx} of {len(blocks)} as the "
        f"main poet list (most li>a links: {sizes[main_idx]}; other block sizes: "
        f"{[s for i, s in enumerate(sizes) if i != main_idx]})"
    )
    log_line(
        INDEX_LOG,
        "SHAHMUKHI_BLOCK_SELECTION",
        f"chosen_block={main_idx}/{len(blocks)}",
        f"link_count={sizes[main_idx]}",
        f"all_sizes={sizes}",
    )

    main_entries = []
    seen = set()
    for a in blocks[main_idx].select("li a[href$='.php']"):
        href = a.get("href")
        if href in seen:
            continue
        seen.add(href)
        main_entries.append((a.get_text(strip=True), href))

    ambiguous_entries = []
    excluded = []
    other_seen = set()
    for i, block in enumerate(blocks):
        if i == main_idx:
            continue
        for a in block.select("li a[href$='.php']"):
            href = a.get("href")
            if href in seen or href in other_seen:
                continue
            other_seen.add(href)
            if is_external(href):
                excluded.append((href, external_reason(href), a.get_text(strip=True)))
            elif href in SHAHMUKHI_EXCLUSIONS:
                excluded.append((href, SHAHMUKHI_EXCLUSIONS[href], a.get_text(strip=True)))
            else:
                ambiguous_entries.append((a.get_text(strip=True), href))

    return main_entries, ambiguous_entries, excluded


def write_csv(path, rows, script_name):
    scraped_at = now_iso()
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["name_raw", "href", "url", "script", "ambiguous", "scraped_at"])
        for name_raw, href, ambiguous in rows:
            url = urljoin(BASE_URL, href)
            writer.writerow([name_raw, href, url, script_name, ambiguous, scraped_at])


def validate_count(script_name, count):
    if count < MIN_POETS or count > MAX_POETS:
        print(
            f"VALIDATION FAILED: {script_name} yielded {count} poet links "
            f"(expected {MIN_POETS}-{MAX_POETS}). Stopping -- see logs/index_fetch.log."
        )
        log_line(INDEX_LOG, "VALIDATION_FAILED", script_name, count)
        sys.exit(1)
    print(f"[{script_name}] validation OK: {count} poet links (within {MIN_POETS}-{MAX_POETS})")


def main():
    rate_limiter = RateLimiter()

    g_html, g_status = fetch_cached(GURMUKHI_URL, GURMUKHI_CACHE, INDEX_LOG, rate_limiter)
    s_html, s_status = fetch_cached(SHAHMUKHI_URL, SHAHMUKHI_CACHE, INDEX_LOG, rate_limiter)
    if g_html is None or s_html is None:
        print("FATAL: could not obtain one or both index pages. Stopping.")
        sys.exit(1)
    print(f"gurmukhi index: {g_status}, shahmukhi index: {s_status}")

    g_soup = BeautifulSoup(g_html, "html.parser")
    s_soup = BeautifulSoup(s_html, "html.parser")

    g_main, g_ambig, g_excl = extract_gurmukhi(g_soup)
    s_main, s_ambig, s_excl = extract_shahmukhi(s_soup)

    g_rows = [(name, href, False) for name, href in g_main] + [
        (name, href, True) for name, href in g_ambig
    ]
    s_rows = [(name, href, False) for name, href in s_main] + [
        (name, href, True) for name, href in s_ambig
    ]

    print(f"[gurmukhi] main list: {len(g_main)}, ambiguous (included): {len(g_ambig)}, "
          f"excluded: {len(g_excl)}, total retained: {len(g_rows)}")
    print(f"[shahmukhi] main list: {len(s_main)}, ambiguous (included): {len(s_ambig)}, "
          f"excluded: {len(s_excl)}, total retained: {len(s_rows)}")

    validate_count("gurmukhi", len(g_rows))
    validate_count("shahmukhi", len(s_rows))

    write_csv(DATA_PROCESSED / "poets_gurmukhi.csv", g_rows, "gurmukhi")
    write_csv(DATA_PROCESSED / "poets_shahmukhi.csv", s_rows, "shahmukhi")

    with open(EXCLUDED_LOG, "w", encoding="utf-8") as f:
        f.write(f"Excluded-link audit, generated {now_iso()}\n")
        f.write(
            "These links appear inside a div.section container on the index pages "
            "but are NOT part of the Punjabi poet A-Z list -- they belong to a "
            "different section of the homepage (other language, other genre, or an "
            "external subdomain). Excluded by explicit lookup, not pattern-matching.\n\n"
        )
        f.write(f"=== GURMUKHI ({len(g_excl)} excluded) ===\n")
        for href, reason, text in g_excl:
            f.write(f"{href}\t{reason}\t{text}\n")
        f.write(f"\n=== SHAHMUKHI ({len(s_excl)} excluded) ===\n")
        for href, reason, text in s_excl:
            f.write(f"{href}\t{reason}\t{text}\n")
        if g_ambig or s_ambig:
            f.write("\n=== AMBIGUOUS (included in CSVs with ambiguous=True) ===\n")
            for name, href in g_ambig:
                f.write(f"gurmukhi\t{href}\t{name}\n")
            for name, href in s_ambig:
                f.write(f"shahmukhi\t{href}\t{name}\n")

    print(f"Wrote {EXCLUDED_LOG}")

    for path in [DATA_PROCESSED / "poets_gurmukhi.csv", DATA_PROCESSED / "poets_shahmukhi.csv"]:
        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        non_ascii_rows = [r for r in rows if any(ord(c) > 127 for c in r["name_raw"])]
        print(f"{path.name}: {len(rows)} rows written. Sample row: {rows[0]}")
        if non_ascii_rows:
            print(f"  non-ASCII name_raw found ({len(non_ascii_rows)} rows), e.g.: {non_ascii_rows[0]}")
        else:
            print("  all name_raw values are ASCII (index-level names are romanized "
                  "transliterations on this site -- see METHODOLOGY.md limitations).")


if __name__ == "__main__":
    main()
