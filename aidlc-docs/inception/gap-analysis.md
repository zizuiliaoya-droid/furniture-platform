# 差距分析报告 — 文档 vs 现有实现

> **生成时间**：2026-05-18
> **触发请求**：用户更新了《开发文档.md》和《需求文档.md》，要求对比现有实现并提出优化方案。
> **结论速览**：文档已经描述了新一轮重大改造（产品字段重构 + 电商式选购 + 配置 Excel 导入 + 图册搜索体验重构 + 案例行业树 + 文档在线预览/富文本 + 分享品牌展示），但**代码层 95% 仍为初始实现**。这次迭代实质是把文档已规划但**从未落地**的优化项真正实现一遍。

---

## 一、扫描范围

| 文档 | 已加载 | 关键变更 |
|---|---|---|
| 开发文档.md | ✅ | §3 数据模型已含 Brand / ProductConfigDimension / ProductPriceMatrix / ProductPriceRule / ProductDocument；§4 API 已含 calculate-price / from-product / catalog filters；§9 业务逻辑已含 OPT-5/6 |
| 需求文档.md | ✅ | §2.2~2.4 产品/详情/图册全面重写；§3 核心业务流程图（配置→算价→加单）；§5.2 本轮变更明确列出 11 项采纳 + 3 项剔除 |
| optimization-plan.md | ✅ | 与 2 份文档一致，P0/P1/P2 列出全部新模型与新 API |

| 代码区域 | 已抽样 | 状态 |
|---|---|---|
| backend/products/models.py | ✅ | **旧版**（无 Brand / 无 category_l1/l2 / 无 pricing_mode / 无 5 张新表） |
| backend/products/urls.py | ✅ | **旧版**（无 calculate-price / config-dimensions / config-template / brands / category-options / products/{id}/documents 路由） |
| backend/quotes/models.py | ✅ | **旧版**（QuoteItem 无 config_attributes / image / image_url） |
| backend/quotes/urls.py | ✅ | **旧版**（无 from-product 路由） |
| backend/catalog/views.py | ✅ | **旧版**（仅 q + category 过滤；无 filters/聚合、无 MECE、无多维多选） |
| backend/cases/models.py | ✅ | 行业枚举与"办公空间 8 大细分"不一致（当前为 TECH/FINANCE/REALESTATE/EDUCATION/MEDICAL/MEDIA/MANUFACTURE/GOVERNMENT/OTHER） |
| backend/documents/models.py | ✅ | 缺富文本支持（无 content / resource_type 字段） |
| frontend/src/services/productService.ts | ✅ | 无 calculate-price / config-dimensions / upload-config-excel / linkDocument / getCategoryOptions 等任意新 API 方法 |
| frontend/src/pages/catalog/CatalogPage.tsx | ✅ | **旧版**（左侧 Tree + 简单 Search，与"取消左侧导航 + 悬浮筛选 + MECE + 即时查询"完全相反） |
| frontend/src/pages/products/ProductDetailPage.tsx | ✅ | **旧版**（仅 Descriptions + 图片预览 + 旧配置表；无 ProductConfigSelector / ProductPriceDisplay / AddToQuoteModal / ProductDocumentList） |
| frontend/src/pages/quotes/QuoteDetailPage.tsx | ✅ | 仅只读表格；无明细行内编辑、无图片列、无"新增明细"跳转图册按钮 |
| frontend/src/pages/sharing/ShareViewPage.tsx | ✅ | 无品牌头部、无批量分享展示 |

---

## 二、差距清单（按文档章节对齐）

### 差距 G-1：产品字段重构（开发文档 §3.2 / 需求文档 §2.2.2）

