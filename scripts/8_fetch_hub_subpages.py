import sys
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from common import BASE_URL, DATA_RAW, LOGS, RateLimiter, fetch_cached, log_line

SUBPAGE_LOG = LOGS / "subpage_fetch.log"
SUBPAGE_DIR = DATA_RAW / "subpages"

GURMUKHI_NAV_HREFS = {
    "PunjabiPoetry.php", "Punjabi-Sufi-Poetry.php", "Urdu-Poetry.php",
    "Hindi-Poetry.php", "Translations.php", "pkcontactus.php",
}
SHAHMUKHI_NAV_HREFS = {
    "indexShahmukhi.php", "PunjabiPoetryShahmukhi.php", "PunjabiSufiPoetryShahmukhi.php",
    "HindiPoetryShahmukhi.php", "TranslationsShahmukhi.php", "pkcontactus.php",
}


def normalize_href(href, base_host="punjabi-kavita.com"):
    if href.startswith("http://") or href.startswith("https://"):
        parsed = urlparse(href)
        host = parsed.netloc.lower().replace("www.", "")
        if host != base_host:
            return None
        href = parsed.path
    return href.lstrip("/")


def sublinks_of(script, hub_href):
    hub_path = DATA_RAW / script / hub_href
    with open(hub_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    nav = GURMUKHI_NAV_HREFS if script == "gurmukhi" else SHAHMUKHI_NAV_HREFS
    seen = []
    for a in soup.select("a[href$='.php']"):
        href = a.get("href")
        norm = normalize_href(href)
        if norm is None:
            continue
        if norm in nav:
            continue
        if script == "gurmukhi" and norm.endswith("Shahmukhi.php"):
            continue
        if norm not in seen:
            seen.append(norm)
    return seen


def fetch_hub_subpages(script, hub_href):
    sublinks = sublinks_of(script, hub_href)
    rate_limiter = RateLimiter()
    results = []
    for i, href in enumerate(sublinks, start=1):
        url = urljoin(BASE_URL, href)
        cache_path = SUBPAGE_DIR / script / href
        html, status = fetch_cached(url, cache_path, SUBPAGE_LOG, rate_limiter)
        results.append((href, status))
        print(f"[{script}/{hub_href}] {i}/{len(sublinks)}: {href} -- {status}")
    return results


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: python3 8_fetch_hub_subpages.py <script> <hub_href>")
        sys.exit(1)
    fetch_hub_subpages(sys.argv[1], sys.argv[2])
