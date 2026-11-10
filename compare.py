#!/usr/bin/env python3
"""Compare Coles / Woolworths / ALDI prices via the Apify Actor luke-main/au-supermarket-prices.
Needs APIFY_TOKEN (the user's own token) in the environment. Only calls api.apify.com."""
import argparse, json, os, sys, urllib.request

URL = "https://api.apify.com/v2/acts/luke-main~au-supermarket-prices/run-sync-get-dataset-items"

def main():
    p = argparse.ArgumentParser()
    p.add_argument("terms", nargs="+")
    p.add_argument("--stores", default="coles,woolworths,aldi")
    p.add_argument("--per-query", type=int, default=5)
    a = p.parse_args()
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        sys.exit("Set APIFY_TOKEN to your own Apify API token.")
    body = {"stores": a.stores.split(","), "searchTerms": a.terms,
            "maxItemsPerQuery": a.per_query, "maxItems": a.per_query * len(a.terms) * 3}
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        rows = json.load(r)
    out = {}
    for row in rows:
        term = (row.get("source") or "").split(":", 1)[-1]
        out.setdefault(term, {}).setdefault(row["store"], []).append(
            {k: row.get(k) for k in ("name", "size", "price", "unitPriceText", "wasPrice", "isOnSpecial", "url")})
    print(json.dumps(out, indent=1, ensure_ascii=False))

if __name__ == "__main__":
    main()
