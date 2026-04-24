# Unit 2 前端代码生成计划

## 单元上下文
- **单元名称**: furniture-frontend
- **技术栈**: React 18 + TypeScript 5 + Ant Design 5.x + Vite 5.x + Zustand + Axios
- **代码位置**: 工作区根目录下的 `frontend/` 目录
- **故事覆盖**: US-1.1 ~ US-8.2（全部 30 个故事的 UI 层）

---

## 代码生成步骤

### Step 1: 项目骨架与配置
- [ ] package.json, vite.config.ts, tsconfig.json
- [ ] vercel.json, nginx.conf, Dockerfile
- [ ] src/main.tsx, src/App.tsx

### Step 2: 主题与样式基础
- [ ] src/theme/antdTheme.ts（包豪斯主题配置）
- [ ] src/styles/global.css（全局样式、字体声明）

### Step 3: API 服务层
- [ ] src/services/api.ts（Axios 实例 + 拦截器）
- [ ] src/services/authService.ts
- [ ] src/services/productService.ts
- [ ] src/services/caseService.ts
- [ ] src/services/documentService.ts
- [ ] src/services/quoteService.ts
- [ ] src/services/shareService.ts
- [ ] src/services/searchService.ts
- [ ] src/services/dashboardService.ts

### Step 4: 状态管理
- [ ] src/store/authStore.ts
- [ ] src/store/productStore.ts

### Step 5: 布局与公共组件
- [ ] src/layouts/MainLayout.tsx
- [ ] src/layouts/Sidebar.tsx
- [ ] src/components/ProtectedRoute.tsx
- [ ] src/components/GlobalSearch.tsx

### Step 6: 登录页（台灯交互）
- [ ] src/pages/auth/LoginPage.tsx（GSAP 台灯动画 + 登录表单）

### Step 7: 核心页面
- [ ] src/pages/dashboard/DashboardPage.tsx
- [ ] src/pages/auth/UserManagementPage.tsx
- [ ] src/pages/products/ProductListPage.tsx
- [ ] src/pages/products/ProductDetailPage.tsx
- [ ] src/pages/products/ProductFormPage.tsx
- [ ] src/pages/products/CategoryManagementPage.tsx
- [ ] src/pages/catalog/CatalogPage.tsx

### Step 8: 业务页面
- [ ] src/pages/cases/CaseListPage.tsx
- [ ] src/pages/cases/CaseDetailPage.tsx
- [ ] src/pages/cases/CaseFormPage.tsx
- [ ] src/pages/documents/DocumentListPage.tsx
- [ ] src/pages/quotes/QuoteListPage.tsx
- [ ] src/pages/quotes/QuoteDetailPage.tsx
- [ ] src/pages/quotes/QuoteFormPage.tsx
- [ ] src/pages/sharing/ShareManagementPage.tsx
- [ ] src/pages/sharing/ShareViewPage.tsx

### Step 9: 代码摘要
- [ ] aidlc-docs/construction/furniture-frontend/code/code-summary.md
