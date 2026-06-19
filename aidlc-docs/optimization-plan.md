# 系统优化方案 — 基于客户反馈与核心思路

> **更新说明（2026-05 补充）**：根据最新一轮客户反馈，对原方案进行了大幅调整：
> - 分类体系重构（OPT-1.1～1.4）整体取消，改用「多维搜索 + 悬浮筛选」模式（详见 OPT-2.1）
> - 文件夹排序需求（OPT-3.1～3.2）整体剔除
> - 产品图册导航（OPT-8.1）取消，改为多级类别展示式搜索（OPT-8.3）
> - 新增产品详情页重构、电商式配置选购、Excel 动态配置等核心需求（详见 P2 章节）

---

## 一、差异分析

### 1. 分类体系：当前 vs 客户需求 ❌【方案取消】

**原差异分析**：当前 TYPE/SPACE/ORIGIN 三维度，客户原需求为「产品类别 + 品牌」二维体系。

**最新客户决策**：
- ❌ **OPT-1.1～1.4 全部取消**：不再做分类维度的强制重构（不再固化为 CATEGORY/BRAND 两棵树）
- ✅ 改为「**多维搜索 + 悬浮筛选**」模式（参考淘宝首页筛选体验）— 见 OPT-2.1
- ✅ 分类信息（品牌、产地、产品一级/二级类别等）作为**搜索筛选项**而非独立的导航树存在

**优化项**：
- ~~[ ] OPT-1.1：将分类维度从 TYPE/SPACE/ORIGIN 改为 CATEGORY（产品类别）/ BRAND（品牌）~~ **【取消】**
- ~~[ ] OPT-1.2：预置客户提供的产品类别二级分类数据（6大一级+详细二级）~~ **【取消】**
- ~~[ ] OPT-1.3：预置品牌维度数据（ZIKOO 自有品牌 + 国际品牌）~~ **【取消】**
- ~~[ ] OPT-1.4：产品图册左侧导航改为双维度树形筛选（品牌树 + 类别树）~~ **【取消】**

> 注：客户提供的产品类别（6大一级+二级）和品牌列表数据**仍需要预置**，但作为**筛选项数据源**使用，不再作为强制的分类树结构。

---

### 2. 产品图册搜索体验重构 ⭐【新核心需求】

**当前系统**：产品图册左侧分类树 + 顶部搜索框（仅 name/code）
**客户最新需求**：
- ❌ **取消左侧分类导航**
- ✅ 顶部增加**多维搜索条件**，筛选条件做成**悬浮面板**，体验类似**淘宝首页筛选**
- ✅ **即时查询**：前端实时刷新查询结果（输入/勾选即查，无需点确认）
- ✅ **连续型变量**（如尺寸、价格区间）提前配置好 **MECE** 范围（互斥且穷尽的区间分段）
- ✅ **筛选项动态生成**：除需要人工配置的字段（如品牌、产地、一级类别等）外，其他属性筛选项基于产品库实际数据**动态生成**
- ✅ 搜索框独立检索名称、产品编号、材质、尺寸描述等属性细节

**优化项（原项重写）**：
- [ ] **OPT-2.1（新）：产品图册搜索体验重构**
  - 取消左侧分类树导航
  - 顶部搜索栏 + 悬浮筛选面板（淘宝式）
  - 筛选条件即时生效（debounce 实时查询）
  - 连续型变量预配置 MECE 区间（如长度：≤600 / 600-900 / 900-1200 / 1200-1800 / >1800 mm）
  - 离散型筛选项除人工配置字段外动态生成（聚合自 config_attributes / 规格字段）
  - 多选筛选 + 全字段关键词搜索

---

### 3. 文件夹排序 ❌【需求剔除】

**最新客户决策**：文件夹排序需求**整体剔除**，不再开发。

**优化项**：
- ~~[ ] OPT-3.1：添加文件夹批量排序 API~~ **【取消】**
- ~~[ ] OPT-3.2：前端文件夹树支持拖拽排序~~ **【取消】**

---

### 4. 产品详情页重构 ⭐【新核心需求】

