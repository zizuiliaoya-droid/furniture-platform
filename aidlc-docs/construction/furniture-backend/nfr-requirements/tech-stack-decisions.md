# 技术栈决策 — Unit 1 后端

## 核心技术栈

| 技术 | 版本 | 选择理由 |
|------|------|----------|
| **Python** | 3.12+ | 最新稳定版，性能提升，Django 5.x 要求 |
| **Django** | 5.x | 成熟的全栈框架，内置 ORM/Auth/Admin，开发效率高 |
| **Django REST Framework** | 3.15+ | Django 生态最成熟的 REST API 框架 |
| **PostgreSQL** | 16 | 需求文档指定，JSON 字段支持好，Railway 原生支持 |
| **Gunicorn** | 22.x | Python WSGI 服务器标准选择，多 worker 支持 |

## 依赖库

| 库 | 版本 | 用途 | 选择理由 |
|----|------|------|----------|
| **WeasyPrint** | 62.x | PDF 生成 | 需求文档指定，HTML→PDF 转换质量好 |
| **openpyxl** | 3.x | Excel 解析 | 需求文档指定，.xlsx 读写标准库 |
| **Pillow** | 10.x | 图片处理 | 需求文档指定，缩略图生成 |
| **django-cors-headers** | 4.x | CORS 处理 | 前后端分离必需 |
| **dj-database-url** | 2.x | 数据库 URL 解析 | Railway DATABASE_URL 支持 |
| **whitenoise** | 6.x | 静态文件服务 | Railway 环境无 Nginx，需要 Django 直接服务静态文件 |
| **psycopg2-binary** | 2.9+ | PostgreSQL 驱动 | Django + PostgreSQL 标准驱动 |
| **gunicorn** | 22.x | WSGI 服务器 | 生产环境标准选择 |

## 未引入的技术（及理由）

| 技术 | 未引入理由 |
|------|-----------|
| Celery | 初期不需要异步任务队列，缩略图同步生成可满足需求。后续如需异步可引入 |
| Redis | 无缓存需求（数据量小），无 Celery broker 需求 |
| Elasticsearch | 全局搜索使用 Django ORM 即可满足，数据量不大 |
| JWT | 需求文档指定 Token Authentication，DRF Token 更简单 |
| Django Channels | 无 WebSocket 需求 |
| Sentry | 初期通过 Docker logs 满足错误追踪，后续可引入 |

## 部署技术

| 环境 | 技术 | 说明 |
|------|------|------|
| 测试 | Railway | 自动检测 Python 项目，内置 PostgreSQL 插件 |
| 测试 | WhiteNoise | Django 直接服务静态文件（无 Nginx） |
| 生产 | Docker + Gunicorn | Dockerfile 构建，entrypoint.sh 启动 |
| 生产 | Nginx（前端容器） | 反向代理 /api/* 到 backend:8000 |
| 生产 | PostgreSQL 16 Alpine | Docker 容器，数据持久化到 volume |

## Gunicorn 配置建议

| 环境 | Workers | Threads | Timeout |
|------|---------|---------|---------|
| Railway（测试） | 2 | 2 | 120s |
| NAS（生产） | 4 | 2 | 120s |

- Workers 公式：min(2×CPU+1, 8)
- NAS DS920+ 有 4 核 CPU，建议 4 workers
- Timeout 120s 考虑 PDF 生成和大文件上传
