# AI-DLC State Tracking

## Language Selection
- **Language**: 中文 (Chinese)
- **Selected At**: 2026-04-23T00:00:00Z

## Project Information
- **Project Name**: 家具软装内部管理平台
- **Project Type**: Brownfield（棕地，存在完整 backend + frontend 实现，进入新一轮迭代）
- **Start Date**: 2026-04-23T00:00:00Z
- **Last Iteration**: 2026-05 优化迭代 — CONSTRUCTION 全量完成 + 核心链路强化 + 上线 Zeabur（2026-06-19）
- **Current Iteration**: 2026-07-24 客户横向模板与体验链路加固
- **Current Stage**: CONSTRUCTION - 发布前审计整改完成并通过验证，等待 GitHub 自动部署验收
- **Live URLs**: 前端 https://furniture-zk.zeabur.app ｜ 后端 https://furniture-api-zk.zeabur.app（本轮尚未部署）
- **Test Login**: admin / admin123456

## User Request
按照提供的开发文档和需求文档开发，后续给用户测试采用临时方案（railway+vercel的部署方式），测试通过后部署到用户的私有云上，登录页采用interactive-dark-login.md来开发

## Workspace State
- **Existing Code**: No
- **Reverse Engineering Needed**: No
- **Workspace Root**: .
- **Existing Documents**: 开发文档.md, 需求文档.md

## Code Location Rules
- **Application Code**: Workspace root (NEVER in aidlc-docs/)
- **Documentation**: aidlc-docs/ only

## Stage Progress
### INCEPTION
- [x] Workspace Detection — Greenfield project detected
- [x] Requirements Analysis — Standard depth, 10 questions + 1 clarification resolved
- [x] User Stories — 3 personas, 30 stories (US-1.1 ~ US-8.2), Given-When-Then format
- [x] Workflow Planning — 执行计划已生成
- [x] Application Design — 4 artifacts generated
- [x] Units Generation — 2 units (backend → frontend), 3 artifacts

### CONSTRUCTION
- [x] Functional Design — 3 artifacts (domain-entities, business-rules, business-logic-model)
- [x] NFR Requirements — 2 artifacts (nfr-requirements, tech-stack-decisions)
- [x] NFR Design — 2 artifacts (nfr-design-patterns, logical-components)
- [x] Infrastructure Design — 2 artifacts (infrastructure-design, deployment-architecture)
- [x] Code Generation (Unit 1 Backend) — 13 steps complete, 61 API endpoints
- [x] Code Generation (Unit 2 Frontend) — 9 steps complete, 17 pages, 19 routes
- [x] Build and Test — 4 instruction documents generated
- [ ] Build and Test — EXECUTE

### OPERATIONS
- [ ] Operations (Placeholder)

---

## 2026-05 Optimization Iteration

### INCEPTION (Brownfield Re-entry)
- [x] Workspace Detection — 检测到棕地项目 + 文档大幅更新
- [x] Gap Analysis — 12 个差距已识别（详见 inception/gap-analysis.md）
- [x] Scope Approval — Q1=A 全量 / Q2=A 清库重建 / Q3=E 自定义 8 大办公分类 / Q4=A 完整 Excel 导入 / Q5=D 完整聚合
- [x] Workflow Planning (revised) — 3 工作单元 16 步
- [x] Per-unit Construction loops — 后端 5 新模型 + 前端重写全部完成

### CONSTRUCTION (Optimization)
- [x] 后端：Brand / ProductConfigDimension / ProductPriceMatrix / ProductPriceRule / ProductDocument + Product 字段重构 + QuoteItem 扩展 + Case 行业枚举
- [x] 前端：图册重写 / 产品详情电商式选购 / 报价 CRUD / 文档预览
- [x] 核心链路强化 6 项修复 + 21/21 单元测试通过

### OPERATIONS
- [x] 种子数据命令 seed_demo（幂等，参考真实椅子配置）
- [x] 部署适配（nginx 模板 / Dockerfile / settings / urls / zbpack）
- [x] 推送 GitHub（zizuiliaoya-droid/furniture-platform）
- [x] Zeabur 香港节点部署：PostgreSQL + 后端 + 前端全部 RUNNING
- [x] 线上验收：登录 / 图册 / 案例 / 品牌 / 算价 / 前端代理全部通过
- [ ] 用户手动：Zeabur 连接 GitHub App 启用 push-to-deploy
- [ ] 用户手动：后端 /app/media 挂载持久化 Volume

### Identified Gaps
- G-1 Product 字段重构（category_l1/l2 / brand / lead_time / 尺寸 / pricing_mode / base_price）
- G-2 双模式价格引擎（ProductConfigDimension + Matrix + Rule + calculate-price）
- G-3 产品配置 Excel 导入（template + parse + preview + confirm）
- G-4 ProductDocument M2M 关联
- G-5 Brand 品牌字典
- G-6 图册搜索体验重构（取消 Tree + 悬浮筛选 + MECE + 即时查询）
- G-7 产品详情页电商式选购（ConfigSelector + PriceDisplay + AddToQuoteModal）
- G-8 报价单 QuoteItem 字段扩展 + from-product 一键加入 + 明细 CRUD
- G-9 客户案例行业树 + 排序 + 图片懒加载/WebP
- G-10 文档在线预览 + 培训资料富文本
- G-11 分享功能批量 + 品牌展示
- G-12 旧分类体系过渡兼容收尾


## 2026-07-24 客户横向模板与体验链路加固迭代

### CONSTRUCTION
- [x] 执行计划批准：`construction/plans/customer-template-and-ux-hardening-plan.md`
- [x] 客户横向多 Sheet 模板、组合价格 Matrix、完整默认 preset
- [x] 产品基本信息 + 图片 + 配置事务化一页创建
- [x] 固定价产品加入报价、默认封面、中文配置摘要
- [x] `itemId` 原位改配置，不新增重复报价明细
- [x] 报价 Excel 嵌图、仅整单折扣、分享候选排重
- [x] 用户编辑/部门/密码重置与超级管理员保护
- [x] 产品/报价模块权限及对象级写入硬校验
- [x] 客户原始 Excel 4 Sheet 只读解析回归
- [x] Django 迁移检查：No changes detected
- [x] SQLite pytest：49 passed
- [x] 前端 TypeScript + Vite 生产构建通过
- [x] 2026-07-25 发布前审计方案 B：导入、报价、账户、权限、体验和部署入口 11 项整改完成
- [x] 权限矩阵后端闭环：产品/图册/案例/文档/报价/分享及聚合入口
- [x] 整改后 SQLite pytest：62 passed；真实客户 Excel 4 产品、0 error

### DELIVERY
- [x] 软件修改记录、执行计划和审计日志已更新
- [ ] 客户统一验收
- [x] Git commit / push（2026-07-25 用户明确批准，推送 `origin/main`）
- [ ] Zeabur 自动部署与线上验收
