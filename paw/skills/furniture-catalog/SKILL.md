---
name: furniture-catalog
description: Use this skill whenever a user wants to find, browse, filter, compare, or recommend furniture products from the company catalog. Trigger especially for 搜产品、找家具、产品推荐、品牌、品类、产地、货期、价格范围、椅子、桌子、柜子、配件、学校家具.
metadata:
  requires:
    bins: [python]
    env: [FURNITURE_API_URL, FURNITURE_API_TOKEN]
---

# Furniture Catalog

Convert the user's request into explicit filters, then call the shared client:

```text
python <skills-root>/furniture-system/scripts/furniture_api.py --skill furniture-catalog search-products --query "人体工学椅" --category-l1 SEATING --origin IMPORT --max-price 5000
```

## Workflow

1. Search with the narrowest known filters; omit unknown filters instead of guessing codes.
2. Present product name, code, brand, minimum price, lead time, and `web_url`.
3. If several products match, compare no more than five and state which user constraint each one satisfies.
4. Use `furniture-product-config` before quoting a configurable product. `min_price` is not a guaranteed configured price.
5. Do not recommend inactive or unreturned products and do not invent inventory data.

For exact filter names, read `<skills-root>/furniture-system/references/api.md`.
