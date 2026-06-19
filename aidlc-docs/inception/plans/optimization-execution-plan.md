# 执行计划 — 2026-05 优化迭代（全量 P0~P5）

> **生成时间**：2026-05-18
> **迭代范围**：一次做完全部 12 个差距（Q1=A）
> **数据策略**：清库重建（Q2=A）
> **案例行业**：精简 8 大办公空间分类 + 其他（Q3=E 自定义）
> **Excel 导入**：本轮完整交付（含模板 + 解析 + UI + 手工录入兜底）（Q4=A）
> **图册聚合**：ConfigDimension.options + 长/宽/高 MECE + 价格 MECE（Q5=D）

---

## 一、变更影响评估

| 维度 | 影响 |
|---|---|
| 用户体验 | ✅ 重大（图册重写、详情页电商化、报价单明细 CRUD、文档预览、分享品牌展示） |
| 数据模型 | ✅ 重大（Product 字段重构 + 5 张新表 + QuoteItem 扩展 + Case 行业枚举） |
| API 接口 | ✅ 重大（新增 ~20 个端点，改造 ~10 个端点） |
| 基础设施 | ⚠️ 轻微（部署架构不变，仅 requirements.txt 可能新增依赖） |
| NFR | ⚠️ 轻微（价格计算 < 300ms 是新性能约束，其余不变） |

**风险等级**：Medium-High（模型重构 + 全量改造，但无正式数据可清库）
**回滚复杂度**：Low（清库重建 + Git 分支管理）

---

## 二、工作单元划分

由于全量一次做完，按**依赖顺序**拆为 3 个工作单元：

| 单元 | 名称 | 内容 | 依赖 |
|---|---|---|---|
| Unit A | 后端模型 + API 重构 | P0 全部 + P1/P2/P3/P4/P5 后端部分 | 无 |
| Unit B | 前端核心重构 | P1 图册 + P2 详情页电商化 + P2 报价单 CRUD | Unit A |
| Unit C | 前端增强模块 | P3 文档预览/富文本 + P4 案例 + P5 分享 | Unit A |

> Unit B 和 Unit C 可并行（互不依赖），但都依赖 Unit A 完成。

---

## 三、阶段决策

### 🔵 INCEPTION PHASE（本轮已完成）

| 阶段 | 状态 | 理由 |
|---|---|---|
| Workspace Detection | ✅ COMPLETED | 已检测为棕地 + 文档更新 |
| Reverse Engineering | ✅ COMPLETED | 已通过代码抽样完成差距分析 |
| Requirements Analysis | ✅ COMPLETED | 差距清单 + 5 题审批 = 需求确认 |
| User Stories | ⏭ SKIP | 上一轮 30 个故事仍有效，本轮是增量优化 |
| Workflow Planning | 🔄 IN PROGRESS | 本文件 |
| Application Design | ⏭ SKIP | 组件结构不变，仅扩展字段和新增子模块 |
| Units Generation | ✅ COMPLETED | 上方已划分 3 个单元 |

### 🟢 CONSTRUCTION PHASE

| 阶段 | 状态 | 理由 |
|---|---|---|
| Functional Design | ⏭ SKIP | 开发文档 §3/§9 已有完整模型定义和业务逻辑伪代码 |
| NFR Requirements | ⏭ SKIP | 上一轮 NFR 仍有效，仅新增 calculate-price < 300ms 约束（已记录） |
| NFR Design | ⏭ SKIP | 技术栈不变，设计模式不变 |
| Infrastructure Design | ⏭ SKIP | 部署架构不变（Railway + NAS Docker Compose） |
| Code Generation (Unit A) | 🔜 EXECUTE | 后端模型 + API 全面重构 |
| Code Generation (Unit B) | 🔜 EXECUTE | 前端核心重构 |
| Code Generation (Unit C) | 🔜 EXECUTE | 前端增强模块 |
| Build and Test | 🔜 EXECUTE | 构建验证 + 测试指导 |

---

## 四、Unit A — 后端模型 + API 重构（详细步骤）

