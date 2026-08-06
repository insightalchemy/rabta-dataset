"""Phase B -- fetch every poet page listed in poets_gurmukhi.csv / poets_shahmukhi.csv.

Reads the index CSVs produced by Phase A (disk only for the list of targets).
Fetches each poet page over the network, one at a time, 3s minimum delay,
caches to data/raw/{script}/{href}.html, and is resumable: anything already
cached is skipped without a network request.
"""
import csv
import sys

from common import DATA_PROCESSED, DATA_RAW, LOGS, RateLimiter, fetch_cached, log_line

FETCH_LOG = LOGS / "fetch.log"
MAX_FAILURE_RATE = 0.05


def load_targets(csv_path, script_name):
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    targets = []
    for r in rows:
        cache_path = DATA_RAW / script_name / r["href"]
        targets.append((r["url"], cache_path))
    return targets


def fetch_all(script_name, targets, rate_limiter):
    attempted = 0
    cached_count = 0
    fetched_count = 0
    failed = []

    for i, (url, cache_path) in enumerate(targets, start=1):
        attempted += 1
        html, status = fetch_cached(url, cache_path, FETCH_LOG, rate_limiter)
        if status == "cached":
            cached_count += 1
        elif status == "fetched":
            fetched_count += 1
        else:
            failed.append(url)

        if i % 25 == 0 or i == len(targets):
            print(
                f"[{script_name}] progress: {i}/{len(targets)} "
                f"(cached={cached_count}, fetched={fetched_count}, failed={len(failed)})"
            )

    return attempted, cached_count, fetched_count, failed


def main():
    rate_limiter = RateLimiter()

    all_results = {}
    for script_name, csv_name in [
        ("gurmukhi", "poets_gurmukhi.csv"),
        ("shahmukhi", "poets_shahmukhi.csv"),
    ]:
        targets = load_targets(DATA_PROCESSED / csv_name, script_name)
        print(f"[{script_name}] {len(targets)} poet pages to process")
        attempted, cached_count, fetched_count, failed = fetch_all(script_name, targets, rate_limiter)
        all_results[script_name] = (attempted, cached_count, fetched_count, failed)

    overall_ok = True
    for script_name, (attempted, cached_count, fetched_count, failed) in all_results.items():
        success = attempted - len(failed)
        failure_rate = len(failed) / attempted if attempted else 0
        print(
            f"\n[{script_name}] SUMMARY: attempted={attempted}, cached={cached_count}, "
            f"newly_fetched={fetched_count}, succeeded={success}, failed={len(failed)} "
            f"({failure_rate:.1%})"
        )
        if failed:
            print(f"  failed URLs: {failed}")
            log_line(FETCH_LOG, script_name, "FAILED_URLS", ";".join(failed))
        if failure_rate > MAX_FAILURE_RATE:
            print(
                f"VALIDATION FAILED: {script_name} failure rate {failure_rate:.1%} "
                f"exceeds {MAX_FAILURE_RATE:.0%} threshold."
            )
            overall_ok = False

    if not overall_ok:
        sys.exit(1)
    print("\nPhase B validation OK: failure rate within threshold for both scripts.")


if __name__ == "__main__":
    main()
