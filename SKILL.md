---
name: au-grocery-price-compare
description: Compare current Coles, Woolworths and ALDI (Australia) grocery prices for a shopping list or product, find the cheapest store, unit prices and specials, and optionally report only price changes since last run. Uses the public Apify Actor luke-main/au-supermarket-prices with the user's own Apify API token.
license: MIT
metadata:
  author: Luke Main
  built_by: AI agents, reviewed and owned by Luke Main
  version: 1.0.0
---

# Australian grocery price comparison (Coles vs Woolworths vs ALDI)

Use this skill when the user wants to know where groceries are cheapest in Australia, compare a basket across Coles, Woolworths and ALDI, check unit prices or specials, or watch prices for changes.

## What it needs
- An Apify API token belonging to the user, in the environment variable `APIFY_TOKEN` (free Apify accounts include monthly credit). If it is missing, ask the user to create one at https://console.apify.com/settings/integrations. Never print the token.
- Network access to `https://api.apify.com` only. This skill makes no other network calls.

## Cost to the user
The Actor is pay-per-result on Apify: about US$0.001 per product returned (US$1 per 1,000), billed to the user's own Apify account. A 10-item basket with 5 results per item per store costs roughly US$0.15. Keep `maxItemsPerQuery` small to keep costs low and tell the user the expected cost before large runs.

## Steps
1. Turn the user's request into short search terms, one per product (e.g. "full cream milk 2l", "vegemite 380g", "weet-bix"). Pick stores (default all three: `coles`, `woolworths`, `aldi`).
2. Run the Actor synchronously and get results in one call:

```bash
python3 scripts/compare.py "full cream milk 2l" "vegemite" "weet-bix" --per-query 5
```

   Or call the API directly:

```bash
curl -s -X POST "https://api.apify.com/v2/acts/luke-main~au-supermarket-prices/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" -H "Content-Type: application/json" \
  -d '{"stores":["coles","woolworths","aldi"],"searchTerms":["full cream milk 2l"],"maxItemsPerQuery":5,"maxItems":200}'
```

3. Each returned row has: `store`, `name`, `brand`, `size`, `price` (AUD incl. GST), `unitPrice`, `unitPriceText`, `wasPrice`, `isOnSpecial`, `specialText`, `inStock`, `url`, `source` (the search term).
4. For each search term, pick the most relevant match per store (prefer the same size; compare `unitPrice` when sizes differ). Present a compact table: item | Coles | Woolworths | ALDI | cheapest. Add a basket total per store when every store has a match, and flag specials (`wasPrice`).
5. Price watching: add `"changesOnly": true, "stateStoreName": "<watchlist-name>"` to the input. The first run records prices; later runs return only rows with `changeType` (`price_up`, `price_down`, `new`), `oldPrice` and `pctChange`.

## Caveats to tell the user
- Prices are each chain's default online/catalogue price; individual stores and postcodes can differ.
- ALDI Australia has no online shop, so ALDI shows catalogue prices and no stock level.
- Independent tool, not affiliated with Coles, Woolworths or ALDI.
