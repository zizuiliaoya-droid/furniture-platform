# 业务规则 — Unit 1 后端

## 1. 认证与权限规则

### BR-AUTH-01: Token 认证
- 登录成功后生成 DRF Token，返回 {token, user}
- Token 存储在数据库，一个用户同时只有一个有效 Token
- 登出时删除 Token

### BR-AUTH-02: 角色权限
- ADMIN：全部 CRUD 权限 + 用户管理
- STAFF：查看权限 + 创建报价单/分享链接
- 权限通过 IsAdminRole 自定义权限类控制
- 员工不能：删除任何数据、管理用户、管理分类、上传产品图片、导入产品

### BR-AUTH-03: 用户状态
- is_active=False 的用户无法登录
- 管理员可切换用户状态
- 管理员可重置其他用户密码

### BR-AUTH-04: 初始管理员
- 系统启动时通过 create_admin.py 脚本创建
- 用户名和密码来自环境变量 ADMIN_USERNAME / ADMIN_PASSWORD
- 如果用户名已存在则跳过创建

---

## 2. 产品管理规则

### BR-PROD-01: 产品软删除
- 删除产品时设置 is_active=False，不物理删除
- 软删除的产品对员工不可见
- 管理员可在列表中通过筛选查看已删除/下架的产品
- 报价单中的 QuoteItem.product 通过 SET_NULL 处理，product_name 快照保留

### BR-PROD-02: 产品编号唯一性
- code 字段全局唯一（UNIQUE 约束）
- code 可为空（允许不填编号）
- Excel 导入时检查编号重复

### BR-PROD-03: 分类树规则
- 三个独立维度：TYPE（类型）、SPACE（空间）、ORIGIN（产地）
- 同一父分类下同维度不允许重名：UNIQUE(parent, name, dimension)
- 删除分类前检查：有子分类或关联产品时禁止删除
- 拖拽排序通过批量更新 sort_order 实现

### BR-PROD-04: 产品图片规则
- 单张图片最大 10MB
- 上传后自动生成缩略图：small(150×150), medium(400×400)
- 每个产品只能有一张封面图（设置新封面时取消旧封面）
- 图片排序通过 sort_order 字段控制

### BR-PROD-05: 产品配置规则
- 每个产品可有多个配置
- attributes 为 JSON 格式，键值对自由定义
- guide_price 为指导价格，可为空

### BR-PROD-06: Excel 批量导入规则
- 仅支持 .xlsx 格式
- 模板字段：名称（必填）、编号（可选）、产地（必填，IMPORT/DOMESTIC/CUSTOM）、描述、最低售价、分类名称
- 导入前预览：显示成功/失败条数和失败原因
- 编号重复的行标记为失败
- 分类名称不存在的行标记为失败

### BR-PROD-07: 产品搜索规则
- 搜索关键词同时匹配：name, code, description, configs__config_name, configs__attributes
- 使用 OR 关系组合
- 员工只能搜索 is_active=True 的产品

---

## 3. 报价方案规则

### BR-QUOTE-01: 金额计算
- QuoteItem.subtotal = unit_price × quantity × (1 - discount / 100)
- Quote.total_amount = SUM(所有 QuoteItem.subtotal)
- 在 QuoteItem.save() 中自动计算 subtotal
- 增删改明细后调用 Quote.recalculate_total()

### BR-QUOTE-02: 状态流转（严格单向）
```
DRAFT ──► SENT ──► CONFIRMED
  │         │          │
  └─────────┴──────────┴──► CANCELLED
```
- 允许的转换：DRAFT→SENT, SENT→CONFIRMED, 任意→CANCELLED
- 不允许回退：SENT 不能回到 DRAFT，CONFIRMED 不能回退
- CANCELLED 是终态，不可再变更

### BR-QUOTE-03: 报价复制
- 复制时创建新报价单，标题加"(副本)"后缀
- 复制所有 QuoteItem，product 引用保持
- 新报价单状态为 DRAFT
- created_by 为执行复制的用户

### BR-QUOTE-04: PDF 导出
- 使用 WeasyPrint 生成
- 包含：标题、客户名称、明细表格、总金额、备注、条款
- 返回 application/pdf Content-Type

---

## 4. 分享功能规则

### BR-SHARE-01: 分享链接创建
- token 使用 UUID4 生成，64 字符
- content_type: PRODUCT/CASE/QUOTE/CATALOG
- CATALOG 类型 object_id 为空（分享整个图册）
- 密码使用 Django make_password/check_password 哈希

### BR-SHARE-02: 分享访问验证流程
1. 检查 is_active=True
2. 检查 expires_at（未过期或为 NULL）
3. 检查 access_count < max_access_count（或 max_access_count 为 NULL）
4. 如有密码，验证密码
5. 验证通过后：access_count += 1，记录 ShareAccessLog

### BR-SHARE-03: 点击追踪
- 前端在分享页面中，用户点击产品或报价项时发送追踪请求
- 记录 event_type（PRODUCT_CLICK/QUOTE_ITEM_CLICK）、object_id、object_name
- 统计接口返回各对象的点击次数

---

## 5. 文件存储规则

### BR-FILE-01: 文件路径格式
- `{subdirectory}/{YYYYMMDD}/{uuid}_{filename}`
- subdirectory: products/cases/documents
- uuid 防止文件名冲突

### BR-FILE-02: 缩略图生成
- 使用 Pillow 库
- small: 150×150（等比缩放，居中裁剪）
- medium: 400×400（等比缩放，居中裁剪）
- 缩略图路径：原路径加 _small / _medium 后缀

### BR-FILE-03: 文件大小限制
- 图片（产品/案例）：最大 10MB
- 文档：最大 50MB
- 在 View 层验证文件大小

---

## 6. 仪表盘规则

### BR-DASH-01: 统计数据
- 全量统计：产品总数（is_active=True）、案例总数、报价单总数、文档总数
- 本月新增：本月新增产品数、案例数、报价单数
- 最近 30 天每日统计：每天的新增产品数、案例数、报价单数（用于前端图表）
- 最近活动：最近 10 条报价单（按 updated_at 排序）

---

## 7. 全局搜索规则

### BR-SEARCH-01: 跨模块搜索
- 搜索范围：products(name,code), cases(title), documents(name), quotes(title,customer_name)
- 每个模块返回最多 5 条匹配结果
- 返回格式：{ products: [...], cases: [...], documents: [...], quotes: [...] }
- 员工只能搜索 is_active=True 的产品
