# 工作单元依赖关系

## 单元依赖矩阵

```
              Unit 1 (后端)    Unit 2 (前端)
Unit 1 (后端)     -               -
Unit 2 (前端)     ✓               -
```

**Unit 2 依赖 Unit 1**: 前端所有 API 调用依赖后端接口已实现。

## 关键路径

```
Unit 1 (后端) ──► Unit 2 (前端) ──► 构建与测试
```

- **关键路径**: Unit 1 → Unit 2 → Build & Test
- **可并行部分**: 无（严格顺序依赖）
- **瓶颈**: Unit 1 后端开发是关键路径起点

## 单元间接口契约

### API 契约（Unit 1 → Unit 2）

| 接口组 | 端点数 | 关键接口 |
|--------|--------|----------|
| 认证 | 7 | POST /api/auth/login/, GET /api/auth/me/ |
| 产品 | 14 | GET/POST /api/products/, POST /api/products/import/ |
| 分类 | 6 | GET /api/categories/tree/, PUT /api/categories/reorder/ |
| 图册 | 2 | GET /api/catalog/, GET /api/catalog/search/ |
| 案例 | 7 | GET/POST /api/cases/, POST /api/cases/{id}/upload_images/ |
| 文档 | 8 | POST /api/documents/upload/, GET /api/documents/{id}/download/ |
| 报价 | 9 | GET/POST /api/quotes/, GET /api/quotes/{id}/pdf/ |
| 分享 | 5 | POST /api/shares/, GET /api/share/{token}/ |
| 搜索 | 1 | GET /api/search/?q= |
| 仪表盘 | 1 | GET /api/dashboard/stats/ |
| **合计** | **60** | |

### 数据格式契约
- **认证**: Authorization: Token {token}
- **分页**: { count, next, previous, results }
- **错误**: { detail: "error message" } 或 { field: ["error"] }
- **文件上传**: multipart/form-data
- **文件下载**: application/octet-stream + Content-Disposition

## 部署依赖

### 测试环境
```
Railway (后端 + PostgreSQL) ◄── Vercel (前端)
                                  │
                                  └── VITE_API_BASE_URL 指向 Railway
```

### 生产环境
```
Docker Compose:
  db (PostgreSQL) ◄── backend (Django) ◄── frontend (Nginx)
                                              │
                                              └── /api/* 反向代理到 backend:8000
```
