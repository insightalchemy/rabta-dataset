import sys
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from common import BASE_URL, DATA_RAW, LOGS, RateLimiter, extract_content_links, fetch_cached, log_line

SUBPAGE_LOG = LOGS / "subpage_fetch.log"
SUBPAGE_DIR = DATA_RAW / "subpages"


def sublinks_of(script, hub_href):
    hub_path = DATA_RAW / script / hub_href
    with open(hub_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    return sorted(extract_content_links(soup, script, hub_href))


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
