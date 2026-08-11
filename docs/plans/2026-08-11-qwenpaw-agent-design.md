# QwenPaw 家具平台 Agent 设计

## 背景与目标

现有家具平台已经具备 Django/DRF、React、PostgreSQL、Docker Compose，以及产品、定价、报价、文档、案例、分享和权限模块。目标不是重写这些模块，而是在不削弱确定性、安全性和现有图形界面的前提下，增加一个可通过 QwenPaw、控制台和后续企业消息渠道使用的自然语言入口。

成功标准：普通查询可以直接完成；写操作生成可审计结果；价格、权限、导入事务和分享限制永远由后端执行；复杂编辑继续跳转现有 Web 页面；平台和 Agent 均有可重复部署配置；公网 Web 链路经过 HTTPS 验收。

## 方案选择

选择“Web 平台 + Agent Gateway + Paw Skills”混合方案。

1. Paw-only：开发快，但聊天界面不适合图片排序、价格矩阵、Excel 错误预览和复杂报价编辑；同时模型不能作为财务和权限规则的执行者，因此拒绝。
2. 大模型直接嵌入每个 Django 模块：耦合高、供应商切换困难，且会让业务请求依赖模型可用性，因此拒绝。
3. 混合方案：Django 暴露范围明确的 Agent API，Skills 只负责把 Paw 的结构化意图转成 API 调用；现有前端继续承担复杂交互。该方案改动小、可审计、可独立降级，因此采用。

## 组件与数据流

```text
用户 ── Web/消息渠道 ── QwenPaw
                         │
                    领域 Skills
                         │ HTTPS + Token
                  Django Agent Gateway
                    │       │       │
                 权限    业务服务   审计日志
                    └──── PostgreSQL
```

Agent Gateway 提供能力发现、产品搜索/详情、价格验证、报价草稿、文档/案例检索和导入预览等窄接口。只读接口可以直接执行；创建报价草稿等可逆写入要求幂等键；导入确认、发布分享等敏感操作要求后端签发的短期一次性确认票据。Gateway 不保存自然语言推理链，只记录用户、Skill、动作、输入摘要、结果状态、关联对象、请求 ID 和耗时。

Paw Skills 按领域拆分，而不是按页面拆分：目录、产品配置、报价、资料、案例、导入和系统能力。每个 Skill 复用同一个无第三方依赖的 Python API 客户端，并从 `FURNITURE_API_URL`、`FURNITURE_API_TOKEN`、`FURNITURE_WEB_URL` 读取配置。密钥不写入 Skill 或 Git。

## 错误处理与安全

后端是唯一可信边界。所有 Agent 请求继续执行 DRF TokenAuthentication、模块权限和对象归属校验；Serializer 校验模型生成的参数。网络重试只用于 GET 和带幂等键的请求；客户端对 401/403、409、422、429 和 5xx 返回可操作的中文错误，不自动绕过权限或确认。

价格必须由 `PriceCalculationService` 计算。报价项目保存快照。Excel 必须先预览，存在错误或未完成映射时不得确认。确认票据绑定用户、动作和输入摘要并在短期内过期，使用后写入审计表防止重放。日志不记录密码、Token、完整文件或客户敏感内容。

QwenPaw 公网部署必须开启 Console 登录认证、Tool Guard 和 Skill Scanner；控制台与平台使用不同凭据。平台后端和数据库不直接暴露给 Paw 所在网络之外，Skills 只访问 HTTPS API。

## 测试与部署

测试分四层：Django 服务/接口测试验证权限、定价、幂等和确认；Paw 客户端契约测试验证请求结构和错误转换；前端构建与关键组件测试验证现有界面；部署后冒烟测试验证首页、登录、能力发现和未授权拒绝。生产部署执行 Django `check --deploy`，生成强密钥，配置持久化媒体与数据库卷，并确保 `/api`、`/media` 和 SPA 路由由 nginx 正确代理。

Web 平台继续部署到现有 Zeabur 公网域名。QwenPaw 可以在独立 GPU 主机、云主机或 Docker 中运行；其模型故障不会影响家具平台的确定性功能。若没有模型凭据，Skills 和 Gateway 仍可独立完成自动测试，Paw 对话层在提供凭据后启用。
