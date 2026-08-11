# 公网发布安全审计

审计范围：Django/DRF API、React 客户端、Nginx、上传与媒体预览、Agent Gateway、QwenPaw 运行配置。

## 已修复

### Critical

- 富文本文档预览原先直接渲染存储的 HTML，存在持久型 XSS。客户端现使用 DOMPurify 清洗，并由自动化测试覆盖脚本和事件属性剔除。

### High

- 上传文件原先只检查体积和扩展名。现在图片校验实际图片内容，文档采用允许列表和关键文件签名检查，HTML/SVG 等主动内容拒绝上传。
- 历史媒体文件直接打开时可能在业务域执行。媒体响应现在附带 `nosniff` 和 sandbox CSP，Nginx 同步设置同源嵌入边界。
- 登录和分享密码验证原先无速率限制。现在分别使用独立匿名限流策略。
- Compose 原先公开 PostgreSQL 和 Django 端口，并提供弱默认管理员密码。现在只暴露前端入口，初始化账户必须显式配置。

### Medium

- 前端补充 CSP、frame、referrer、permissions 和 MIME 嗅探防护头。
- 新建和重置用户密码的最低长度提高到 12，登录字段增加长度上限。
- 媒体存储路径使用已解析根路径校验，阻止目录穿越删除。
- npm 生产及开发依赖审计均为 0 个已知漏洞。

## 运行约束

- DRF Token 属于长期凭据。QwenPaw 必须使用独立低权限账号，并按组织策略定期轮换 Token。
- QwenPaw Console 如果绑定公网地址，必须保持 `QWENPAW_AUTH_ENABLED=true`，并放在 HTTPS 反向代理或 VPN 后。
- Zeabur PostgreSQL 的 TCP 公网端口转发已关闭，服务间连接只使用项目私网。
- 当前前端为了兼容既有登录流程将 Token 存于 `localStorage`。CSP、富文本清洗和主动文件阻断降低了 XSS 风险；后续如接入外部不可信内容，建议迁移为短期 HttpOnly Cookie 会话。