**当前系统**：产品详情页有图片展示、配置列表、文档快捷链接（通用跳转）
**客户最新需求**：
- ✅ **产品详情页字段重构**：完全参考《产品库字段描述.xlsx》进行字段调整
- ✅ **产品-文档关联**：详情页展示与该产品相关的设计资源/培训资料/资质文件（保留）
- ✅ 详情页改为更集中的预览模式（大图 + 信息 + 配置 + 关联文档 一屏展示）

**字段重构清单（参考产品库字段描述.xlsx）**：
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| 产品名称 | 文本 | ✅ | |
| 产品编号 | 文本 | ✅ | |
| 产品分类（一级） | 单选 | ✅ | 6 大一级：Seating / Desks+Workstations / Table / Storage / Accessories / Education |
| 产品分类（二级） | 单选 | ✅ | 级联：选一级后动态联动二级 |
| 品牌 | 单选 | ✅ | ZIKOO / Steelcase / Vitra / … |
| 产地 | 单选 | ✅ | 进口 / 国产 |
| 货期 | 单选 | ✅ | 45 天内 / 2-4月【越南】/ 2-4月【马来西亚】/ 4-6月【荷兰/意大利/德国】 |
| 产品描述 | 文本 | ✅ | |
| 指导价 | 数字 | ✅ | 见 OPT-4.4 双模式 |
| 产品图片 | 图片 | ✅ | 多图 + 首图标记，三视图 |
| 长 / 宽 / 高 | 数字 | | mm |
| 官网链接 | 链接 | | |
| 可选材质图册 | 图片 | | |
| 3D 模型 | 链接 | | |
| **椅子类专属字段（动态表单）** | | | 选了二级=椅子类后展开 |
| 框架颜色（背框） | 单选 | | P1 / P2 / P3 |
| 框架颜色（座框） | 单选 | | P1 / P2 / P3 |
| 坐垫材质 | 单选 | | 网 / 布 / 皮 |
| 靠背材质 | 单选 | | 网（AIR / 3D knit / intermix）/ 布（P1/P2/P3）/ 皮（P1/P2/P3）|
| 靠背材质系列 | 单选（级联） | | 跟随靠背材质级联 |
| 扶手 | 单选 | | 2D / 3D / 4D |
| 底座 | 单选 | | 标准 / 高配 / 低配 |
| 腰撑 | 单选 | | 有 / 无 |
| 滚轮 | 单选 | | 地板轮 / 地毯轮 |
| 头枕 | 单选 | | 有 / 无 |
| 脚踏 | 单选 | | 有 / 无 |

**优化项**：
- [ ] **OPT-4.1：产品-文档关联模型**（保留）— 新增 ProductDocument M2M
- [ ] **OPT-4.2：详情页展示关联的设计资源/培训资料/资质文件**（保留）
- [ ] **OPT-4.3：详情页集中预览模式**（保留）
- [ ] **OPT-4.4（新）：产品字段按《产品库字段描述.xlsx》重构**
  - 一级/二级分类级联选择
  - 二级分类决定动态表单（不同品类显示不同的专属字段集）
  - 椅子类等品类的专属属性维护

---

### 5. 产品详情页电商式配置选购 ⭐【新核心需求】

**客户需求**：产品详情页参考**电商购物模式**：
- ✅ 用户在详情页**动态选择配置项**（材质 / 框架颜色 / 扶手 / 底座 / 滚轮 / 头枕 / 脚踏 等）
- ✅ 选择过程中**实时生成指导价 + 配置明细**
- ✅ **一键添加到指定报价单**（选择目标报价单后追加到明细）
- ✅ 添加报价单明细时，支持从**产品图册的图集**中选择某张图片作为该报价明细的展示图
- ✅ 报价单明细完整记录：**配置组合 + 选定图片 + 单价 + 数量等**
- ✅ 报价单明细支持 **CRUD**（增/删/改/查）
- ✅ 「**新增明细**」入口直接跳转到**产品图册**进行选品

**指导价计算双模式**（参考 xlsx 第 9 项 A/B 方案）：
- **模式 A：配置-价格映射表**
  - 每个产品维护独立的「配置组合 → 价格」映射表
  - 价格直接查表，不存在的组合视为无效配置（不允许选择）
  - 适合规格组合有限、价格不规律的产品
