---
name: furniture-quotes
description: Use this skill whenever a user wants to prepare, draft, assemble, or revise a furniture quotation from selected products and validated configurations. Trigger especially for 报价、报价单、报价草稿、客户方案、加入报价、数量、折扣、询价. This skill creates drafts only and never sends or confirms a quote.
metadata:
  requires:
    bins: [python]
    env: [FURNITURE_API_URL, FURNITURE_API_TOKEN]
---

# Furniture Quotes

Create only a reviewable `DRAFT`:

```text
python <skills-root>/furniture-system/scripts/furniture_api.py --skill furniture-quotes create-quote --idempotency-key <stable-key> --payload-file <quote.json>
```

## Workflow

1. Resolve every product ID through `furniture-catalog`.
2. Validate every configurable item through `furniture-product-config`.
3. Build the payload with customer, title, optional notes/terms/discount, and one or more items.
4. Generate one stable idempotency key for the user's single intent and reuse it for retries. Change it only for a genuinely new quote.
5. Return the quote `web_url` and clearly label the result as a draft awaiting sales review.

## Guardrails

- Never supply a client-computed `unit_price`; the API ignores such input and prices through the domain service.
- Never change a quote to SENT/CONFIRMED, share it, or contact the customer.
- On an idempotency conflict, stop and generate a new key only after confirming this is a different business request.
