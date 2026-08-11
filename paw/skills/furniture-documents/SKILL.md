---
name: furniture-documents
description: Use this skill whenever a user wants to search internal furniture documents, design resources, training materials, certificates, or completed project cases. Trigger especially for 资料、文档、培训、证书、设计资源、案例、项目经验、参考项目、行业案例.
metadata:
  requires:
    bins: [python]
    env: [FURNITURE_API_URL, FURNITURE_API_TOKEN]
---

# Furniture Documents and Cases

Search documents:

```text
python <skills-root>/furniture-system/scripts/furniture_api.py --skill furniture-documents search-documents --query "人体工学" --doc-type TRAINING
```

Search cases:

```text
python <skills-root>/furniture-system/scripts/furniture_api.py --skill furniture-documents search-cases --query "总部办公" --industry TECH_OFFICE
```

## Rules

1. Summarize only returned excerpts and metadata; do not claim access to unread file contents.
2. Provide the `web_url` for full review in the authenticated platform.
3. Preserve permission boundaries. A 403 means the account cannot use that content domain.
4. When recommending related products from a case, resolve `related_product_ids` through the catalog before describing current product data.
5. Do not include internal document content in external customer messages unless the user explicitly chooses material approved for sharing.
