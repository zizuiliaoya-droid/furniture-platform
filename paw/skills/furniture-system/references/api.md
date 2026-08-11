# Furniture Agent API Reference

All commands use:

```text
python <skills-root>/furniture-system/scripts/furniture_api.py --skill <skill-name> <command>
```

Required environment variables:

- `FURNITURE_API_URL`: HTTPS origin serving `/api`; localhost HTTP is allowed for development.
- `FURNITURE_API_TOKEN`: DRF Token for the effective platform user.
- `FURNITURE_API_TIMEOUT`: optional seconds, default `30`.

## Commands

### `capabilities`

Lists tools visible under the current role permission matrix.

### `search-products`

Options: `--query`, `--category-l1`, `--category-l2`, `--brand`, `--origin`, `--lead-time`, `--min-price`, `--max-price`, `--page`, `--page-size`.

### `product-detail PRODUCT_ID`

Returns images, dimensions, option keys, parent constraints, presets and product links.

### `calculate-price PRODUCT_ID --selections JSON`

The JSON object maps `dimension_key` to option `key`. Only a response with `valid: true` is quotable.

### `search-documents`

Options: `--query`, `--doc-type DESIGN|TRAINING|CERTIFICATE`, `--limit`.

### `search-cases`

Options: `--query`, `--industry`, `--limit`.

### `create-quote`

Requires `--idempotency-key` and exactly one of `--payload JSON` or `--payload-file PATH`.

Payload:

```json
{
  "title": "总部办公家具报价",
  "customer_name": "客户名称",
  "notes": "草稿",
  "terms": "",
  "discount": "0.00",
  "items": [
    {
      "product_id": 1,
      "selections": {"color": "red", "size": "L"},
      "quantity": 2
    }
  ]
}
```

### `preview-import PRODUCT_ID FILE`

Options: `--mapping JSON`, `--replace-dimensions`, `--keep-existing-prices`. Returns a confirmation token only when parsing is safe.

### `confirm-import PRODUCT_ID FILE --confirmation-token TOKEN`

Use the same mapping and replacement flags as preview. Tokens expire and are rejected after one successful use.

## Error semantics

- `400`: malformed or unsafe request; correct input or preview again.
- `401`: missing/expired API token.
- `403`: role permission denied.
- `404`: object unavailable to the effective user.
- `409`: idempotency conflict or confirmation replay; do not blindly retry.
- `5xx`: server failure; report `request_id` and retry only safe/idempotent operations.
