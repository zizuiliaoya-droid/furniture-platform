# 代码摘要 — Unit 2 前端

## 生成文件清单

| 文件 | 说明 |
|------|------|
| frontend/package.json | 依赖配置 |
| frontend/vite.config.ts | Vite 配置（含 API 代理） |
| frontend/tsconfig.json | TypeScript 配置 |
| frontend/index.html | HTML 入口 |
| frontend/vercel.json | Vercel SPA 路由重写 |
| frontend/nginx.conf | Nginx 配置（API 反向代理+媒体文件） |
| frontend/Dockerfile | Docker 构建（Node build + Nginx） |
| frontend/.env.example | 环境变量模板 |
| frontend/src/main.tsx | 入口（ConfigProvider + 主题） |
| frontend/src/App.tsx | 路由配置（19 条路由） |
| frontend/src/theme/antdTheme.ts | 包豪斯 Ant Design 主题 |
| frontend/src/styles/global.css | 全局样式 + 字体 + 微交互 |
| frontend/src/services/*.ts | 9 个 API 服务文件 |
| frontend/src/store/*.ts | 2 个 Zustand Store |
| frontend/src/layouts/*.tsx | MainLayout + Sidebar |
| frontend/src/components/*.tsx | ProtectedRoute + GlobalSearch |
| frontend/src/pages/auth/LoginPage.tsx | 台灯交互暗色登录页 |
| frontend/src/pages/auth/UserManagementPage.tsx | 用户管理 |
| frontend/src/pages/dashboard/DashboardPage.tsx | 仪表盘 |
| frontend/src/pages/products/*.tsx | 4 个产品页面 |
| frontend/src/pages/catalog/CatalogPage.tsx | 产品图册 |
| frontend/src/pages/cases/*.tsx | 3 个案例页面 |
| frontend/src/pages/documents/DocumentListPage.tsx | 文档管理 |
| frontend/src/pages/quotes/*.tsx | 3 个报价页面 |
| frontend/src/pages/sharing/*.tsx | 分享管理 + 分享查看 |

## 页面统计
- 17 个页面组件
- 2 个公共组件
- 2 个布局组件
- 9 个 API 服务
- 2 个状态 Store
- 19 条前端路由

## 用户故事覆盖
全部 30 个故事的 UI 层已实现。
