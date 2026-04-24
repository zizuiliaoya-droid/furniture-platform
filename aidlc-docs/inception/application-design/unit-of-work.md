# 工作单元定义

## 分解策略
按仓库分两大单元，先完成后端全部 API，再开发前端全部页面。

---

## Unit 1：后端（Django + DRF）

### 基本信息
| 属性 | 值 |
|------|-----|
| **单元名称** | furniture-backend |
| **仓库** | 独立 GitHub 仓库 |
| **技术栈** | Django 5.x + DRF 3.15+ + PostgreSQL 16 |
| **部署** | Railway（测试）/ Docker + Gunicorn（生产） |

### 范围
后端全部 10 个 Django App 及其所有 API 接口：

| App | 职责 | API 路由 |
|-----|------|----------|
| config | Django 项目配置、根路由、WSGI | - |
| auth_app | 认证、用户管理、权限 | /api/auth/* |
| products | 产品 CRUD、分类、图片、配置、导入 | /api/products/*, /api/categories/* |
| catalog | 产品图册只读浏览 | /api/catalog/* |
| cases | 客户案例 CRUD、图片、关联产品 | /api/cases/* |
| documents | 文档文件夹、上传/下载 | /api/documents/*, /api/document-folders/* |
| quotes | 报价单 CRUD、明细、PDF 导出 | /api/quotes/* |
| sharing | 分享链接、公开访问、点击追踪 | /api/shares/*, /api/share/{token}/* |
| search | 全局跨模块搜索 | /api/search/ |
| dashboard | 仪表盘统计 | /api/dashboard/* |
| common | 文件存储、分页、异常处理 | - |

### 交付物
- 全部数据模型和数据库迁移
- 全部 REST API 接口
- Token 认证和权限系统
- 文件上传和缩略图生成
- WeasyPrint PDF 导出
- Excel 批量导入
- 初始管理员创建脚本
- Dockerfile + entrypoint.sh
- requirements.txt
- Railway 部署配置

### 代码组织
```
furniture-backend/
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── auth_app/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── permissions.py
│   ├── services.py
│   └── urls.py
├── products/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── services.py
│   └── urls.py
├── catalog/
│   ├── views.py
│   └── urls.py
├── cases/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   └── urls.py
├── documents/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   └── urls.py
├── quotes/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── services.py
│   └── urls.py
├── sharing/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── services.py
│   └── urls.py
├── search/
│   ├── views.py
│   └── urls.py
├── dashboard/
│   ├── views.py
│   ├── services.py
│   └── urls.py
├── common/
│   ├── file_storage.py
│   ├── pagination.py
│   └── exceptions.py
├── scripts/
│   └── create_admin.py
├── entrypoint.sh
├── Dockerfile
├── manage.py
├── requirements.txt
└── .env.example
```

---

## Unit 2：前端（React + TypeScript）

### 基本信息
| 属性 | 值 |
|------|-----|
| **单元名称** | furniture-frontend |
| **仓库** | 独立 GitHub 仓库 |
| **技术栈** | React 18 + TypeScript 5 + Ant Design 5.x + Vite 5.x |
| **部署** | Vercel（测试）/ Docker + Nginx（生产） |

### 范围
前端全部页面、组件、服务层、状态管理：

| 模块 | 页面 |
|------|------|
| 登录 | LoginPage（台灯交互暗色主题） |
| 仪表盘 | DashboardPage |
| 用户管理 | UserManagementPage |
| 产品管理 | ProductListPage, ProductDetailPage, ProductFormPage, CategoryManagementPage |
| 产品图册 | CatalogPage |
| 客户案例 | CaseListPage, CaseDetailPage, CaseFormPage |
| 内部文档 | DocumentListPage |
| 报价方案 | QuoteListPage, QuoteDetailPage, QuoteFormPage |
| 分享 | ShareManagementPage, ShareViewPage |

### 交付物
- 全部页面组件（17 个页面）
- 公共组件（ProtectedRoute, GlobalSearch, ImageUploader, FilePreview, CategoryTree, ShareDialog, StatCard）
- 布局组件（MainLayout, Sidebar）
- 服务层（9 个 Service 文件）
- 状态管理（authStore, productStore）
- 台灯交互登录页（GSAP + MorphSVGPlugin）
- 包豪斯风格 Ant Design 主题定制
- UI UX Pro Max 设计系统集成
- 自托管字体文件
- Vite 配置 + TypeScript 配置
- Nginx 配置
- Dockerfile
- Vercel 部署配置（vercel.json）
- package.json

### 代码组织
```
furniture-frontend/
├── public/
│   └── fonts/                  # 自托管字体文件
│       ├── DMSans/
│       ├── Inter/
│       └── NotoSansSC/
├── src/
│   ├── App.tsx                 # 路由配置
│   ├── main.tsx                # 入口文件
│   ├── theme/                  # 包豪斯主题配置
│   │   └── antdTheme.ts
│   ├── services/               # API 服务层
│   │   ├── api.ts
│   │   ├── authService.ts
│   │   ├── productService.ts
│   │   ├── caseService.ts
│   │   ├── documentService.ts
│   │   ├── quoteService.ts
│   │   ├── shareService.ts
│   │   ├── searchService.ts
│   │   └── dashboardService.ts
│   ├── store/                  # Zustand 状态管理
│   │   ├── authStore.ts
│   │   └── productStore.ts
│   ├── pages/                  # 页面组件
│   │   ├── auth/
│   │   ├── dashboard/
│   │   ├── products/
│   │   ├── catalog/
│   │   ├── cases/
│   │   ├── documents/
│   │   ├── quotes/
│   │   └── sharing/
│   ├── components/             # 公共组件
│   │   ├── ProtectedRoute.tsx
│   │   ├── GlobalSearch.tsx
│   │   ├── ImageUploader.tsx
│   │   ├── FilePreview.tsx
│   │   ├── CategoryTree.tsx
│   │   ├── ShareDialog.tsx
│   │   └── StatCard.tsx
│   └── layouts/                # 布局组件
│       ├── MainLayout.tsx
│       └── Sidebar.tsx
├── nginx.conf
├── Dockerfile
├── package.json
├── vite.config.ts
├── tsconfig.json
├── vercel.json
└── .env.example
```

---

## 开发顺序

```
Unit 1: 后端 ──────────────────────────────► Unit 2: 前端
(Django API 全部完成)                        (React 全部页面)
                                                    │
                                                    ▼
                                            构建与测试
                                            (集成测试 + 部署)
```

**顺序逻辑**: 先完成后端全部 API，确保接口稳定后再开发前端，避免前端因 API 变更频繁返工。
