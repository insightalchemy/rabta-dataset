import csv
import sys
import time
from urllib.parse import urljoin

from common import BASE_URL, DATA_PROCESSED, DATA_RAW, LOGS, RateLimiter, fetch_cached, log_line

SUBPAGE_LOG = LOGS / "subpage_fetch.log"
STATUS_LOG = LOGS / "subpage_fetch_status.log"
SUBPAGE_DIR = DATA_RAW / "subpages"

CONSECUTIVE_FAILURE_LIMIT = 5
SLOW_RESPONSE_SECONDS = 12.0
CONSECUTIVE_SLOW_LIMIT = 3


def main():
    with open(DATA_PROCESSED / "subpages_to_fetch.csv", encoding="utf-8") as f:
        targets = list(csv.DictReader(f))

    rate_limiter = RateLimiter()
    attempted = 0
    cached_count = 0
    fetched_count = 0
    failed = []
    consecutive_failures = 0
    consecutive_slow = 0

    print(f"{len(targets)} sub-pages to fetch")
    log_line(STATUS_LOG, "START", f"targets={len(targets)}")

    for i, row in enumerate(targets, start=1):
        script, href = row["script"], row["href"]
        url = urljoin(BASE_URL, href)
        cache_path = SUBPAGE_DIR / script / href

        start = time.monotonic()
        html, status = fetch_cached(url, cache_path, SUBPAGE_LOG, rate_limiter)
        elapsed = time.monotonic() - start

        attempted += 1
        if status == "cached":
            cached_count += 1
            consecutive_failures = 0
            consecutive_slow = 0
        elif status == "fetched":
            fetched_count += 1
            consecutive_failures = 0
            if elapsed > SLOW_RESPONSE_SECONDS:
                consecutive_slow += 1
            else:
                consecutive_slow = 0
        else:
            failed.append((script, href, url))
            consecutive_failures += 1
            log_line(STATUS_LOG, "FAILED", script, href, url)

        if consecutive_failures >= CONSECUTIVE_FAILURE_LIMIT:
            msg = (f"STOPPING: {consecutive_failures} consecutive failures at "
                   f"{i}/{len(targets)} ({script}/{href}). Site may be struggling.")
            print(msg)
            log_line(STATUS_LOG, "ABORT_CONSECUTIVE_FAILURES", consecutive_failures, script, href)
            return

        if consecutive_slow >= CONSECUTIVE_SLOW_LIMIT:
            msg = (f"STOPPING: {consecutive_slow} consecutive responses over "
                   f"{SLOW_RESPONSE_SECONDS}s at {i}/{len(targets)} ({script}/{href}). "
                   f"Site may be under strain.")
            print(msg)
            log_line(STATUS_LOG, "ABORT_SLOW_RESPONSES", consecutive_slow, script, href)
            return

        if i % 50 == 0 or i == len(targets):
            msg = (f"progress: {i}/{len(targets)} (cached={cached_count}, "
                   f"fetched={fetched_count}, failed={len(failed)})")
            print(msg)
            log_line(STATUS_LOG, "PROGRESS", i, len(targets), cached_count, fetched_count, len(failed))

    failure_rate = len(failed) / attempted if attempted else 0
    print(f"\nDONE: attempted={attempted}, cached={cached_count}, fetched={fetched_count}, "
          f"failed={len(failed)} ({failure_rate:.1%})")
    log_line(STATUS_LOG, "DONE", attempted, cached_count, fetched_count, len(failed))
    if failed:
        print("Failed pages:")
        for script, href, url in failed:
            print(f"  {script}/{href} -- {url}")
        log_line(STATUS_LOG, "FAILED_LIST", failed)


if __name__ == "__main__":
    main()
