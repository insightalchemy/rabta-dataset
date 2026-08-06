import time
from datetime import datetime, timezone
from pathlib import Path

import requests

CONTACT_EMAIL = "ishan.nagpal10@gmail.com"
USER_AGENT = f"Rabta Research Project (contact: {CONTACT_EMAIL})"
MIN_DELAY_SECONDS = 3.0
BASE_URL = "https://www.punjabi-kavita.com/"
REQUEST_TIMEOUT = 20

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
