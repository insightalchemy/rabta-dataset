from common import OUTPUT, now_iso

MARKER = "## Presence vs. coverage depth"

SECTION = f"""{MARKER}

**This section was corrected on {now_iso()} -- see output/CORRECTION.md for
the full account. The version of this section published previously
understated Sharaf's Shahmukhi content by roughly 26x due to a link-
detection bug that also affected the "under 500 words" figures below; see
the correction notice before relying on any number in this section.**

The matched-pair figures in this dataset record whether a poet has a page
in each script. They do not measure how much of that poet's work appears
on each side, and "appears in both scripts" should be read as nominal
presence, not equivalent coverage -- that qualification still holds. What
changed is the evidence for it.

Corrected case study: Babu Firoz Din Sharaf has 104,577 words across ten
Gurmukhi sub-pages against 6,739 words across a Shahmukhi landing page
plus one sub-page (ratio 0.0644). The previously published figures --
"approximately 350 works... against a single Shahmukhi page of 233 words"
-- were incomplete: a Gurmukhi sub-page and the entire Shahmukhi sub-page
had not been fetched due to a link-detection bug (fragment-suffixed hrefs
like `Foo.php#Bar` were not matched). Sharaf's Shahmukhi page does contain
substantial content (24 full poems, not a title-only stub); the divergence
from the Gurmukhi side is still large, just roughly 26x smaller than
previously stated.

The 59.7% under 500 words / 84.1% under 1000 words figures for the full
227-page Shahmukhi corpus are numerically unchanged on re-verification
(the underlying text extraction was not the bug), but their
interpretation was wrong: of the 135 pages under 500 words, 105 (78%) are
now known to be pages misclassified as short-and-complete when they are
actually hub pages linking to unfetched sub-pages. Only 30 pages (22% of
the under-500 group) are confirmed genuinely short. 1,926 sub-pages
(1,622 Gurmukhi-side, 304 Shahmukhi-side) remain unfetched; word counts
and layout for the 428 poet pages they belong to should be treated as
undetermined, not short, until that fetch happens.
"""


def main():
    path = OUTPUT / "METHODOLOGY.md"
    existing = path.read_text(encoding="utf-8")
    if MARKER in existing:
        existing = existing[: existing.index(MARKER)]
    content = existing.rstrip("\n") + "\n\n" + SECTION
    path.write_text(content, encoding="utf-8")
    print(f"Updated {path}")


if __name__ == "__main__":
    main()
