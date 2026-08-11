# QwenPaw 家具平台技能包

该目录包含家具平台的 6 个领域 Skill。`furniture-system` 提供共享 API 客户端；其余 Skill 提供触发规则和安全工作流。

## 安装

QwenPaw 官方支持外部 Skill 路径。将仓库中的 `paw/skills` 注册到 `$QWENPAW_WORKING_DIR/config.json`：

```json
{
  "skill_paths": ["/absolute/path/to/furniture-platform/paw/skills"]
}
```

也可以把每个 Skill 目录复制到：

```text
$QWENPAW_WORKING_DIR/workspaces/<agent_id>/skills/
```

在 QwenPaw Console 中为这些 Skill 配置：

- `FURNITURE_API_URL=https://furniture-zk.zeabur.app`
- `FURNITURE_API_TOKEN=<家具平台为该操作员签发的 Token>`
- 可选 `FURNITURE_API_TIMEOUT=30`

启用全部 6 个 Skill 后，先运行 `/furniture-system 查询可用能力`。生产环境不要把 Token 写进 `SKILL.md`、聊天记录或 Git。

## 本地验证

```powershell
python -m pytest paw/tests -q
python paw/skills/furniture-system/scripts/furniture_api.py --help
```

## Docker 启动

复制环境模板并填写专用平台 Token、Console 强密码和至少一个模型供应商密钥：

```powershell
Copy-Item paw/.env.example paw/.env
docker compose --env-file paw/.env -f paw/docker-compose.yml up -d
```

默认只监听 `127.0.0.1:8088`。如果必须通过公网访问 Console，将
`QWENPAW_BIND_ADDRESS` 改为服务器网卡地址，并继续保留登录认证；更推荐放在
HTTPS 反向代理或 VPN 后面。首次启动后访问 `http://127.0.0.1:8088/`，确认模型、
默认 Agent 和 6 个家具 Skill 均已启用。