- **模式 B：基准价 + 加价规则**
  - 系统预设默认指导价
  - 每个配置要素（材质/功能/配件）有独立加价规则
  - 用户更改任一要素 → 实时重算最终价
  - 适合规格组合多、价格可累加的产品

**优化项**：
- [ ] **OPT-5.1（新）：产品配置选择器组件**
  - 详情页内嵌式配置选择 UI
  - 实时显示当前组合的配置明细 + 指导价
  - 配置变更触发即时价格重算
- [ ] **OPT-5.2（新）：产品配置-价格双模式后端模型**
  - 模式 A：ProductPriceMatrix 表（产品ID + 配置组合 hash + 价格）
  - 模式 B：ProductPriceRule 表（产品ID + 配置维度 + 加价值）
  - 产品级开关字段决定使用哪种模式
- [ ] **OPT-5.3（新）：一键加入报价单**
  - 详情页「加入报价单」按钮，弹窗选择目标报价单（或新建）
  - 加入时弹出图片选择器（取自产品图册的图集）
  - 报价明细写入：产品+配置JSON+单价+图片URL
- [ ] **OPT-5.4（新）：报价单明细 CRUD 完善**
  - 明细列表显示：图片 + 产品名 + 配置摘要 + 单价 + 数量 + 小计
  - 支持编辑/删除/调整数量
  - 「新增明细」按钮跳转到产品图册（带回调）

---

### 6. 产品配置 Excel 动态导入 ⭐【新核心需求】

**客户需求**：
- ✅ 产品详情页支持上传**该产品的配置 Excel**
- ✅ 系统**动态解析并展示** Excel 中描述的配置维度
- ✅ 用户基于上传的配置数据**动态选择**生成指导价
- ✅ 平台需要**提供 Excel 模板**（字段固定 + 维度可扩展）

**典型场景**：椅子类产品的配置组合非常多（材质×颜色×扶手×底座×滚轮 …），手工录入工作量大；甲方提供 Excel 后系统自动解析为配置选择器。

**优化项**：
- [ ] **OPT-6.1（新）：产品配置 Excel 模板设计**
  - 模板包含：配置维度定义 sheet + 配置-价格映射 sheet
  - 兼容 OPT-5.2 的双模式
- [ ] **OPT-6.2（新）：Excel 解析服务**
  - 后端服务解析上传的配置 Excel
  - 写入 ProductPriceMatrix 或 ProductPriceRule
  - 支持预览 → 确认 → 导入流程
- [ ] **OPT-6.3（新）：动态配置选择器**
  - 详情页根据产品已导入的配置数据动态渲染选择器
  - 与 OPT-5.1 联动

---

### 7. 客户案例 — 行业树筛选

**当前系统**：9 大行业分类（科技/互联网、金融/保险/财税…其他）
**客户最新需求**：
- ✅ 客户案例增加**行业树筛选**
- ✅ 分类为**办公空间 8 大细分行业 + 其他**
- ✅ 案例**按名称排序**

**优化项**：
- [ ] **OPT-7.1（新）：客户案例行业树筛选**
  - 列表页左侧/顶部增加行业树筛选控件
  - 8 大细分行业 + 其他（与客户确认的列表对齐）
  - 案例默认按 name 升序排列

---

### 8. 文档模块体验

**客户反馈与最新需求**：
- ✅ **设计资源、培训资料、资质文件支持在线预览**
- ✅ **培训资料支持富文本上传**（图文混排）
- ✅ **培训资料支持视频、音频等格式**
- ✅ **案例图片继续平铺加载，不需要分页**，但**加载效率需优化**（懒加载 / 缩略图 / 渐进加载）
- ✅ 文件夹删除（已支持）

**优化项**：
- [ ] **OPT-8.1：在线预览能力增强**
  - 图片：模态框预览 + 缩略图列表
  - PDF：浏览器内嵌查看器（pdf.js）
  - 视频：HTML5 video 播放器（mp4 / webm）
  - 音频：HTML5 audio 播放器（mp3 / wav / m4a）
  - Office 文档（doc/ppt/xlsx）：调用预览服务（如 Office Online Viewer 或自建）
- [ ] **OPT-8.2：培训资料富文本上传**
  - 富文本编辑器（图文混排，支持嵌入图片/视频/音频）
  - 资源类型扩展：富文本 / 视频 / 音频 / 文档
