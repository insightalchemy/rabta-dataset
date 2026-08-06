import csv

from common import OUTPUT

def main():
    with open(OUTPUT / "unmatched_shahmukhi.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    out_path = OUTPUT / "shahmukhi_only.csv"
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name_raw", "url", "page_layout", "poem_count"])
        writer.writeheader()
        for r in rows:
            writer.writerow({
                "name_raw": r["name_raw"],
                "url": r["url"],
                "page_layout": r["page_layout"],
                "poem_count": r["poem_count"] if r["page_layout"] == "hub" else "",
            })

    print(f"Wrote {out_path} ({len(rows)} rows)\n")
    print(f"The {len(rows)} Shahmukhi-only poets (name and page layout only -- no biographical lookup):")
    for r in rows:
        layout = r["page_layout"]
        extra = f", poem_count={r['poem_count']}" if layout == "hub" else ""
        print(f"  - {r['name_raw']} [{layout}{extra}] -- {r['url']}")


if __name__ == "__main__":
    main()