| 文档要求 | 现有代码 | 差距 |
|---|---|---|
| `category_l1` 枚举（SEATING/DESKS_WORKSTATIONS/TABLE/STORAGE/ACCESSORIES/EDUCATION） | 旧 `category(FK)` | ❌ 缺字段 |
| `category_l2` 枚举（一级联动） | 无 | ❌ 缺字段 |
| `brand FK→Brand` | 无 Brand 表 | ❌ 缺模型 + 字段 |
| `lead_time` 枚举（WITHIN_45D / 2-4M_VIETNAM / 2-4M_MALAYSIA / 4-6M_EU） | 无 | ❌ 缺字段 |
| `length_mm / width_mm / height_mm` | 无 | ❌ 缺字段 |
| `official_url / model_3d_url / material_album` | 无 | ❌ 缺字段 |
| `pricing_mode` (MATRIX/RULE) + `base_price` | 无 | ❌ 缺字段 |
| 椅子类专属字段（动态表单） | 无 | ❌ 缺前端动态表单组件 |

**影响范围**：模型迁移、序列化器、ProductFormPage、ProductListPage（筛选项）、ProductDetailPage（展示）。

---

### 差距 G-2：产品配置 + 双模式价格引擎（开发文档 §3.2 + §9.5 / 需求文档 §2.2.3 §3）

| 文档要求 | 现有代码 | 差距 |
|---|---|---|
| `ProductConfigDimension` 表（动态选择器数据源、级联） | 仅有旧 `ProductConfig`（attributes JSON） | ❌ 缺新表 |
| `ProductPriceMatrix` 表（模式 A 映射） | 无 | ❌ 缺新表 |
| `ProductPriceRule` 表（模式 B 加价规则） | 无 | ❌ 缺新表 |
| `POST /api/products/{id}/calculate-price/`（响应 < 300ms） | 无 | ❌ 缺端点 + Service |
| `GET /api/products/{id}/config-dimensions/` | 无 | ❌ 缺端点 |

**影响范围**：3 张新表 + 迁移、`products/services.py` 新增 `PriceCalculationService`、URL 路由、序列化器。

---

### 差距 G-3：产品配置 Excel 导入（开发文档 §9.7 / 需求文档 §2.2.4）

| 文档要求 | 现有代码 | 差距 |
|---|---|---|
| `GET /api/products/config-template/` 下载模板 | 无 | ❌ 缺端点 |
| `POST /api/products/{id}/upload-config-excel/`（parse → preview → confirm） | 无 | ❌ 缺端点 |
| 模板包含 dimensions / pricing_mode / matrix 或 rules sheet | 无模板文件 | ❌ 缺资源 |
| 同一产品再次导入"先清空后写入" | 无 | ❌ 缺业务逻辑 |
| 前端 `<ConfigExcelImporter />` 组件 | 无 | ❌ 缺组件 |

**影响范围**：`products/services.py::ConfigExcelService`、模板生成代码、ProductFormPage 增加上传区。

---

### 差距 G-4：产品-文档关联（开发文档 §3.2 / 需求文档 §2.2.1 §2.4）

| 文档要求 | 现有代码 | 差距 |
|---|---|---|
| `ProductDocument` M2M（含 relation_type=DESIGN/TRAINING/CERTIFICATE） | 无 | ❌ 缺新表 |
| `GET/POST/DELETE /api/products/{id}/documents/` | 无 | ❌ 缺端点 |
| 详情页 `<ProductDocumentList />` 分组展示 | 无 | ❌ 缺组件 |

---

### 差距 G-5：品牌字典（开发文档 §3.2 / §4.2.1）

| 文档要求 | 现有代码 | 差距 |
|---|---|---|
| `Brand` 模型（name / is_self_owned / sort_order） | 无 | ❌ 缺模型 |
| `GET/POST/PATCH/DELETE /api/brands/` | 无 | ❌ 缺端点 |
| 前端 `brandService` | 无 | ❌ 缺 service |

---

### 差距 G-6：产品图册搜索体验重构（开发文档 §4.4 / 需求文档 §2.3）