- [ ] **OPT-8.3：案例图片加载效率优化**
  - 平铺加载（不分页），但启用：
    - 图片懒加载（IntersectionObserver）
    - 缩略图列表 + 点击查看大图
    - 渐进式加载（先模糊占位，再清晰图）
    - 服务端图片压缩 + WebP 输出

---

### 9. 产品图册搜索 — 多级类别展示

**客户最新需求**（替代原 OPT-8.1 双维度树）：
- ✅ 图册搜索**参考淘宝首页**进行**多级类别展示**
- ✅ 与 OPT-2.1 的悬浮筛选面板联动：搜索结果区上方/侧边显示已激活的多级类别面包屑

**优化项**：
- ~~[ ] OPT-8.1：产品图册左侧改为双维度导航（品牌树 + 类别树）~~ **【取消】**
- [ ] **OPT-9.1（新，原 OPT-8.3）：图册搜索多级类别展示**
  - 顶部搜索栏 → 多级类别快捷标签（淘宝式）
  - 选中一级类别后展开二级类别
  - 已选条件以面包屑/标签形式可移除
  - 与 OPT-2.1 悬浮筛选共用筛选状态

---

### 10. 核心思路对齐："内部使用，按需外放"

（保留原内容，无变更）

**当前系统对齐情况**：
- ✅ 产品管理：纯内部，需登录，管理员权限控制
- ✅ 分享功能：支持按需创建分享链接（产品/案例/报价/图册）
- ✅ 报价方案：内部创建，可通过分享链接对外
- ⚠️ 产品图册：当前只有内部版，缺少"对外版"的概念区分
- ⚠️ 客户案例：客户说是"未来对外分享的重点"，当前分享功能已支持但可强化

**优化项**：
- [ ] OPT-10.1（原 OPT-9.1）：分享功能增加"批量分享"能力（如分享整个行业的案例集合）
- [ ] OPT-10.2（原 OPT-9.2）：分享页面增加公司品牌展示（Logo、公司名称、联系方式）

---

## 二、优化方案汇总（按优先级排序，已根据最新需求重排）

### P0 — 产品详情页重构（基础数据结构）
| # | 优化项 | 影响范围 | 说明 |
|---|--------|----------|------|
| OPT-4.4 | 产品字段按 xlsx 重构 | 后端模型+迁移+前端表单 | 一级/二级级联+品类动态表单 |
| OPT-4.1 | 产品-文档关联模型 | 后端模型 | 新增 ProductDocument M2M |
| OPT-5.2 | 产品配置-价格双模式后端 | 后端模型 | Matrix / Rule 双表 |
| OPT-6.1 | 产品配置 Excel 模板设计 | 文档+模板文件 | 提供给客户填写的标准模板 |

### P1 — 产品图册搜索重构（用户体验核心）
| # | 优化项 | 影响范围 | 说明 |
|---|--------|----------|------|
| OPT-2.1 | 图册搜索体验重构 | 前端 CatalogPage + 后端 API | 多维搜索+悬浮筛选+即时查询 |
| OPT-9.1 | 多级类别展示 | 前端 | 淘宝式多级类别标签 |
| 数据预置 | 品牌/产品类别/产地/货期等下拉数据 | 数据迁移 | 客户提供的列表沿用 |

### P2 — 产品详情页电商式选购
| # | 优化项 | 影响范围 | 说明 |
|---|--------|----------|------|
| OPT-5.1 | 产品配置选择器组件 | 前端 | 实时配置 + 实时价格 |
| OPT-5.3 | 一键加入报价单 | 前端 + 后端 | 含图集选图 |
| OPT-5.4 | 报价单明细 CRUD 完善 | 前端 + 后端 | 跳转产品图册新增 |
| OPT-6.2 | Excel 解析服务 | 后端 | preview → confirm |
| OPT-6.3 | 动态配置选择器 | 前端 | 跟随导入数据渲染 |
| OPT-4.2 | 详情页展示关联文档 | 前端 | 设计资源/培训/资质 |
| OPT-4.3 | 详情页集中预览模式 | 前端 | 大图+信息+配置+文档 |

