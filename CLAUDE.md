# Rabta — Punjabi Cross-Script Dataset

## Project context
Research project on the Gurmukhi–Shahmukhi divide in Punjabi literature.
Building a public dataset of which poets appear in which script on
punjabi-kavita.com. Output may be published and cited in academic work.

## Critical constraints
- Neither author reads Gurmukhi or Shahmukhi. Flag anything requiring
  script literacy instead of resolving it yourself.
- NEVER populate a data field from model knowledge. Every non-scraped
  value needs a source_url from an actual lookup. No source = empty cell.
- Never guess at poet biography (religion, nationality, dates, era).
- Mark all uncertain values explicitly rather than smoothing them over.

## Scraping rules
- Check robots.txt before any request. If disallowed, stop and tell me.
- Minimum 3 second delay between requests. Never parallelize requests.
- User-agent must identify the project and include a contact email.
- Cache every response to data/raw/. Never re-fetch a cached page.
- The site owner has been contacted about this research. Be a good citizen.

## Technical
- Python 3, requests + BeautifulSoup. Standard library where possible.
- All file I/O in UTF-8. Gurmukhi and Perso-Arabic text must round-trip
  intact. Verify encoding after every write.
- Scripts must be resumable — assume interruption at any point.
- Log every request and every skipped/failed page to logs/.