### Step A-1：数据模型重构
- [x] 新增 `Brand` 模型
- [x] `Product` 模型新增字段：`category_l1 / category_l2 / brand(FK) / lead_time / pricing_mode / base_price / length_mm / width_mm / height_mm / official_url / material_album / model_3d_url`
- [x] 新增 `ProductConfigDimension` 模型
- [x] 新增 `ProductPriceMatrix` 模型
- [x] 新增 `ProductPriceRule` 模型
- [x] 新增 `ProductDocument` 模型
- [x] `QuoteItem` 新增字段：`config_attributes / image(FK→ProductImage) / image_url`
- [x] `Case.INDUSTRY_CHOICES` 更新为 8 大办公空间分类 + 其他
- [x] `Case.Meta.ordering` 改为 `['title']`（按名称升序）
- [x] 清除旧迁移（待 Django 环境生成新迁移）

### Step A-2：品牌 CRUD API
- [x] `brands/` 在 products 内新增 BrandViewSet
- [x] `GET/POST/PATCH/DELETE /api/brands/`
- [x] 序列化器 + URL 注册

### Step A-3：产品 API 扩展
- [x] 更新 ProductSerializer（新字段 + 嵌套 brand / config_dimensions / documents）
- [x] `GET /api/products/category-options/`（一级 + 二级枚举）
- [x] `GET /api/products/{id}/config-dimensions/`
- [x] `POST /api/products/{id}/calculate-price/`（PriceCalculationService）
- [x] `POST /api/products/{id}/upload-config-excel/`（ConfigExcelService：parse → preview → confirm）
- [x] `GET /api/products/config-template/`（生成标准模板 xlsx）
- [x] `GET/POST/DELETE /api/products/{id}/documents/`（ProductDocument CRUD）
- [x] 更新产品列表筛选（支持 category_l1 / category_l2 / brand / lead_time / origin / is_active）

### Step A-4：图册 API 重构
- [x] `GET /api/catalog/`（多维多选筛选：brand[] / category_l1[] / category_l2[] / origin[] / lead_time[] / length_range / width_range / height_range / price_range / 动态属性[]）
- [x] `GET /api/catalog/filters/`（聚合接口：品牌列表 / 类别枚举 / 产地 / 货期 / MECE 区间预设 / ConfigDimension 动态属性）
- [x] `GET /api/catalog/search/`（全字段关键词搜索升级）

### Step A-5：报价单 API 扩展
- [x] `POST /api/quotes/{id}/items/from-product/`（一键加入：算价 + 写明细 + 重算总价）
- [x] QuoteItem 序列化器更新（含 config_attributes / image_url）
- [x] duplicate 服务更新（复制新字段）
- [ ] PDF 模板更新（明细行含展示图 + 配置摘要）

### Step A-6：案例 + 文档 + 分享后端
- [x] Case 行业枚举更新 + 排序更新（已在 A-1 完成）
- [x] Document 模型扩展（resource_type 字段，支持 RICH_TEXT / FILE / VIDEO / AUDIO + content 字段）
- [x] ShareLink 支持批量分享（content_type=BATCH + object_ids JSON）
- [x] 分享页品牌信息（BrandingConfig 单例模型 + share/{token}/ 响应附带 branding）
- [x] PDF 模板更新（明细行含展示图 + 配置摘要）

### Step A-7：数据库重建 + 初始数据
- [ ] 删除所有旧迁移文件（已完成）
- [ ] `makemigrations` 全部 app（需 Django 环境）
- [ ] `migrate`（清库重建）
- [ ] 初始管理员创建脚本保持不变
- [ ] 可选：预置品牌数据（ZIKOO + 国际品牌）

---

## 五、Unit B — 前端核心重构（详细步骤）

### Step B-1：API Service 层更新
- [x] `productService.ts` 新增：getConfigDimensions / calculatePrice / uploadConfigExcel / downloadConfigTemplate / getProductDocuments / linkDocument / unlinkDocument / getCategoryOptions
- [x] `quoteService.ts` 新增：addItemFromProduct
- [x] 新增 `brandService.ts`：getBrands / createBrand / updateBrand / deleteBrand
- [x] `catalogService.ts`（新建）：getCatalog / getCatalogFilters / searchCatalog