| 文档要求 | 现有代码 | 差距 |
|---|---|---|
| 取消左侧分类树 | `CatalogPage.tsx` 第 31-36 行仍在渲染 `<Tree />` | ❌ 反向实现 |
| 悬浮筛选面板（淘宝式，多选） | 无 | ❌ 缺组件 `<CatalogFilterDrawer />` |
| 即时查询（debounce） | 单次 onSearch | ❌ 体验差 |
| MECE 区间预设（长 / 宽 / 高 / 价格） | 无 | ❌ 缺业务规则 |
| 动态属性聚合（除人工配置外） | 无 | ❌ 缺后端聚合 |
| 多级类别标签（`<CatalogCategoryTabs />`） | 无 | ❌ 缺组件 |
| `GET /api/catalog/filters/` 聚合接口 | 无 | ❌ 缺端点 |
| `GET /api/catalog/`（多条件多选） | 仅支持 single category + q | ❌ 接口不够 |

**影响范围**：`catalog/views.py` + `catalog/serializers.py` + `CatalogPage.tsx` 全面重写。

---

### 差距 G-7：产品详情页电商式选购（开发文档 §9.5 §9.6 / 需求文档 §2.4 §3）

| 文档要求 | 现有代码 | 差距 |
|---|---|---|
| `<ProductConfigSelector />` 动态选择器 + 级联 | 无 | ❌ 缺组件 |
| `<ProductPriceDisplay />` 实时价格 + 配置面包屑 | 无 | ❌ 缺组件 |
| `<AddToQuoteModal />` 加入报价弹窗（选目标报价单 + 数量/折扣 + 选图） | 无 | ❌ 缺组件 |
| `<ProductImagePicker />` 图集选图 | 无 | ❌ 缺组件 |
| `<MediaPreview />` 在线预览（图片/PDF/视频/音频/Office） | 无 | ❌ 缺组件 |

---

### 差距 G-8：报价单明细 CRUD 与一键加入（开发文档 §3.5 §4.7 §9.6）

| 文档要求 | 现有代码 | 差距 |
|---|---|---|
| `QuoteItem.config_attributes` JSON | 无 | ❌ 缺字段 |
| `QuoteItem.image FK→ProductImage` | 无 | ❌ 缺字段 |
| `QuoteItem.image_url` | 无 | ❌ 缺字段 |
| `POST /api/quotes/{id}/items/from-product/` | 无 | ❌ 缺端点 |
| 明细行内编辑数量/折扣/图 | `QuoteDetailPage` 仅只读表格 | ❌ 缺交互 |
| 「新增明细」跳转 `/catalog?quoteId={id}` | 无 | ❌ 缺入口 |
| PDF 模板渲染明细图 + 配置摘要 | 旧 `pdf_template.html` 简单字段 | ⚠️ 需更新 |

---

### 差距 G-9：客户案例（需求文档 §2.5）

| 文档要求 | 现有代码 | 差距 |
|---|---|---|
| 行业枚举 = 办公空间 8 大细分行业 + 其他 | 当前 9 大行业按"客户行业"维度（科技/金融/地产…），不是"办公空间细分" | ⚠️ 枚举值待与客户对齐后调整 |
| 默认按案例名称升序 | `Case.Meta.ordering = ['-created_at']` | ❌ 排序错 |
| 详情页图片平铺 + 懒加载 + WebP | 仅 `<Image.PreviewGroup>` 平铺，无懒加载/WebP | ⚠️ 性能待优化 |
| 行业树筛选控件 | `CaseListPage` 简单 Select | ⚠️ 改为树形 |

---

### 差距 G-10：内部文档体验（需求文档 §2.6 / 开发文档 §11）

