# 逻辑组件 — Unit 1 后端

## 组件架构图（文本）

```
                    ┌─────────────────────────────────────────┐
                    │              客户端请求                    │
                    └──────────────────┬──────────────────────┘
                                       │
                    ┌──────────────────▼──────────────────────┐
                    │         Gunicorn (WSGI Server)           │
                    │         4 workers × 2 threads            │
                    └──────────────────┬──────────────────────┘
                                       │
                    ┌──────────────────▼──────────────────────┐
                    │         Django Middleware Stack           │
                    │  SecurityMiddleware                       │
                    │  WhiteNoiseMiddleware (静态文件)           │
                    │  CorsMiddleware (CORS)                    │
                    │  SessionMiddleware                        │
                    │  AuthenticationMiddleware                 │
                    └──────────────────┬──────────────────────┘
                                       │
          ┌────────────────────────────┼────────────────────────────┐
          │                            │                            │
    ┌─────▼─────┐              ┌──────▼──────┐              ┌─────▼─────┐
    │  URL Router│              │ Static Files │              │Media Files│
    │  /api/*    │              │ /static/*    │              │ /media/*  │
    └─────┬─────┘              │ (WhiteNoise) │              │ (Django)  │
          │                    └─────────────┘              └───────────┘
          │
    ┌─────▼──────────────────────────────────────────────────────────┐
    │                    DRF View Layer                               │
    │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
    │  │ AuthViews│ │ProductVS │ │ QuoteVS  │ │ ShareVS  │  ...     │
    │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘          │
    └───────┼────────────┼────────────┼────────────┼─────────────────┘
            │            │            │            │
    ┌───────▼────────────▼────────────▼────────────▼─────────────────┐
    │                  Serializer Layer                               │
    │  数据验证 + 序列化/反序列化                                       │
    └───────┬────────────┬────────────┬────────────┬─────────────────┘
            │            │            │            │
    ┌───────▼────────────▼────────────▼────────────▼─────────────────┐
    │                   Service Layer                                 │
    │  ┌───────────┐ ┌────────────┐ ┌────────────┐ ┌──────────────┐ │
    │  │AuthService│ │ProductImport│ │QuoteService│ │ShareService  │ │
    │  │           │ │Service     │ │            │ │              │ │
    │  └─────┬─────┘ └─────┬──────┘ └─────┬──────┘ └──────┬───────┘ │
    │        │              │              │               │         │
    │  ┌─────▼──────────────▼──────────────▼───────────────▼───────┐ │
    │  │              FileStorageService                            │ │
    │  │  upload() / delete() / generate_thumbnail()               │ │
    │  └───────────────────────┬───────────────────────────────────┘ │
    └──────────────────────────┼─────────────────────────────────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
    ┌───────▼───────┐  ┌──────▼──────┐   ┌──────▼──────┐
    │  PostgreSQL   │  │ File System  │   │  WeasyPrint │
    │  Database     │  │ MEDIA_ROOT   │   │  PDF Engine │
    │  (16)         │  │              │   │             │
    └───────────────┘  └─────────────┘   └─────────────┘
```

---

## 逻辑组件清单

### 1. Web 服务器层

| 组件 | 技术 | 职责 |
|------|------|------|
| WSGI Server | Gunicorn | 接收 HTTP 请求，分发到 Django workers |
| Reverse Proxy | Nginx（仅生产） | 静态文件/媒体文件服务，API 反向代理 |

### 2. 中间件层

| 组件 | 职责 |
|------|------|
| SecurityMiddleware | HTTPS 重定向、安全头 |
| WhiteNoiseMiddleware | 静态文件压缩和服务（测试环境） |
| CorsMiddleware | CORS 跨域处理 |
| AuthenticationMiddleware | Token 认证 |

### 3. 应用层

| 组件 | 职责 |
|------|------|
| URL Router | 请求路由分发 |
| DRF Views | API 端点处理、权限检查 |
| Serializers | 数据验证、序列化 |
| Services | 业务逻辑编排 |
| Models | 数据访问、ORM |

### 4. 基础设施层

| 组件 | 技术 | 职责 |
|------|------|------|
| 关系数据库 | PostgreSQL 16 | 数据持久化 |
| 文件系统 | 本地磁盘 / Railway Volume | 媒体文件存储 |
| PDF 引擎 | WeasyPrint | HTML→PDF 转换 |

### 5. 横切关注点

| 组件 | 职责 |
|------|------|
| FileStorageService | 统一文件上传/删除/缩略图 |
| StandardPagination | 统一分页配置 |
| CustomExceptionHandler | 统一错误响应格式 |
| Logging | 统一日志输出（stdout） |

---

## 数据流路径

### 典型 API 请求流
```
Client → Gunicorn → Middleware → Router → View → Serializer → Service → Model → PostgreSQL
                                                                                    ↓
Client ← Gunicorn ← Middleware ← Router ← View ← Serializer ← ← ← ← ← ← ← Response
```

### 文件上传流
```
Client (multipart) → View → validate size/type → FileStorageService.upload()
                                                        ↓
                                                  Save to MEDIA_ROOT
                                                        ↓
                                                  generate_thumbnail() × 2
                                                        ↓
                                                  Create DB record
```

### PDF 导出流
```
Client → QuoteView.pdf() → QuoteService.export_pdf()
                                    ↓
                              Load Quote + Items
                                    ↓
                              Render HTML template
                                    ↓
                              WeasyPrint → PDF bytes
                                    ↓
                              Response (application/pdf)
```
