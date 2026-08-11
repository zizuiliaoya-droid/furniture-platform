---
name: furniture-product-config
description: Use this skill whenever a user asks for a furniture product's details, selectable configuration dimensions, valid options, default preset, exact configured price, or whether a requested combination can be quoted. Trigger especially for 产品详情、配置、颜色、尺寸、材质、选项、组合、算价、多少钱、默认款.
metadata:
  requires:
    bins: [python]
    env: [FURNITURE_API_URL, FURNITURE_API_TOKEN]
---

# Furniture Product Configuration

## Detail

```text
python <skills-root>/furniture-system/scripts/furniture_api.py --skill furniture-product-config product-detail <product_id>
```

## Exact price

```text
python <skills-root>/furniture-system/scripts/furniture_api.py --skill furniture-product-config calculate-price <product_id> --selections '{"color":"red","size":"L"}'
```

## Rules

1. Use only `dimension_key` and option `key` values returned by product detail.
2. Respect parent/child dimension conditions and required dimensions.
3. Never calculate, estimate, interpolate, or add prices in the prompt. Only report a price when the API returns `valid: true` and `source: PriceCalculationService`.
4. When invalid, show `missing_dimensions`, `invalid_selections`, and the API reason; ask the user to choose valid options.
5. Carry the exact validated `selections` object into a quote draft.