### P3 — 文档模块体验
| # | 优化项 | 影响范围 | 说明 |
|---|--------|----------|------|
| OPT-8.1 | 在线预览能力增强 | 前端 | 图片/PDF/视频/音频/Office |
| OPT-8.2 | 培训资料富文本上传 | 前端 + 后端 | 富文本+多媒体 |
| OPT-8.3 | 案例图片加载效率优化 | 前端 + 后端 | 懒加载/缩略图/WebP |

### P4 — 客户案例
| # | 优化项 | 影响范围 | 说明 |
|---|--------|----------|------|
| OPT-7.1 | 客户案例行业树筛选 | 前端 + 后端 | 8大+其他，按名称排序 |

### P5 — 分享功能增强
| # | 优化项 | 影响范围 | 说明 |
|---|--------|----------|------|
| OPT-10.1 | 批量分享 | 后端+前端 | 分享整个行业案例集合 |
| OPT-10.2 | 分享页品牌展示 | 前端 ShareViewPage | Logo/公司名/联系方式 |

---

## 三、已取消 / 已剔除项（不再开发）

| 编号 | 原内容 | 状态 |
|---|---|---|
| OPT-1.1 | 分类维度改为 CATEGORY/BRAND | ❌ 取消 |
| OPT-1.2 | 预置产品类别二级分类（树形） | ❌ 取消（数据保留作为筛选项） |
| OPT-1.3 | 预置品牌维度（树形） | ❌ 取消（数据保留作为筛选项） |
| OPT-1.4 | 图册双维度树形导航 | ❌ 取消 |
| OPT-3.1 | 文件夹排序 API | ❌ 取消 |
| OPT-3.2 | 文件夹拖拽排序 | ❌ 取消 |
| 原 OPT-8.1 | 图册左侧双维度导航 | ❌ 取消（由 OPT-2.1 替代） |

---

## 四、不需要修改的部分（已对齐）

- ✅ 客户案例分类基础数据（8大+其他，已一致；本次新增的是「树形筛选交互」）
- ✅ 文件夹删除功能（后端已支持）
- ✅ 文档分页加载基础能力（保留，但案例图片不分页）
- ✅ 产品全字段搜索基础能力（图册搜索另做，参考 OPT-2.1）
- ✅ 分享链接核心功能（密码/过期/次数限制/访问记录）
- ✅ 报价方案基础流程（CRUD/明细/PDF/复制/状态流转；明细体验由 OPT-5.x 增强）
- ✅ 用户认证与权限体系
- ✅ "内部使用，按需外放"的核心架构

---

## 五、建议开发顺序

1. **P0 产品详情页字段重构** → 字段是后续所有功能的基础（含 Excel 模板设计）
2. **P1 产品图册搜索重构** → 客户最关注的入口体验
3. **P2 产品详情页电商式选购** → 与报价单打通的核心商业流程
4. **P3 文档模块体验** → 在线预览与富文本上传
5. **P4 客户案例行业树筛选** → 范围小，独立完成
6. **P5 分享功能增强** → 锦上添花

---

## 六、变更记录

| 日期 | 变更内容 |
|---|---|
| 2026-05 | 取消 OPT-1.1～1.4（分类体系重构）；取消 OPT-3.1～3.2（文件夹排序）；取消原 OPT-8.1（图册左侧导航） |
| 2026-05 | 重写 OPT-2.1（图册搜索改为多维+悬浮筛选+即时查询+MECE+动态生成） |
| 2026-05 | 新增 OPT-4.4（产品字段按 xlsx 重构）、OPT-5.x（电商式选购）、OPT-6.x（Excel 配置导入）、OPT-7.1（案例行业树）、OPT-8.x（在线预览/富文本/图片优化）、OPT-9.1（多级类别展示） |


---

## 七、端到端流程图与新增 API 清单（OPT-4 / OPT-5 / OPT-6 落地细节）

> 本章作为 P0~P2 的开发蓝图,聚焦"产品配置 → 实时算价 → 一键加入指定报价单"这一核心商业链路。

### 7.1 端到端业务流程

