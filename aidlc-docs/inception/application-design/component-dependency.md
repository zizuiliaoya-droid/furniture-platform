# 组件依赖关系

## 后端组件依赖矩阵

```
                auth  products  catalog  cases  documents  quotes  sharing  search  dashboard  common
auth_app         -      -         -       -       -         -        -        -        -         ✓
products         ✓      -         -       -       -         -        -        -        -         ✓
catalog          -      ✓         -       -       -         -        -        -        -         ✓
cases            ✓      ✓         -       -       -         -        -        -        -         ✓
documents        ✓      -         -       -       -         -        -        -        -         ✓
quotes           ✓      ✓         -       -       -         -        -        -        -         ✓
sharing          ✓      ✓         ✓       ✓       -         ✓        -        -        -         -
search           ✓      ✓         -       ✓       ✓         ✓        -        -        -         -
dashboard        -      ✓         -       ✓       -         ✓        -        -        -         -
common           -      -         -       -       -         -        -        -        -         -
```

**读法**: 行依赖列。例如 sharing 行的 products 列为 ✓，表示 sharing 依赖 products。

### 依赖说明

| 依赖关系 | 类型 | 说明 |
|----------|------|------|
| products → auth_app | FK | Product.created_by → User |
| products → common | 调用 | FileStorageService（图片上传/缩略图） |
| catalog → products | 查询 | 复用 Product/ProductImage 模型 |
| cases → products | M2M | CaseProduct 关联表 |
| cases → common | 调用 | FileStorageService（案例图片） |
| documents → common | 调用 | FileStorageService（文档上传） |
| quotes → products | FK | QuoteItem.product → Product |
| sharing → products/cases/quotes/catalog | 查询 | 根据 content_type 查询对应模块数据 |
| search → products/cases/documents/quotes | 查询 | 跨模块关键词搜索 |
| dashboard → products/cases/quotes | 查询 | 聚合统计数据 |

---

## 前端组件依赖关系

### 页面 → 服务依赖

```
LoginPage          → authService, authStore
DashboardPage      → dashboardService
UserManagementPage → authService
ProductListPage    → productService, productStore
ProductDetailPage  → productService, shareService
ProductFormPage    → productService
CategoryMgmtPage   → productService
CatalogPage        → productService (catalog endpoints)
CaseListPage       → caseService
CaseDetailPage     → caseService, productService
CaseFormPage       → caseService, productService
DocumentListPage   → documentService
QuoteListPage      → quoteService
QuoteDetailPage    → quoteService, shareService
QuoteFormPage      → quoteService, productService
ShareMgmtPage      → shareService
ShareViewPage      → shareService
```

### 公共组件 → 服务依赖

```
GlobalSearch    → searchService
ProtectedRoute  → authStore
ImageUploader   → (接收 upload callback prop)
CategoryTree    → productService
ShareDialog     → shareService
```

---

## 前后端通信模式

### 通信协议
- **协议**: REST API over HTTPS
- **数据格式**: JSON
- **认证**: Token Authentication (Authorization: Token {token})
- **分页**: ?page=1&page_size=20 → { count, next, previous, results }

### 环境配置

| 环境 | 前端 → 后端 |
|------|-------------|
| 本地开发 | Vite proxy → localhost:8000 |
| 测试环境 | Vercel → Railway (VITE_API_BASE_URL) |
| 生产环境 | Nginx /api/* → backend:8000 |

### 文件上传模式
- **Content-Type**: multipart/form-data
- **多文件**: 同一字段名多次传递
- **大小限制**: 图片 10MB，文档 50MB
- **响应**: 返回文件路径和缩略图路径
