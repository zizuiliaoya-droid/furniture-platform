---
name: furniture-system
description: Use this skill whenever a user wants to connect QwenPaw to the furniture management platform, check available platform capabilities, diagnose authentication/API connectivity, or learn which furniture Skills the current account may use. Trigger especially for 家具平台、系统能力、连接状态、API、权限、登录令牌、可用工具.
metadata:
  requires:
    bins: [python]
    env: [FURNITURE_API_URL, FURNITURE_API_TOKEN]
---

# Furniture System

Use the bundled deterministic client for every platform operation:

```text
python <this-skill>/scripts/furniture_api.py --skill furniture-system capabilities
```

## Rules

1. Run `capabilities` before the first domain operation in a new session.
2. Treat the returned capability list as authoritative for the current account.
3. Never print, repeat, summarize, or write `FURNITURE_API_TOKEN` into files.
4. Never access the platform database or media volume directly.
5. Return the API `request_id` when reporting a failure so an administrator can find its audit record.
6. On 401, report that the configured token is invalid or expired. On 403, report the missing permission; do not attempt to bypass it.

Read [references/api.md](references/api.md) only when exact commands, fields, or response semantics are needed.
