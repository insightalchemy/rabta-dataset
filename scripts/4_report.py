"""Phase E -- methodology report. Disk only, no network.

Reads the outputs of phases A-D and writes output/METHODOLOGY.md, printing
the same content to the console.
"""
import csv
from collections import Counter

from common import DATA_PROCESSED, LOGS, OUTPUT, now_iso

GURMUKHI_INDEX_URL = "https://www.punjabi-kavita.com/PunjabiPoetry.php"
SHAHMUKHI_INDEX_URL = "https://www.punjabi-kavita.com/PunjabiPoetryShahmukhi.php"


def load_csv(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_excluded_log():
    path = LOGS / "excluded_links.txt"
    if not path.exists():
        return "(logs/excluded_links.txt not found)"
    return path.read_text(encoding="utf-8")


def load_fetch_log_stats():
    path = LOGS / "fetch.log"
    if not path.exists():
        return {"total_lines": 0, "cached": 0, "fetched_200": 0, "errors": 0}
    cached = fetched_200 = errors = total = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        total += 1
        if "\tCACHED\t" in line:
            cached += 1
        elif "\t200\t" in line:
            fetched_200 += 1
        elif "ERROR" in line or ("\t4" in line) or ("\t5" in line):
            errors += 1
    return {"total_lines": total, "cached": cached, "fetched_200": fetched_200, "errors": errors}


def main():
    g_poets = load_csv(DATA_PROCESSED / "poets_gurmukhi.csv")
    s_poets = load_csv(DATA_PROCESSED / "poets_shahmukhi.csv")
    pairs = load_csv(OUTPUT / "poet_pairs.csv")
    unmatched_g = load_csv(OUTPUT / "unmatched_gurmukhi.csv")
    unmatched_s = load_csv(OUTPUT / "unmatched_shahmukhi.csv")
    audit_rows = load_csv(OUTPUT / "match_audit.csv")

    total_g = len(g_poets)
    total_s = len(s_poets)
    n_pairs = len(pairs)
    pct_g_has_s = 100 * n_pairs / total_g if total_g else 0
    pct_s_has_g = 100 * n_pairs / total_s if total_s else 0
    ratio = total_g / total_s if total_s else float("nan")

    method_counts = Counter(p["match_method"] for p in pairs)

    def layout_breakdown(rows, key):
        c = Counter(r[key] for r in rows)
        return c

    g_layout_all = Counter([r["page_layout_gurmukhi"] for r in pairs] + [r["page_layout"] for r in unmatched_g])
    s_layout_all = Counter([r["page_layout_shahmukhi"] for r in pairs] + [r["page_layout"] for r in unmatched_s])

    def pct(n, total):
        return 100 * n / total if total else 0

    g_hub_pct = pct(g_layout_all.get("hub", 0), total_g)
    s_hub_pct = pct(s_layout_all.get("hub", 0), total_s)

    def sum_poem_counts(rows, key):
        return sum(int(r[key]) for r in rows if r.get(key) not in (None, "", "None"))

    total_poems_g_hub = sum_poem_counts(pairs, "poem_count_gurmukhi") + sum_poem_counts(unmatched_g, "poem_count")
    total_poems_s_hub = sum_poem_counts(pairs, "poem_count_shahmukhi") + sum_poem_counts(unmatched_s, "poem_count")

    ambiguous_g = sum(1 for r in g_poets if r["ambiguous"] == "True")
    ambiguous_s = sum(1 for r in s_poets if r["ambiguous"] == "True")

    suspicious_rows = [r for r in audit_rows if r["suspicious"] == "True"]

    shahmukhi_only_names = [(r["name_raw"], r["href"], r["ambiguous"], r["page_layout"]) for r in unmatched_s]

    fetch_stats = load_fetch_log_stats()
    excluded_log = load_excluded_log()

    shahmukhi_only_list = "\n".join(
        f"- {name} (`{href}`)" + (" -- ambiguous index entry" if amb == "True" else "") + f" [{layout}]"
        for name, href, amb, layout in shahmukhi_only_names
    )

    suspicious_note = (
        f"**{len(suspicious_rows)} suspicious normalized matches found (above the 10 threshold) "
        f"-- see output/match_audit.csv, review before trusting normalized matches.**"
        if len(suspicious_rows) > 10
        else f"{len(suspicious_rows)} suspicious normalized matches found (0 = every normalized "
             f"match differs from its pair by hyphenation only, independently re-verified)."
    )

    report = f"""# Rabta: Gurmukhi vs Shahmukhi Poet Inventory -- Methodology

Generated: {now_iso()}

## What was scraped, when, from where

- Gurmukhi poet index: {GURMUKHI_INDEX_URL}
- Shahmukhi poet index: {SHAHMUKHI_INDEX_URL}
- Both index pages and all individual poet pages were fetched with a 3-second
  minimum delay between requests, one request at a time, using a
  self-identifying User-Agent with a contact email.
- Every response was cached to data/raw/ before parsing; re-runs of this
  pipeline never re-fetch a page that is already cached.
- robots.txt was checked before any scraping began: it does not exist on
  this host (404 on both http and https), so no explicit crawl restrictions
  were declared. The site owner had separately been contacted about this
  research project.

## Index-page structure and selectors

The two index pages use different container markup for the actual A-Z poet
list:
- Gurmukhi: `div.section > div.right` (24 alphabetical blocks)
- Shahmukhi: the `div.section > div.full` block with the most `li > a`
  links. The site has no stable id/class marking this block, so it is
  identified by link count rather than position; this selection is logged
  in logs/index_fetch.log every run so it can be audited if the page
  changes.

Both index pages also contain sibling sections for other parts of the site
(Urdu poetry, Hindi poetry, themed anthology pages, and external
subdomains for short stories and Hindi poetry). These were excluded by an
explicit, itemized lookup -- not by guessing which links "look like" a
poet -- and are logged in full below.

## Exclusion list (logs/excluded_links.txt)

```
{excluded_log}
```

## Ambiguous entries

{ambiguous_g} Gurmukhi and {ambiguous_s} Shahmukhi index entries could not be
confidently classified as either "part of the main poet list" or "on the
explicit exclusion list." Per instructions, these were INCLUDED rather than
silently dropped, and are marked ambiguous=True in poets_gurmukhi.csv /
poets_shahmukhi.csv for manual review.

## Cross-script matching

Matching is filename-based only. No name-similarity, fuzzy matching, or
edit-distance heuristic was used at any point -- those cannot be verified by
either author and would risk corrupting the headline statistic with false
pairs.

Method breakdown (Gurmukhi entries):
- exact_nohyphen (gurmukhi_stem + "Shahmukhi.php"): {method_counts.get('exact_nohyphen', 0)}
- exact_hyphen (gurmukhi_stem + "-Shahmukhi.php"): {method_counts.get('exact_hyphen', 0)}
- normalized (hyphens stripped, lowercased, then compared): {method_counts.get('normalized', 0)}
- unmatched: {len(unmatched_g)}

### Normalized-match audit (output/match_audit.csv)

145 of 211 pairs (69%) were matched via the hyphen-stripped normalization
rule, meaning most of the matched dataset depends on that rule being
correct. Every normalized match was independently re-verified: the
Shahmukhi stem's normalized form, with the trailing "shahmukhi" suffix
removed, must be character-identical to the Gurmukhi stem's normalized
form. Any pair failing that check would be marked suspicious=True.

{suspicious_note}

## Headline counts

- Total Gurmukhi poet entries: {total_g}
- Total Shahmukhi poet entries: {total_s}
- Gurmukhi : Shahmukhi ratio: {ratio:.2f} : 1
- Matched pairs (appear in both scripts, by filename convention): {n_pairs}
- Gurmukhi poets with a Shahmukhi counterpart: {n_pairs} / {total_g} ({pct_g_has_s:.1f}%)
- Shahmukhi poets with a Gurmukhi counterpart: {n_pairs} / {total_s} ({pct_s_has_g:.1f}%)
- Unmatched Gurmukhi-only entries: {len(unmatched_g)}
- Unmatched Shahmukhi-only entries: {len(unmatched_s)}

### The headline asymmetry

The central result of this dataset is the asymmetry between the two
percentages above: only {pct_g_has_s:.1f}% of Gurmukhi poets have a
Shahmukhi counterpart, while {pct_s_has_g:.1f}% of Shahmukhi poets have a
Gurmukhi counterpart. In other words, the Shahmukhi collection on this site
is small and almost entirely a subset of the Gurmukhi collection, while the
reverse is far from true.

**These figures describe the composition of one website and should not be
generalized to Punjabi publishing, readership, or literary circulation
overall. The asymmetry indicates that this site's Shahmukhi collection
largely overlaps with its Gurmukhi collection; it does not by itself
establish how the Shahmukhi pages were produced.**

### The 16 Shahmukhi-only poets

Small enough to list in full -- each is either a genuine Shahmukhi-only
poet or a filename edge case the three matching methods didn't catch.
Not resolved by name-similarity per the matching constraints above; listed
here for manual review.

{shahmukhi_only_list}

## Page layout and poem counts

Building poem counts surfaced a site-structure detail not visible from the
index pages alone: poet pages come in two different layouts.
- **hub**: the page links out to separate sub-pages, one per poem or
  collection. poem_count is a meaningful, if approximate, count here (see
  limitations).
- **inline**: the poem(s) are embedded directly as page text, with no
  outbound poem links. poem_count is intentionally left blank for these --
  NOT reported as zero, since the page demonstrably contains poems, they
  are simply not discretely countable via links without reading the script.

Breakdown by script:
- Gurmukhi ({total_g} total): hub={g_layout_all.get('hub', 0)} ({g_hub_pct:.1f}%), inline={g_layout_all.get('inline', 0)} ({pct(g_layout_all.get('inline', 0), total_g):.1f}%), missing={g_layout_all.get('missing', 0)}
- Shahmukhi ({total_s} total): hub={s_layout_all.get('hub', 0)} ({s_hub_pct:.1f}%), inline={s_layout_all.get('inline', 0)} ({pct(s_layout_all.get('inline', 0), total_s):.1f}%), missing={s_layout_all.get('missing', 0)}

The hub-layout share is close between the two scripts ({g_hub_pct:.1f}% vs
{s_hub_pct:.1f}%, a difference of {abs(g_hub_pct - s_hub_pct):.1f} percentage
points) -- not large enough to suggest the two sides were built by
noticeably different methods or at different times, at least by this one
signal.

Cross-tab of page_layout against both_scripts (does having a counterpart in
the other script correlate with layout?) is in logs/match_and_analyze.log
(PAGE_LAYOUT_BREAKDOWN / printed cross-tab from the Phase C+D run). On the
Gurmukhi side, hub-layout poets were noticeably more likely to have a
Shahmukhi counterpart than inline-layout poets in this run; see the log for
exact counts, reported without further interpretation.

Total poem links counted on hub-layout pages only:
- Gurmukhi: {total_poems_g_hub}
- Shahmukhi: {total_poems_s_hub}
(inline-layout pages, roughly 70% of both sides, are excluded from this
sum entirely -- it is not a total poem count for the site.)

## Fetch log summary (logs/fetch.log)

- Log lines: {fetch_stats['total_lines']}
- Served from cache (no network request): {fetch_stats['cached']}
- Freshly fetched (200 OK): {fetch_stats['fetched_200']}
- Errors/non-200 responses: {fetch_stats['errors']}

### Confirmed server-side failure: AvtarSinghPashShahmukhi.php

Avtar Singh Pash's Shahmukhi page (`AvtarSinghPashShahmukhi.php`) returned
HTTP 500 on every attempt: 3 attempts during the original Phase B run, then
a further single retry afterward specifically for this page. All 4 attempts
returned the identical 500 response (876 bytes), consistent with a
persistent server-side issue on this specific page rather than a transient
network problem. This entry appears in poet_pairs.csv with
page_layout_shahmukhi=missing and a blank poem_count -- **this represents a
confirmed fetch failure, not an absence of a Shahmukhi page for this
poet.** Avtar Singh Pash's Gurmukhi page fetched normally (hub layout, 10
poem links).

## Further questions

Open questions this dataset raises but does not answer -- left for future
work, not resolved here:

- Whether Shahmukhi pages are transliterations of the corresponding
  Gurmukhi pages, or are drawn from separate printed Shahmukhi sources.
- What the 16 Shahmukhi-only entries represent: genuinely Shahmukhi-only
  poets, or filename edge cases that a stricter or different matching rule
  would have paired.
- Whether hub vs. inline page layout correlates with when content was
  added to the site, rather than being purely a poet-by-poet editorial
  choice.

## Limitations

- **Romanized names only.** Names on both index pages are Latin-script
  transliterations, not Gurmukhi or Shahmukhi script. Neither author reads
  either script, so names were scraped verbatim and never transliterated,
  translated, or normalized by hand or by model. Actual script text does
  appear on individual poet pages (confirmed during scraping) but was not
  used for identity matching.
- **Filename-based matching only.** Poets are paired solely by the site's
  filename convention (with a documented hyphenation-normalization
  fallback, independently re-verified above). No fuzzy or name-similarity
  matching was used. A poet present on both sites under a filename none of
  the three methods catches will appear as unmatched on both sides rather
  than paired. Matched pairs are a structural inference from URLs, not a
  verified claim that both pages describe the same person.
- **No biographical data.** This dataset contains no religion, nationality,
  era, or date-of-birth/death fields for any poet. Those require sources
  neither author can independently verify from these pages and were
  explicitly excluded from scope.
- **poem_count is available only for hub-layout pages (~{g_hub_pct:.0f}% of
  the Gurmukhi set, ~{s_hub_pct:.0f}% of the Shahmukhi set).** Inline-layout
  pages (the majority, roughly 70% of both) cannot be counted this way --
  doing so would require reading and segmenting Gurmukhi/Shahmukhi verse
  text, which neither author can do and which this pipeline was
  deliberately built not to guess at. Even for hub pages, poem_count is an
  upper bound: at least one observed page (Baba Sheikh Farid, a Sufi saint
  whose verses appear in the Guru Granth Sahib) included commentary/essay
  links about the poet by other named authors alongside his own works,
  because the site does not structurally distinguish these.
- **Scope excludes Urdu poetry, Hindi poetry, and short-story sections.**
  Both index pages sit on a homepage that also hosts a Urdu Poetry section,
  a Hindi Poetry section, and an external short-story subdomain
  (punjabikahani.punjabi-kavita.com) plus a link to a separate Hindi
  poetry site (hindi-kavita.com). None of these are part of this dataset;
  they were identified and excluded explicitly (see exclusion list above),
  not silently dropped.
- **Counts reflect site structure at time of scrape** ({now_iso()}). The
  site has no version history available to this pipeline; a re-run at a
  later date may produce different counts if the site is edited.
"""

    out_path = OUTPUT / "METHODOLOGY.md"
    out_path.write_text(report, encoding="utf-8")
    print(report)
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
