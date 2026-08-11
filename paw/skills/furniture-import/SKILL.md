---
name: furniture-import
description: Use this skill whenever a user wants to inspect, map, preview, or import a furniture configuration/pricing Excel workbook. Trigger especially for Excel、xlsx、批量导入、配置导入、价格矩阵、字段映射、预览、确认导入. Always preview first; confirmation is a separate explicit destructive step.
metadata:
  requires:
    bins: [python]
    env: [FURNITURE_API_URL, FURNITURE_API_TOKEN]
---

# Furniture Configuration Import

## Preview

```text
python <skills-root>/furniture-system/scripts/furniture_api.py --skill furniture-import preview-import <product_id> <file.xlsx> --mapping '{}'
```

Report detected format, dimensions, price rows, warnings, errors, and impact. If `needs_mapping` is true, select a Sheet and columns from `available_sheets`, then preview again.

## Confirm

Run only after the user explicitly approves the displayed preview in the current conversation:

```text
python <skills-root>/furniture-system/scripts/furniture_api.py --skill furniture-import confirm-import <product_id> <same-file.xlsx> --confirmation-token <preview-token> --mapping '{}'
```

## Guardrails

1. Never confirm when `can_confirm` is false or errors are non-empty.
2. Use the exact same file, mapping, and replacement flags as the preview. The server rejects mismatches.
3. Do not expose the confirmation token or store it in notes/memory. It is short-lived and one-time.
4. Default to merging dimensions and replacing prices only when complete price data exists.
5. Explain that `--replace-dimensions` can remove current configuration structure; require explicit approval naming that effect.
6. Never retry a consumed token. Preview again to obtain a new token.