```
[管理员侧]                                 [使用侧 - 销售/设计]
                                          
1. 录入产品(基础字段,按 xlsx 重构)         5. 打开产品详情页
   → 一级/二级类别级联                       → 看到大图 + 基础信息 + 配置选择器 + 关联文档
   → 品类驱动动态表单(椅子类等)
                                           6. 在配置选择器中按维度勾选
2. 上传产品配置 Excel                         (材质/颜色/扶手/底座/滚轮 ...)
   → 平台提供标准模板                         → 每次勾选触发 calculate-price API
   → 后端解析 → preview → confirm              → 实时显示配置明细 + 指导价
   → 写入 ProductPriceMatrix(模式 A)
       或 ProductPriceRule(模式 B)        7. 点击「加入报价单」
                                              → 弹窗选择目标报价单(或新建)
3. 上传产品图册图集                           → 弹窗从该产品图集中选择展示图
   (沿用现有 upload_images 接口)              → 提交 → 报价单追加一条明细
                                              → 报价单总价自动重算
4. 关联文档资源
   (设计资源/培训资料/资质文件)             8. 在报价单详情页继续 CRUD 明细
   → ProductDocument M2M                     → 编辑数量/折扣/明细图
                                              → 「新增明细」按钮跳回产品图册(带 quoteId)
```

### 7.2 数据模型新增

#### 7.2.1 ProductDocument(产品-文档关联)

```
ProductDocument
├── id                BIGINT PK
├── product           FK → Product
├── document          FK → Document
├── relation_type     VARCHAR(15)  DESIGN/TRAINING/CERTIFICATE(冗余,加速筛选)
├── sort_order        INT
└── created_at        DATETIME
unique_together: (product, document)
```

#### 7.2.2 ProductConfigDimension(配置维度,动态选择器数据源)

```
ProductConfigDimension
├── id                BIGINT PK
├── product           FK → Product
├── dimension_key     VARCHAR(100)   维度键,如 "frame_color_back"
├── dimension_label   VARCHAR(100)   维度展示名,如 "框架颜色(背框)"
├── options           JSON           [{"key":"P1","label":"P1"}, ...]
├── parent_dimension  VARCHAR(100)   级联父维度 key(可空)
├── is_required       BOOLEAN        是否必选
├── sort_order        INT
└── created_at        DATETIME
unique_together: (product, dimension_key)
```

> 说明:解决 xlsx 中"靠背材质 → 靠背材质系列"这类级联关系。

#### 7.2.3 ProductPriceMatrix(模式 A:配置-价格映射表)

```
ProductPriceMatrix
├── id                BIGINT PK
├── product           FK → Product
├── config_signature  VARCHAR(255)   配置组合的稳定哈希
├── config_attributes JSON           {"frame_color_back":"P1","cushion_material":"网", ...}
├── price             DECIMAL(10,2)
└── created_at        DATETIME
unique_together: (product, config_signature)
index: (product, config_signature)
```

#### 7.2.4 ProductPriceRule(模式 B:基准价 + 加价规则)

```
ProductPriceRule
├── id                BIGINT PK
├── product           FK → Product
├── dimension_key     VARCHAR(100)
├── option_key        VARCHAR(100)
├── price_delta       DECIMAL(10,2)  正负皆可
└── sort_order        INT
unique_together: (product, dimension_key, option_key)
```

> Product 模型增加字段:
> - `pricing_mode VARCHAR(10) CHOICES=('MATRIX','RULE')` 默认 'MATRIX'
> - `base_price DECIMAL(10,2)` 仅模式 B 使用

#### 7.2.5 QuoteItem 字段扩展

```
QuoteItem(在现有基础上增加)
├── config_attributes JSON           完整配置 {"维度":"选项",...}
├── image_url         VARCHAR(500)   报价明细展示图(可空)
├── image_id          FK → ProductImage(可空)  来自产品图集
└── (其余字段保持不变)
```

#### 7.2.6 Product 字段重构(对齐 xlsx)

新增 / 调整:
- `category_l1 VARCHAR(20)` 一级类别枚举(SEATING / DESKS_WORKSTATIONS / TABLE / STORAGE / ACCESSORIES / EDUCATION)
- `category_l2 VARCHAR(40)` 二级类别(由一级联动)
- `brand_id FK → Brand`
- `lead_time VARCHAR(40)` 货期(枚举:within_45d / 2-4m_vietnam / 2-4m_malaysia / 4-6m_eu)
- `length_mm INT / width_mm INT / height_mm INT`
- `official_url VARCHAR(500)`
- `material_album JSON` 可选材质图册(图片地址数组)
- `model_3d_url VARCHAR(500)`