| 文档要求 | 现有代码 | 差距 |
|---|---|---|
| 设计资源 / 培训资料 / 资质文件在线预览（图片/PDF/视频/音频/Office） | 仅下载 | ❌ 缺预览 |
| 培训资料富文本上传（图文混排 + 视频 / 音频内嵌） | 无 | ❌ 缺功能 |
| `Document` 模型支持 `resource_type` (RICH_TEXT / FILE / VIDEO / AUDIO) | 无 | ❌ 缺字段 |
| `<RichTextUploader />` 富文本编辑器 | 无 | ❌ 缺组件 |
| `<MediaPreview />` 公共预览组件 | 无 | ❌ 缺组件 |

---

### 差距 G-11：分享功能增强（需求文档 §2.8）

| 文档要求 | 现有代码 | 差距 |
|---|---|---|
| 批量分享（如某行业案例集合） | `content_type` 单对象 | ❌ 缺功能 |
| 分享页品牌展示（Logo / 公司名 / 联系方式） | 无 | ❌ 缺展示 |

---

### 差距 G-12：旧分类体系兼容收尾

需求文档 §5.2 明确剔除"CATEGORY/BRAND 强制分类树"与"图册双维度树形导航"。

| 现状 | 处理方案 |
|---|---|
| `Category` 表存在 + 旧 dimension=TYPE/SPACE/ORIGIN | 保留作为"过渡筛选项字典"，但前端不再以 Tree 暴露；后端做迁移使其 `dimension` 字段不再强制（或忽略） |
| `Product.category(FK)` + `Product.categories(M2M)` | 文档要求"过渡保留"，新代码主用 `category_l1/l2`；保留 FK 直到旧数据无依赖 |

---

## 三、优化总览（一图看全）

```
P0 — 数据模型重构（基础，必须先于 P1/P2）
├── G-1 Product 字段重构（含枚举 / 尺寸 / pricing_mode / base_price）
├── G-2 ProductConfigDimension + Matrix + Rule 三张新表
├── G-4 ProductDocument M2M
├── G-5 Brand 字典
└── G-8 QuoteItem 字段扩展

P1 — 产品图册搜索体验（用户最关注的入口）
├── G-6 catalog/filters/ 聚合 + 多维多选 + MECE 区间
└── 前端 CatalogPage 全面重写：取消 Tree，改 FilterDrawer + CategoryTabs + 即时查询

P2 — 产品详情页电商式选购（核心商业链路）
├── G-2 calculate-price 服务（< 300ms）
├── G-3 配置 Excel 导入（template + parse + preview + confirm）
├── G-4 详情页关联文档分组展示
├── G-7 ProductConfigSelector + PriceDisplay + AddToQuoteModal + ImagePicker + MediaPreview
└── G-8 from-product API + QuoteDetailPage 明细 CRUD + 「新增明细」跳转图册

P3 — 文档模块体验
├── G-10 在线预览（MediaPreview）
└── G-10 培训资料富文本上传 + 视频 / 音频

P4 — 客户案例
└── G-9 行业枚举 + 排序 + 图片懒加载/WebP + 行业树筛选

P5 — 分享功能
├── G-11 批量分享
└── G-11 分享页品牌展示
```

---

## 四、推荐执行策略

> 完整范围共 12 个差距，跨数据模型 + 后端 API + 前端组件三个层级，工作量大。建议**分批迭代**而不是一口气全做。

**推荐分批方案**：

- **第一批（P0+P2 核心链路）**：模型重构 + 双模式算价 + Excel 导入 + 详情页电商化 + 报价单一键加入。这是商业闭环。
- **第二批（P1）**：图册搜索体验全面重写。
- **第三批（P3+P4+P5）**：文档预览 / 案例 / 分享增强（独立模块，影响小）。

也可以选择**只做特定优先级**或**整体一次性做完**。

---

## 五、待用户决策

由于改造范围大、影响面广，正式启动前需要你确认 5 个关键问题。问题清单已生成在：

📄 **[`aidlc-docs/inception/optimization-scope-questions.md`](./optimization-scope-questions.md)**

请打开该文件，按文件内说明用 `[Answer]:` 标签填写答案后告诉我"填好了"，我再继续生成详细执行计划。
