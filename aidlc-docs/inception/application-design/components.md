# 组件定义

## 后端组件（Django Apps）

### 1. auth_app — 认证与用户管理
- **职责**: 用户认证、Token 管理、用户 CRUD、角色权限控制
- **模型**: User（扩展 AbstractUser）
- **接口**: /api/auth/*
- **关键能力**: 登录/登出、Token 生成/销毁、用户状态切换、密码重置、IsAdminRole 权限类

### 2. products — 产品管理
- **职责**: 产品 CRUD、分类管理、图片管理、配置管理、Excel 批量导入
- **模型**: Category, Product, ProductImage, ProductConfig, ProductCategory
- **接口**: /api/products/*, /api/categories/*
- **关键能力**: 三维度树形分类、多图上传+缩略图、多配置价格、全字段搜索、拖拽排序、批量导入

### 3. catalog — 产品图册（只读）
- **职责**: 面向内部用户的产品图册浏览和搜索
- **模型**: 无（复用 products 模型）
- **接口**: /api/catalog/*
- **关键能力**: 卡片式浏览、分类导航筛选、分页加载

### 4. cases — 客户案例
- **职责**: 案例 CRUD、案例图片管理、案例-产品关联
- **模型**: Case, CaseImage, CaseProduct
- **接口**: /api/cases/*
- **关键能力**: 9 大行业分类、多图上传+缩略图、关联产品

### 5. documents — 内部文档
- **职责**: 文件夹管理、文档上传/下载/预览、标签管理
- **模型**: DocumentFolder, Document
- **接口**: /api/documents/*, /api/document-folders/*
- **关键能力**: 树形文件夹、三种文档类型、在线预览、标签系统、分页加载

### 6. quotes — 报价方案
- **职责**: 报价单 CRUD、明细管理、金额计算、PDF 导出、报价复制
- **模型**: Quote, QuoteItem
- **接口**: /api/quotes/*
- **关键能力**: 自动金额计算、状态流转、WeasyPrint PDF 生成、一键复制

### 7. sharing — 分享功能
- **职责**: 分享链接 CRUD、公开访问验证、访问记录、点击追踪
- **模型**: ShareLink, ShareAccessLog, ClickTrackingLog（新增）
- **接口**: /api/shares/*, /api/share/{token}/*
- **关键能力**: UUID 链接、密码验证、过期/次数控制、点击追踪统计

### 8. search — 全局搜索
- **职责**: 跨模块关键词搜索
- **模型**: 无（跨模块查询）
- **接口**: /api/search/
- **关键能力**: 同时搜索产品/案例/文档/报价单

### 9. dashboard — 仪表盘统计（新增）
- **职责**: 聚合各模块统计数据，提供首页仪表盘 API
- **模型**: 无（聚合查询）
- **接口**: /api/dashboard/stats/
- **关键能力**: 产品/案例/报价统计、最近活动、本月新增

### 10. common — 公共工具
- **职责**: 文件存储服务、分页配置、全局异常处理
- **模型**: 无
- **关键能力**: FileStorageService（上传/删除/缩略图）、StandardPagination、全局异常处理器

---

## 前端组件

### 页面组件（pages/）

| 目录 | 页面 | 说明 |
|------|------|------|
| auth/ | LoginPage | 台灯交互暗色登录页 |
| auth/ | UserManagementPage | 用户管理（管理员） |
| dashboard/ | DashboardPage | 首页仪表盘（新增） |
| products/ | ProductListPage | 产品列表 |
| products/ | ProductDetailPage | 产品详情 |
| products/ | ProductFormPage | 产品新建/编辑 |
| products/ | CategoryManagementPage | 分类管理 |
| catalog/ | CatalogPage | 产品图册 |
| cases/ | CaseListPage | 案例列表 |
| cases/ | CaseDetailPage | 案例详情 |
| cases/ | CaseFormPage | 案例新建/编辑 |
| documents/ | DocumentListPage | 文档列表（三种类型共用） |
| quotes/ | QuoteListPage | 报价单列表 |
| quotes/ | QuoteDetailPage | 报价单详情 |
| quotes/ | QuoteFormPage | 报价单新建/编辑 |
| sharing/ | ShareManagementPage | 分享管理 |
| sharing/ | ShareViewPage | 分享查看（公开） |

### 公共组件（components/）

| 组件 | 说明 |
|------|------|
| ProtectedRoute | 路由守卫（认证+权限） |
| GlobalSearch | 全局搜索下拉组件 |
| ImageUploader | 通用图片上传组件（多图、排序、封面） |
| FilePreview | 文件在线预览组件（图片/PDF/音频/视频） |
| CategoryTree | 分类树组件（可复用于产品、图册） |
| ShareDialog | 分享链接创建对话框 |
| StatCard | 统计卡片组件（仪表盘用） |

### 布局组件（layouts/）

| 组件 | 说明 |
|------|------|
| MainLayout | 主布局（侧边栏+顶栏+内容区） |
| Sidebar | 侧边导航菜单 |

### 服务层（services/）

| 服务 | 说明 |
|------|------|
| api.ts | Axios 实例（baseURL、Token 拦截器、401 处理） |
| authService.ts | 登录/登出/用户管理 API |
| productService.ts | 产品/分类/配置/图片 API |
| caseService.ts | 案例 API |
| documentService.ts | 文档/文件夹 API |
| quoteService.ts | 报价单 API |
| shareService.ts | 分享链接 API |
| searchService.ts | 全局搜索 API |
| dashboardService.ts | 仪表盘统计 API（新增） |

### 状态管理（store/）

| Store | 说明 |
|-------|------|
| authStore.ts | 认证状态（token, user, login, logout） |
| productStore.ts | 产品列表状态（分页、筛选、搜索） |
