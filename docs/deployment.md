# 家具平台与 QwenPaw 部署

## 公网拓扑

生产环境将 Web 前端和 Django API 分为两个 Zeabur 服务，PostgreSQL 只在项目私网内可见。浏览器通过前端同源 `/api/` 反向代理访问 API；QwenPaw 使用专用低权限用户的 Token 直连 API。

- Web：`https://furniture-zk.zeabur.app`
- API：`https://furniture-api-zk.zeabur.app`
- 健康检查：`GET /api/health/`

## Zeabur 必需环境变量

后端：

```text
DJANGO_SECRET_KEY=<random-secret>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=furniture-api-zk.zeabur.app,furniture-zk.zeabur.app,127.0.0.1,localhost
CORS_ALLOWED_ORIGINS=https://furniture-zk.zeabur.app
CSRF_TRUSTED_ORIGINS=https://furniture-api-zk.zeabur.app,https://furniture-zk.zeabur.app
PUBLIC_WEB_URL=https://furniture-zk.zeabur.app
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
DJANGO_SECURE_HSTS_SECONDS=31536000
```

数据库优先使用 Zeabur 注入的 `DATABASE_URL`。首次部署可以临时设置 `ADMIN_USERNAME` 和 `ADMIN_PASSWORD`；管理员创建后应删除这两个变量。

前端：

```text
BACKEND_URL=https://furniture-api-zk.zeabur.app
BACKEND_HOST=furniture-api-zk.zeabur.app
```

## 本机或 NAS

```powershell
Copy-Item .env.example .env
docker compose up -d --build
Invoke-RestMethod http://localhost/api/health/
```

数据库和 Django 容器不映射主机端口，只有前端入口对外暴露。生产环境必须修改示例密码，并在可信 HTTPS 入口后运行。

## QwenPaw

QwenPaw 与业务系统解耦部署。具体启动方式见 `paw/README.md`。公网 Console 必须开启登录认证，模型供应商密钥和家具平台 Token 只存放于 QwenPaw secret volume，不写入 Skill 或 Git。

报价 Skill 只能创建草稿；Excel 导入 Skill 必须先预检，再用一次性确认令牌提交。价格、权限、审计和幂等仍由 Django 后端执行。

## 验收

```powershell
./scripts/smoke_public.ps1
```

脚本验证前端、API 健康检查和 Agent Gateway 未登录保护。登录后的领域工作流由后端自动化测试覆盖。
