import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests

CONTACT_EMAIL = "ishan.nagpal10@gmail.com"
USER_AGENT = f"Rabta Research Project (contact: {CONTACT_EMAIL})"
MIN_DELAY_SECONDS = 3.0
BASE_URL = "https://www.punjabi-kavita.com/"
REQUEST_TIMEOUT = 20

GURMUKHI_NAV_HREFS = {
    "PunjabiPoetry.php", "Punjabi-Sufi-Poetry.php", "Urdu-Poetry.php",
    "Hindi-Poetry.php", "Translations.php", "pkcontactus.php",
}
SHAHMUKHI_NAV_HREFS = {
    "indexShahmukhi.php", "PunjabiPoetryShahmukhi.php", "PunjabiSufiPoetryShahmukhi.php",
    "HindiPoetryShahmukhi.php", "TranslationsShahmukhi.php", "pkcontactus.php",
}


def normalize_href(href, base_host="punjabi-kavita.com"):
    href = href.split("#", 1)[0]
    if href.startswith("http://") or href.startswith("https://"):
        parsed = urlparse(href)
        host = parsed.netloc.lower().replace("www.", "")
        if host != base_host:
            return None
        href = parsed.path
    href = href.lstrip("/")
    if not href.endswith(".php"):
        return None
    return href


def extract_content_links(soup, script, current_href):
    """Every <a href> pointing to another .php page, stripped of any #fragment,
    excluding site nav, self-page anchors, and (for gurmukhi pages) the
    cross-script link. Matches hrefs like 'Foo.php#Bar', not just 'Foo.php'."""
    nav = GURMUKHI_NAV_HREFS if script == "gurmukhi" else SHAHMUKHI_NAV_HREFS
    seen = set()
    for a in soup.find_all("a", href=True):
        norm = normalize_href(a["href"])
        if norm is None:
            continue
        if norm in nav:
            continue
        if norm == current_href:
            continue
        if script == "gurmukhi" and norm.endswith("Shahmukhi.php"):
            continue
        seen.add(norm)
    return seen

ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
OUTPUT = ROOT / "output"
LOGS = ROOT / "logs"

for _d in (DATA_RAW, DATA_PROCESSED, OUTPUT, LOGS):
    _d.mkdir(parents=True, exist_ok=True)


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def log_line(log_path, *fields):
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write("\t".join([now_iso(), *[str(x) for x in fields]]) + "\n")


class RateLimiter:
    def __init__(self, min_delay=MIN_DELAY_SECONDS):
        self.min_delay = min_delay
        self._last = None

    def wait(self):
        if self._last is not None:
            elapsed = time.monotonic() - self._last
            remaining = self.min_delay - elapsed
            if remaining > 0:
                time.sleep(remaining)
        self._last = time.monotonic()


def fetch_cached(url, cache_path, log_path, rate_limiter, max_retries=2):
    cache_path = Path(cache_path)
    if cache_path.exists():
        log_line(log_path, url, "CACHED", cache_path.stat().st_size)
        return cache_path.read_text(encoding="utf-8"), "cached"

    attempt = 0
    while attempt <= max_retries:
        attempt += 1
        rate_limiter.wait()
        try:
            resp = requests.get(
                url,
                headers={"User-Agent": USER_AGENT},
                timeout=REQUEST_TIMEOUT,
            )
            resp.encoding = resp.encoding or "utf-8"
            if resp.status_code == 200:
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                cache_path.write_text(resp.text, encoding="utf-8")
                log_line(log_path, url, resp.status_code, len(resp.content))
                return resp.text, "fetched"
            else:
                log_line(log_path, url, resp.status_code, len(resp.content), f"attempt={attempt}")
                if attempt > max_retries:
                    return None, "failed"
        except requests.RequestException as exc:
            log_line(log_path, url, "ERROR", str(exc), f"attempt={attempt}")
            if attempt > max_retries:
                return None, "failed"
    return None, "failed"