> 老的 `category(FK)` 字段保留过渡期兼容,后续迁移完成可去除。

#### 7.2.7 Brand(品牌字典)

```
Brand
├── id                BIGINT PK
├── name              VARCHAR(100)   ZIKOO / Steelcase / Vitra / ...
├── is_self_owned     BOOLEAN
├── sort_order        INT
└── created_at        DATETIME
```

### 7.3 新增 / 变更 API 清单

| 方法 | 路径 | 说明 | 权限 | 关联优化项 |
|---|---|---|---|---|
| GET | /api/products/{id}/config-dimensions/ | 获取该产品的所有配置维度及选项(供动态选择器渲染) | 已登录 | OPT-5.1 / OPT-6.3 |
| POST | /api/products/{id}/calculate-price/ | 入参 `{selections: {key:value,...}}`,返回 `{price, breakdown, valid, missing_dimensions}` | 已登录 | OPT-5.1 |
| POST | /api/products/{id}/upload-config-excel/ | 上传产品配置 Excel,流程:parse → preview → confirm(query=`?confirm=true`) | 管理员 | OPT-6.2 |
| GET | /api/products/config-template/ | 下载产品配置 Excel 标准模板 | 管理员 | OPT-6.1 |
| GET | /api/products/{id}/documents/ | 获取产品关联的文档(可按 relation_type 筛选) | 已登录 | OPT-4.2 |
| POST | /api/products/{id}/documents/ | 关联文档 `{document_id, relation_type}` | 管理员 | OPT-4.1 |
| DELETE | /api/products/{id}/documents/{doc_id}/ | 解除关联 | 管理员 | OPT-4.1 |
| POST | /api/quotes/{quote_id}/items/from-product/ | 一键加入报价单,入参 `{product_id, selections, image_id?, quantity?, discount?}`,后端自动算价 + 写明细 + 重算总价 | 已登录 | OPT-5.3 |
| GET | /api/brands/ | 品牌列表 | 已登录 | OPT-4.4 |
| POST/PATCH/DELETE | /api/brands/ | 品牌 CRUD | 管理员 | OPT-4.4 |
| GET | /api/products/category-options/ | 一级 + 二级类别枚举(用于级联下拉与图册筛选) | 已登录 | OPT-4.4 / OPT-2.1 |
| GET | /api/catalog/filters/ | 图册筛选项聚合(品牌/一级二级类别/产地/货期/连续型 MECE 区间/动态属性聚合) | 已登录 | OPT-2.1 / OPT-9.1 |
| GET | /api/catalog/search/ | 图册搜索升级,支持多条件 + 多选 + 关键词 + MECE 区间筛选 | 已登录 | OPT-2.1 / OPT-9.1 |

### 7.4 价格计算服务(后端核心算法)

**`POST /api/products/{id}/calculate-price/`** 伪代码:

```
def calculate_price(product, selections: dict) -> dict:
    # 1. 校验维度齐全
    required = ProductConfigDimension.objects.filter(product=product, is_required=True)
    missing = [d.dimension_key for d in required if d.dimension_key not in selections]
    if missing:
        return {valid: False, missing_dimensions: missing, price: None}

    # 2. 校验级联约束
    for dim in ProductConfigDimension.objects.filter(product=product):
        if dim.parent_dimension and selections.get(dim.parent_dimension):
            # 校验当前维度的可选项必须属于父选项的子集
            ...

    # 3. 模式 A:查映射表
    if product.pricing_mode == 'MATRIX':
        sig = build_signature(selections)   # 稳定哈希(按 key 排序)
        row = ProductPriceMatrix.objects.filter(
            product=product, config_signature=sig).first()
        if not row:
            return {valid: False, reason: '该组合无对应价格', price: None}
        return {valid: True, price: row.price, breakdown: selections}

    # 4. 模式 B:基准价 + 加价
    price = product.base_price
    breakdown = {'base_price': product.base_price, 'deltas': []}
    for k, v in selections.items():
        rule = ProductPriceRule.objects.filter(
            product=product, dimension_key=k, option_key=v).first()
        if rule:
            price += rule.price_delta
            breakdown['deltas'].append({k: v, 'delta': rule.price_delta})
    return {valid: True, price: price, breakdown: breakdown}
```