### Step B-2：产品图册页面重写（CatalogPage）
- [x] 移除左侧 Tree 导航
- [x] 新增悬浮筛选面板（Drawer：品牌多选 / 产地 / 货期 / MECE 区间 / 动态属性）
- [x] 新增多级类别标签（一级 → 二级展开）
- [x] 即时查询（debounce 300ms）
- [x] 已选条件面包屑 + 可移除
- [x] 支持 `?quoteId=` 上下文（从报价单跳入选品）

### Step B-3：产品详情页重构（ProductDetailPage）
- [x] 配置选择器（动态渲染维度、级联、debounce 触发 calculate-price）
- [x] 实时价格展示（价格 + 配置面包屑；无效组合提示）
- [x] 加入报价单弹窗（选目标报价单 + 数量/折扣 + 图集选图）
- [x] 关联文档分组展示（设计/培训/资质）
- [x] 基础信息区更新（品牌 / 产地 / 货期 / 尺寸 / 官网 / 3D）

### Step B-4：产品表单页更新（ProductFormPage）
- [x] 一级/二级类别级联下拉
- [x] 品牌下拉
- [x] 货期 / 定价模式 / 基准价 / 尺寸
- [x] 配置 Excel 导入（上传 + 预览 + 确认）
- [x] 管理员手工录入维度 UI（兜底）

### Step B-5：报价单详情页增强（QuoteDetailPage）
- [x] 明细表格增加"展示图"列
- [x] 明细行内编辑（数量 / 折扣 / 删除）
- [x] 「新增明细」按钮 → 跳转 `/catalog?quoteId={id}`
- [x] 配置摘要列 + 合计行

---

## 六、Unit C — 前端增强模块（详细步骤）

### Step C-1：文档在线预览 + 富文本
- [x] 新增 `<MediaPreview />`（图片模态框 / PDF 内嵌 / 视频 HTML5 / 音频 HTML5 / Office 预览）
- [x] DocumentListPage 增加预览按钮（根据 mime_type 调用 MediaPreview）
- [ ] 新增 `<RichTextUploader />`（培训资料富文本编辑器 — 需引入 TinyMCE/Quill，下一步细化）

### Step C-2：客户案例增强
- [x] CaseListPage 行业筛选改为标签式（8 大 + 其他）
- [x] 默认排序改为按名称升序（后端已改 ordering）
- [x] CaseDetailPage 图片平铺 + 懒加载（loading="lazy"）+ 缩略图 + 占位符

### Step C-3：分享功能增强
- [x] ShareViewPage 顶部增加品牌头部（Logo / 公司名 / 联系方式）
- [x] ShareViewPage 支持 batch_cases 类型展示（批量案例分享）

---

## 七、Build and Test

- [ ] 后端：`makemigrations` + `migrate` + `python manage.py runserver` 验证
- [ ] 前端：`npm install` + `npm run build` 验证
- [ ] Docker Compose：`docker-compose up --build` 端到端验证
- [ ] 核心链路手动验证：上传配置 Excel → 详情页选配 → 算价 → 加入报价单 → PDF 导出

---

## 八、成功标准

- ✅ 管理员上传配置 Excel 后，产品详情页动态渲染配置选择器
- ✅ 用户每次更改配置，价格在 300ms 内更新
- ✅ 模式 A 无映射组合 → UI 提示 + 禁用「加入报价单」
- ✅ 模式 B 基准价 + delta 累加正确
- ✅ 「加入报价单」可选已有报价单或新建 + 选图
- ✅ 报价单明细落库后 total_amount 自动重算
- ✅ 报价单详情页明细可编辑/删除/选图
- ✅ 「新增明细」跳转 `/catalog?quoteId={id}` 选品回流
- ✅ 图册取消左侧树，悬浮筛选 + MECE + 即时查询 + 多级类别标签
- ✅ 文档在线预览（图片/PDF/视频/音频）
- ✅ 案例行业树筛选 + 按名称排序 + 图片懒加载
- ✅ 分享页品牌展示 + 批量分享

---

## 九、预计时间线

| 单元 | 预计步骤数 | 预计交互轮次 |
|---|---|---|
| Unit A（后端） | 7 步 | 1-2 轮（生成 + 审批） |
| Unit B（前端核心） | 5 步 | 1-2 轮 |
| Unit C（前端增强） | 3 步 | 1 轮 |
| Build and Test | 1 步 | 1 轮 |
| **合计** | **16 步** | **4-6 轮** |
