# NFR 需求 — Unit 1 后端

## 1. 性能需求

### NFR-PERF-01: API 响应时间
| 操作类型 | 目标 | 说明 |
|----------|------|------|
| 简单查询（列表、详情） | < 200ms | 产品列表、案例详情等 |
| 复杂查询（搜索、统计） | < 500ms | 全局搜索、仪表盘统计 |
| 写操作（创建、更新） | < 300ms | 产品创建、报价更新等 |
| 文件上传（不含传输） | < 2s | 图片上传+缩略图生成 |
| PDF 生成 | < 5s | WeasyPrint 报价单导出 |

### NFR-PERF-02: 并发处理
- 预期并发用户：20-50 人
- Gunicorn workers：4-8（根据 NAS CPU 核心数调整，建议 2×CPU+1）
- 数据库连接池：最大 20 连接
- Railway 测试环境：2 workers（受限于免费/低价套餐资源）

### NFR-PERF-03: 数据库优化
- 为高频查询字段建立索引：Product.name, Product.code, Product.is_active, Quote.status, ShareLink.token
- 分类树查询使用 select_related/prefetch_related 减少 N+1 查询
- 列表接口统一分页（默认 20 条/页）
- 仪表盘统计考虑缓存（简单场景可不缓存，数据量小时直接查询）

### NFR-PERF-04: 文件处理
- 缩略图生成异步化（可选，初期同步生成，后续可引入 Celery）
- 图片上传限制 10MB，文档限制 50MB
- 使用 Pillow 的 thumbnail 方法高效生成缩略图

---

## 2. 安全需求

### NFR-SEC-01: 认证安全
- Token 认证（DRF TokenAuthentication）
- 密码使用 Django 默认 PBKDF2 哈希（iterations ≥ 600000）
- 分享链接密码使用 make_password/check_password
- 登录失败不区分"用户名不存在"和"密码错误"（统一提示）

### NFR-SEC-02: API 安全
- CORS 白名单配置（仅允许前端域名）
- CSRF 对 API 禁用（Token 认证不需要）
- 所有写操作需要认证
- 管理员操作通过 IsAdminRole 权限类控制
- 文件上传验证 Content-Type 和文件大小

### NFR-SEC-03: 数据保护
- DEBUG=False 在生产环境
- SECRET_KEY 通过环境变量注入
- 数据库密码通过环境变量注入
- 敏感信息不记录到日志
- 媒体文件通过 Nginx 代理访问（生产环境），不直接暴露文件系统路径

### NFR-SEC-04: 分享链接安全
- UUID4 token 不可预测
- 密码哈希存储
- 过期时间和访问次数限制
- 可随时禁用链接

---

## 3. 可靠性与运维需求

### NFR-REL-01: 日志策略
- Django 日志级别：生产 WARNING，测试 INFO
- 请求日志：记录 API 请求路径、方法、状态码、耗时
- 错误日志：记录完整异常堆栈
- 日志输出到 stdout（Docker 容器标准做法）
- 生产环境通过 Docker logs 查看

### NFR-REL-02: 备份策略
- **定时 pg_dump**：每日凌晨通过 cron 或 Docker 定时任务执行 pg_dump，保留最近 7 天
- **NAS Hyper Backup**：整体备份 Docker volumes（数据库数据 + 媒体文件）
- **恢复流程**：pg_restore 恢复数据库 + 恢复媒体文件目录

### NFR-REL-03: 可用性
- Docker 容器 restart: always（开机自启、崩溃自动重启）
- Gunicorn 进程管理（worker 崩溃自动重启）
- 数据库连接断开自动重连（Django 默认行为）
- 无需高可用集群（单 NAS 部署，可接受短暂停机）

### NFR-REL-04: 监控
- 初期不引入专业监控工具（Prometheus/Grafana）
- 通过 Docker logs + NAS 资源监控满足基本需求
- 后续可考虑添加 Django health check 端点（/api/health/）

---

## 4. 可维护性需求

### NFR-MAINT-01: 代码规范
- Python 代码遵循 PEP 8
- 使用 Django 最佳实践（Fat Models, Thin Views, Service Layer）
- API 使用 DRF ViewSet/Serializer 标准模式
- 统一的错误响应格式

### NFR-MAINT-02: 数据库迁移
- 使用 Django migrations 管理数据库变更
- entrypoint.sh 启动时自动执行 makemigrations + migrate
- 生产环境部署前备份数据库

### NFR-MAINT-03: 环境配置
- 所有配置通过环境变量注入
- .env.example 提供模板
- settings.py 使用 os.environ.get() 读取配置
- Railway 自动注入 DATABASE_URL