### 7.5 一键加入报价单服务

**`POST /api/quotes/{quote_id}/items/from-product/`** 伪代码:

```
@transaction.atomic
def add_item_from_product(quote, product, selections, image_id, quantity, discount):
    # 1. 复用价格计算
    result = calculate_price(product, selections)
    if not result['valid']:
        raise ValidationError(result)

    # 2. 选定明细图
    image_url = ''
    if image_id:
        img = ProductImage.objects.get(pk=image_id, product=product)
        image_url = img.image_path

    # 3. 写入明细
    item = QuoteItem.objects.create(
        quote=quote,
        product=product,
        product_name=product.name,
        config_name=summarize_selections(selections),  # 配置摘要文本
        config_attributes=selections,
        unit_price=result['price'],
        quantity=quantity,
        discount=discount,
        image_id=image_id,
        image_url=image_url,
        sort_order=quote.items.count(),
    )

    # 4. 触发总价重算
    quote.recalculate_total()
    return item
```

### 7.6 前端组件清单

| 组件 | 位置 | 说明 |
|---|---|---|
| `<ProductConfigSelector />` | products/ProductDetailPage | 动态渲染配置维度选择器,支持级联,debounce 触发价格计算 |
| `<ProductPriceDisplay />` | products/ProductDetailPage | 实时显示价格 + 配置明细面包屑 |
| `<AddToQuoteModal />` | products/ProductDetailPage | 弹窗:选目标报价单(列表/新建)+ 选明细图(图集网格)+ 数量/折扣 |
| `<ProductImagePicker />` | 复用组件 | 从产品图集中选图 |
| `<QuoteItemEditor />` | quotes/QuoteDetailPage | 报价明细 CRUD UI(行内编辑/弹窗编辑) |
| `<CatalogFilterDrawer />` | catalog/CatalogPage | 悬浮筛选面板(淘宝式),含 MECE 区间滑块 + 动态聚合 |
| `<ConfigExcelImporter />` | products/ProductFormPage | 上传配置 Excel + preview + confirm |

### 7.7 配置 Excel 模板结构(草案,OPT-6.1)

**Sheet 1: dimensions(配置维度定义)**

| dimension_key | dimension_label | options(逗号分隔) | parent_dimension | is_required | sort_order |
|---|---|---|---|---|---|
| frame_color_back | 框架颜色(背框) | P1,P2,P3 | | TRUE | 1 |
| backrest_material | 靠背材质 | 网,布,皮 | | TRUE | 2 |
| backrest_series | 靠背材质系列 | AIR,3D knit,intermix | backrest_material=网 | FALSE | 3 |

**Sheet 2: pricing_mode**

| mode | base_price |
|---|---|
| MATRIX 或 RULE | (仅 RULE 模式填写基准价) |

**Sheet 3a: matrix(模式 A 用)**
- 列头 = 各维度 dimension_key + price
- 每一行 = 一个具体配置组合 → 价格

**Sheet 3b: rules(模式 B 用)**

| dimension_key | option_key | price_delta |
|---|---|---|
| frame_color_back | P1 | 0 |
| frame_color_back | P2 | 50 |
| backrest_material | 皮 | 800 |

### 7.8 验收标准(核心链路)

- ✅ 管理员上传配置 Excel 后,产品详情页能动态渲染配置选择器
- ✅ 用户每次更改配置,价格在 300ms 内更新
- ✅ 模式 A 下选到无对应映射的组合时,UI 友好提示"此组合无报价"且禁用「加入报价单」按钮
- ✅ 模式 B 下基准价 + 各维度 delta 累加正确
- ✅ 「加入报价单」可选择已存在报价单或快速新建
- ✅ 加入时可从产品图集中选定一张图作为明细展示图
- ✅ 报价单明细落库后,Quote.total_amount 自动重算
- ✅ 报价单详情页可对该明细 编辑数量/折扣/图片/删除
- ✅ 报价单详情页「新增明细」按钮跳转 `/catalog?quoteId={id}`,在图册中选品并完成上述流程
