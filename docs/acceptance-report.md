# 交付验收报告

验收日期：2026-08-12（Asia/Shanghai）

## 公网入口

- Web：<https://furniture-zk.zeabur.app/>
- API：<https://furniture-api-zk.zeabur.app/>
- API 健康检查：<https://furniture-api-zk.zeabur.app/api/health/>

## 自动化结果

- Django/DRF：100 项测试通过。
- React：3 项 Vitest 测试通过，TypeScript 与 Vite 生产构建通过。
- QwenPaw API 客户端：5 项测试通过；6 个 Skill 通过结构校验。
- Django migration check：无遗漏迁移。
- npm audit：生产与开发依赖均为 0 个已知漏洞。
- Docker Compose：平台和 QwenPaw 两份配置均通过解析校验。

## 公网结果

- Web 首页：HTTP 200，生产 CSP、frame、referrer、permissions、nosniff 响应头生效。
- API 健康检查：HTTP 200，数据库可用。
- Agent Gateway 未登录访问：HTTP 401。
- Agent Gateway 登录后：返回 9 项能力；产品、文档和案例搜索返回生产数据；请求 ID 与 HTTPS 深链接正常。
- PostgreSQL：公网 TCP 端口转发为 `DISABLED`，仅保留 Zeabur 私网 DNS。
- 浏览器渲染：登录页成功加载，标题和灯具交互入口正常显示。

## QwenPaw 运行说明

Skill、确定性 API 客户端和带认证的 Docker 编排已交付。QwenPaw 首次启动仍需在私有 `.env`/Console 中提供模型供应商密钥和家具平台专用用户 Token；仓库不包含或生成第三方模型密钥。
