# 用户故事 → 工作单元映射

## Unit 1：后端（furniture-backend）

后端负责所有故事的 API 层实现。

| 故事 | 标题 | 后端涉及 App |
|------|------|-------------|
| US-1.2 | 用户登录 | auth_app |
| US-1.3 | 用户登出 | auth_app |
| US-1.4 | 用户管理 | auth_app |
| US-1.5 | 密码重置 | auth_app |
| US-1.6 | 权限控制 | auth_app |
| US-2.1 | 创建产品 | products |
| US-2.2 | 编辑产品 | products |
| US-2.3 | 删除产品 | products |
| US-2.4 | 查看产品列表 | products |
| US-2.5 | 查看产品详情 | products |
| US-2.6 | 产品上架/下架 | products |
| US-2.7 | 分类管理 | products |
| US-2.8 | 产品多分类关联 | products |
| US-2.9 | 产品图片管理 | products, common |
| US-2.10 | 产品配置管理 | products |
| US-2.11 | 产品搜索 | products |
| US-2.12 | Excel 批量导入 | products |
| US-3.1 | 图册浏览 | catalog |
| US-3.2 | 图册分类导航 | catalog |
| US-4.1 | 创建案例 | cases |
| US-4.2 | 编辑和删除案例 | cases |
| US-4.3 | 案例图片管理 | cases, common |
| US-4.4 | 案例关联产品 | cases |
| US-4.5 | 案例列表与筛选 | cases |
| US-5.1 | 文件夹管理 | documents |
| US-5.2 | 文档上传 | documents, common |
| US-5.3 | 文档下载 | documents |
| US-5.4 | 文档在线预览 | documents |
| US-5.5 | 文档标签与搜索 | documents |
| US-5.6 | 文档分页加载 | documents |
| US-6.1 | 创建报价单 | quotes |
| US-6.2 | 管理报价明细 | quotes |
| US-6.3 | 报价单状态管理 | quotes |
| US-6.4 | 复制报价单 | quotes |
| US-6.5 | PDF 导出 | quotes |
| US-6.6 | 报价单搜索与筛选 | quotes |
| US-7.1 | 创建分享链接 | sharing |
| US-7.2 | 管理分享链接 | sharing |
| US-7.3 | 外部客户访问分享 | sharing |
| US-7.4 | 分享访问追踪 | sharing |
| US-8.1 | 全局搜索 | search |
| US-8.2 | 首页仪表盘 | dashboard |

---

## Unit 2：前端（furniture-frontend）

前端负责所有故事的 UI 层实现。

| 故事 | 标题 | 前端涉及页面/组件 |
|------|------|-------------------|
| US-1.1 | 登录页台灯交互 | LoginPage（GSAP 动画） |
| US-1.2 | 用户登录 | LoginPage, authStore |
| US-1.3 | 用户登出 | MainLayout, authStore |
| US-1.4 | 用户管理 | UserManagementPage |
| US-1.5 | 密码重置 | LoginPage, UserManagementPage |
| US-1.6 | 权限控制 | ProtectedRoute |
| US-2.1~2.3 | 产品 CRUD | ProductFormPage, ProductListPage |
| US-2.4 | 产品列表 | ProductListPage, productStore |
| US-2.5 | 产品详情 | ProductDetailPage |
| US-2.6 | 上架/下架 | ProductListPage, ProductDetailPage |
| US-2.7~2.8 | 分类管理 | CategoryManagementPage, CategoryTree |
| US-2.9 | 产品图片 | ProductDetailPage, ImageUploader |
| US-2.10 | 产品配置 | ProductDetailPage |
| US-2.11 | 产品搜索 | ProductListPage, productStore |
| US-2.12 | Excel 导入 | ProductListPage（导入对话框） |
| US-3.1~3.2 | 产品图册 | CatalogPage, CategoryTree |
| US-4.1~4.3 | 案例管理 | CaseFormPage, CaseListPage, ImageUploader |
| US-4.4~4.5 | 案例关联与筛选 | CaseDetailPage, CaseListPage |
| US-5.1 | 文件夹管理 | DocumentListPage |
| US-5.2~5.4 | 文档操作 | DocumentListPage, FilePreview |
| US-5.5~5.6 | 文档搜索与分页 | DocumentListPage |
| US-6.1~6.3 | 报价单管理 | QuoteFormPage, QuoteListPage, QuoteDetailPage |
| US-6.4~6.6 | 报价复制/PDF/搜索 | QuoteDetailPage, QuoteListPage |
| US-7.1~7.2 | 分享管理 | ShareManagementPage, ShareDialog |
| US-7.3 | 外部访问分享 | ShareViewPage |
| US-7.4 | 访问追踪 | ShareManagementPage |
| US-8.1 | 全局搜索 | GlobalSearch |
| US-8.2 | 首页仪表盘 | DashboardPage, StatCard |

---

## 故事覆盖验证

| 检查项 | 状态 |
|--------|------|
| 全部 30 个故事已分配到 Unit 1（后端） | ✅ |
| 全部 30 个故事已分配到 Unit 2（前端） | ✅ |
| US-1.1（台灯交互）仅在 Unit 2 | ✅ 纯前端动画 |
| 无遗漏故事 | ✅ |
