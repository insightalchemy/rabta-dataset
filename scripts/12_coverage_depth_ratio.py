import csv

from bs4 import BeautifulSoup

from common import DATA_RAW, OUTPUT


def paragraph_count(html_path):
    with open(html_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    return len(soup.find_all("p"))


def depth_proxy(script, href, layout, sublinks):
    if layout == "hub":
        return int(sublinks), "sublinks"
    if layout == "inline":
        html_path = DATA_RAW / script / href
        if not html_path.exists():
            return None, "missing"
        return paragraph_count(html_path), "paragraphs"
    return None, "missing"


def main():
    with open(OUTPUT / "poet_pairs.csv", encoding="utf-8") as f:
        pairs = list(csv.DictReader(f))

    rows = []
    for p in pairs:
        g_depth, g_proxy = depth_proxy(
            "gurmukhi", p["gurmukhi_href"], p["page_layout_gurmukhi"], p["poem_count_gurmukhi"]
        )
        s_depth, s_proxy = depth_proxy(
            "shahmukhi", p["shahmukhi_href"], p["page_layout_shahmukhi"], p["poem_count_shahmukhi"]
        )

        same_proxy = g_proxy == s_proxy and g_proxy != "missing"
        ratio = ""
        magnitude_flag = ""
        if same_proxy and g_depth and g_depth > 0 and s_depth is not None:
            ratio = s_depth / g_depth if g_depth else ""
            if ratio != "" and ratio > 0:
                if ratio >= 10 or ratio <= 0.1:
                    magnitude_flag = "order_of_magnitude"

        rows.append({
            "gurmukhi_name_raw": p["gurmukhi_name_raw"],
            "gurmukhi_href": p["gurmukhi_href"],
            "shahmukhi_href": p["shahmukhi_href"],
            "gurmukhi_depth_proxy_type": g_proxy,
            "gurmukhi_depth_value": g_depth if g_depth is not None else "",
            "shahmukhi_depth_proxy_type": s_proxy,
            "shahmukhi_depth_value": s_depth if s_depth is not None else "",
            "proxies_comparable": same_proxy,
            "depth_ratio_shahmukhi_over_gurmukhi": round(ratio, 4) if isinstance(ratio, float) else "",
            "order_of_magnitude_difference": magnitude_flag == "order_of_magnitude",
        })

    out_path = OUTPUT / "coverage_depth_ratio.csv"
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    comparable = [r for r in rows if r["proxies_comparable"]]
    not_comparable = [r for r in rows if not r["proxies_comparable"]]
    sublink_proxy = [r for r in comparable if r["gurmukhi_depth_proxy_type"] == "sublinks"]
    paragraph_proxy = [r for r in comparable if r["gurmukhi_depth_proxy_type"] == "paragraphs"]

    order_mag = [r for r in comparable if r["order_of_magnitude_difference"]]
    g_bigger = [r for r in order_mag if r["depth_ratio_shahmukhi_over_gurmukhi"] not in ("", 0) and r["depth_ratio_shahmukhi_over_gurmukhi"] < 1]
    s_bigger = [r for r in order_mag if r["depth_ratio_shahmukhi_over_gurmukhi"] not in ("", 0) and isinstance(r["depth_ratio_shahmukhi_over_gurmukhi"], float) and r["depth_ratio_shahmukhi_over_gurmukhi"] > 1]

    print(f"Wrote {out_path} ({len(rows)} rows)")
    print(f"\nCOMPARABLE proxies (same type both sides): {len(comparable)} / {len(rows)}")
    print(f"  of which same-type sublinks (hub/hub): {len(sublink_proxy)}")
    print(f"  of which same-type paragraphs (inline/inline): {len(paragraph_proxy)}")
    print(f"NOT COMPARABLE (different proxy types, e.g. hub vs inline, or missing page): {len(not_comparable)} / {len(rows)}")
    print("  These are NOT presented as a single ranked list with the comparable pairs.")

    print(f"\nOrder-of-magnitude differences (ratio >=10x or <=0.1x) among comparable pairs: "
          f"{len(order_mag)} / {len(comparable)}")
    print(f"  Gurmukhi side apparently deeper (ratio <= 0.1): {len(g_bigger)}")
    print(f"  Shahmukhi side apparently deeper (ratio >= 10): {len(s_bigger)}")

    print("\nOrder-of-magnitude pairs:")
    for r in order_mag:
        print(f"  {r['gurmukhi_name_raw']}: {r['gurmukhi_depth_proxy_type']}="
              f"{r['gurmukhi_depth_value']} vs {r['shahmukhi_depth_value']}, "
              f"ratio={r['depth_ratio_shahmukhi_over_gurmukhi']}")


if __name__ == "__main__":
    main()
