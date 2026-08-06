# Rabta — Punjabi Cross-Script Dataset

Research project on the Gurmukhi–Shahmukhi divide in Punjabi literature.
Inventories which poets appear in which script on punjabi-kavita.com.

## Pipeline

Scripts run in order, each reading only the outputs of the previous stage.
Phases A and B are the only ones that touch the network.

| Script | Phase | Reads | Writes |
|---|---|---|---|
| `scripts/1_fetch_indexes.py` | A — index scrape + poet-link filtering | network (cached) | `data/processed/poets_gurmukhi.csv`, `poets_shahmukhi.csv`, `logs/excluded_links.txt` |
| `scripts/2_fetch_poet_pages.py` | B — fetch every poet page | network (cached) | `data/raw/{gurmukhi,shahmukhi}/*.html` |
| `scripts/3_match_and_analyze.py` | C+D — cross-script matching, page-layout/poem analysis | disk only | `output/poet_pairs.csv`, `unmatched_gurmukhi.csv`, `unmatched_shahmukhi.csv`, `match_audit.csv` |
| `scripts/4_report.py` | E — methodology report | disk only | `output/METHODOLOGY.md` |
| `scripts/5_shahmukhi_only.py` | follow-up — Shahmukhi-only subset | disk only | `output/shahmukhi_only.csv` |

Run from inside `scripts/` (they import `common.py` by relative path):

```
cd scripts
python3 1_fetch_indexes.py
python3 2_fetch_poet_pages.py
python3 3_match_and_analyze.py
python3 4_report.py
python3 5_shahmukhi_only.py
```

Every script is resumable: cached pages in `data/raw/` are never re-fetched,
so re-running a script after an interruption picks up where it left off.

## Scraping conventions

- 3-second minimum delay between requests, no parallel requests.
- User-Agent identifies the project and a contact email (see `common.py`).
- robots.txt was checked before scraping began; see `output/METHODOLOGY.md`.
- All fetches are logged to `logs/index_fetch.log` / `logs/fetch.log`.

## Output

- `data/processed/` — raw per-script poet indexes (name, href, url, ambiguous flag).
- `output/poet_pairs.csv` — poets matched across both scripts, with match method and page layout/poem count.
- `output/unmatched_gurmukhi.csv`, `output/unmatched_shahmukhi.csv` — poets found in only one script.
- `output/shahmukhi_only.csv` — the Shahmukhi-only subset, for manual research.
- `output/match_audit.csv` — independent re-verification of every normalized-rule match.
- `output/METHODOLOGY.md` — full methodology, headline statistics, exclusions, limitations, and open questions.

`data/raw/` and `logs/` are gitignored (see `.gitignore`) since they're
large, regeneratable caches rather than source artifacts.

## Known limitations

See the "Limitations" and "Further questions" sections of
`output/METHODOLOGY.md` — in short: index-level poet names are romanized
transliterations only, matching is filename-based (never by name
similarity), poem counts only exist for "hub"-layout pages (~30% of the
dataset), and no biographical data is included anywhere.
