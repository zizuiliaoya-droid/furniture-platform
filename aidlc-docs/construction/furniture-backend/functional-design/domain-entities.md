# 领域实体设计 — Unit 1 后端

## 实体总览

| 实体 | App | 说明 |
|------|-----|------|
| User | auth_app | 用户（扩展 AbstractUser） |
| Category | products | 产品分类（树形，三维度） |
| Product | products | 产品 |
| ProductImage | products | 产品图片 |
| ProductConfig | products | 产品配置 |
| ProductCategory | products | 产品-分类关联（M2M through） |
| Case | cases | 客户案例 |
| CaseImage | cases | 案例图片 |
| CaseProduct | cases | 案例-产品关联（M2M through） |
| DocumentFolder | documents | 文件夹（树形） |
| Document | documents | 文档文件 |
| Quote | quotes | 报价单 |
| QuoteItem | quotes | 报价明细 |
| ShareLink | sharing | 分享链接 |
| ShareAccessLog | sharing | 分享访问记录 |
| ClickTrackingLog | sharing | 点击追踪记录（新增） |

---

## 实体详细定义

### User
```
字段            类型              约束                    说明
username        VARCHAR(150)      UNIQUE, NOT NULL        用户名
password        VARCHAR(128)      NOT NULL                密码（哈希）
role            VARCHAR(10)       NOT NULL, DEFAULT='STAFF'  角色：ADMIN/STAFF
display_name    VARCHAR(100)      NOT NULL                显示名称
is_active       BOOLEAN           DEFAULT=True            是否启用（软删除也用此字段）
date_joined     DATETIME          AUTO                    注册时间
```

### Category
```
字段            类型              约束                    说明
id              BIGINT            PK, AUTO                主键
name            VARCHAR(100)      NOT NULL                分类名称
parent          FK → Category     NULL=顶级               父分类
dimension       VARCHAR(10)       NOT NULL                维度：TYPE/SPACE/ORIGIN
sort_order      INT               DEFAULT=0               排序序号
UNIQUE: (parent, name, dimension)
```

### Product
```
字段            类型              约束                    说明
id              BIGINT            PK, AUTO                主键
name            VARCHAR(200)      NOT NULL                产品名称
code            VARCHAR(50)       UNIQUE, NULL            产品编号
description     TEXT              NULL                    产品描述
category        FK → Category     NOT NULL                主分类
origin          VARCHAR(10)       NOT NULL                产地：IMPORT/DOMESTIC/CUSTOM
min_price       DECIMAL(10,2)     NULL                    最低售价
is_active       BOOLEAN           DEFAULT=True            是否上架（兼软删除标记）
created_by      FK → User         NOT NULL                创建人
categories      M2M → Category    through=ProductCategory 关联分类
created_at      DATETIME          AUTO                    创建时间
updated_at      DATETIME          AUTO                    更新时间
```
**软删除说明**: is_active=False 同时表示"下架"和"已删除"。管理员删除产品时设置 is_active=False，而非物理删除。

### ProductImage
```
字段            类型              约束                    说明
id              BIGINT            PK, AUTO                主键
product         FK → Product      NOT NULL, CASCADE       所属产品
image_path      VARCHAR(500)      NOT NULL                图片相对路径
thumbnail_path  VARCHAR(500)      NULL                    缩略图路径（JSON: {small, medium}）
sort_order      INT               DEFAULT=0               排序
is_cover        BOOLEAN           DEFAULT=False           是否封面
created_at      DATETIME          AUTO                    创建时间
```

### ProductConfig
```
字段            类型              约束                    说明
id              BIGINT            PK, AUTO                主键
product         FK → Product      NOT NULL, CASCADE       所属产品
config_name     VARCHAR(200)      NOT NULL                配置名称
attributes      JSON              DEFAULT={}              自定义属性
guide_price     DECIMAL(10,2)     NULL                    指导价格
created_at      DATETIME          AUTO                    创建时间
```

### Case
```
字段            类型              约束                    说明
id              BIGINT            PK, AUTO                主键
title           VARCHAR(200)      NOT NULL                案例标题
description     TEXT              NULL                    项目描述
industry        VARCHAR(20)       NOT NULL                行业分类
created_by      FK → User         NOT NULL                创建人
products        M2M → Product     through=CaseProduct     关联产品
created_at      DATETIME          AUTO                    创建时间
updated_at      DATETIME          AUTO                    更新时间
```

### DocumentFolder
```
字段            类型              约束                    说明
id              BIGINT            PK, AUTO                主键
name            VARCHAR(200)      NOT NULL                文件夹名称
doc_type        VARCHAR(15)       NOT NULL                DESIGN/TRAINING/CERTIFICATE
parent          FK → self         NULL=顶级               父文件夹
sort_order      INT               DEFAULT=0               排序
created_at      DATETIME          AUTO                    创建时间
```

### Document
```
字段            类型              约束                    说明
id              BIGINT            PK, AUTO                主键
name            VARCHAR(300)      NOT NULL                文件名
doc_type        VARCHAR(15)       NOT NULL                文档类型
folder          FK → DocumentFolder  NULL                 所属文件夹
file_path       VARCHAR(500)      NOT NULL                文件相对路径
file_size       BIGINT            NOT NULL                文件大小（字节）
mime_type       VARCHAR(100)      NOT NULL                MIME 类型
tags            JSON              DEFAULT=[]              标签数组
created_by      FK → User         NOT NULL                创建人
created_at      DATETIME          AUTO                    创建时间
```

### Quote
```
字段            类型              约束                    说明
id              BIGINT            PK, AUTO                主键
title           VARCHAR(200)      NOT NULL                报价单标题
customer_name   VARCHAR(200)      NOT NULL                客户名称
status          VARCHAR(15)       DEFAULT='DRAFT'         DRAFT/SENT/CONFIRMED/CANCELLED
notes           TEXT              NULL                    备注
terms           TEXT              NULL                    条款
total_amount    DECIMAL(12,2)     DEFAULT=0               总金额（自动计算）
created_by      FK → User         NOT NULL                创建人
created_at      DATETIME          AUTO                    创建时间
updated_at      DATETIME          AUTO                    更新时间
```

### QuoteItem
```
字段            类型              约束                    说明
id              BIGINT            PK, AUTO                主键
quote           FK → Quote        NOT NULL, CASCADE       所属报价单
product         FK → Product      NULL, SET_NULL          关联产品（可空）
product_name    VARCHAR(200)      NOT NULL                产品名称（快照）
config_name     VARCHAR(200)      NULL                    配置名称
unit_price      DECIMAL(10,2)     NOT NULL                单价
quantity        INT               NOT NULL, MIN=1         数量
discount        DECIMAL(5,2)      DEFAULT=0, 0-100        折扣百分比
subtotal        DECIMAL(12,2)     AUTO                    小计（自动计算）
sort_order      INT               DEFAULT=0               排序
```

### ShareLink
```
字段              类型              约束                    说明
id                BIGINT            PK, AUTO                主键
token             VARCHAR(64)       UNIQUE, INDEX           UUID
content_type      VARCHAR(10)       NOT NULL                PRODUCT/CASE/QUOTE/CATALOG
object_id         INT               NULL                    关联对象 ID（CATALOG 时为空）
title             VARCHAR(200)      NOT NULL                分享标题
password_hash     VARCHAR(128)      NULL                    密码哈希（空=无密码）
expires_at        DATETIME          NULL                    过期时间（NULL=永不过期）
max_access_count  INT               NULL                    最大访问次数（NULL=无限制）
access_count      INT               DEFAULT=0               已访问次数
is_active         BOOLEAN           DEFAULT=True            是否启用
created_by        FK → User         NOT NULL                创建人
created_at        DATETIME          AUTO                    创建时间
```

### ShareAccessLog
```
字段            类型              约束                    说明
id              BIGINT            PK, AUTO                主键
share_link      FK → ShareLink    NOT NULL, CASCADE       所属分享链接
accessed_at     DATETIME          AUTO                    访问时间
ip_address      VARCHAR(45)       NULL                    IP 地址
user_agent      VARCHAR(500)      NULL                    浏览器信息
```

### ClickTrackingLog（新增）
```
字段            类型              约束                    说明
id              BIGINT            PK, AUTO                主键
share_link      FK → ShareLink    NOT NULL, CASCADE       所属分享链接
event_type      VARCHAR(20)       NOT NULL                事件类型：PRODUCT_CLICK/QUOTE_ITEM_CLICK
object_id       INT               NOT NULL                被点击对象 ID
object_name     VARCHAR(200)      NULL                    被点击对象名称（快照）
clicked_at      DATETIME          AUTO                    点击时间
ip_address      VARCHAR(45)       NULL                    IP 地址
```

---

## 实体关系图（文本）

```
User ──1:N──► Product (created_by)
User ──1:N──► Case (created_by)
User ──1:N──► Document (created_by)
User ──1:N──► Quote (created_by)
User ──1:N──► ShareLink (created_by)

Category ──1:N──► Category (parent, 树形自引用)
Category ──1:N──► Product (category, 主分类)
Category ──M:N──► Product (through ProductCategory)

Product ──1:N──► ProductImage
Product ──1:N──► ProductConfig
Product ──M:N──► Case (through CaseProduct)
Product ──1:N──► QuoteItem (可空, SET_NULL)

Case ──1:N──► CaseImage

DocumentFolder ──1:N──► DocumentFolder (parent, 树形自引用)
DocumentFolder ──1:N──► Document

Quote ──1:N──► QuoteItem (CASCADE)

ShareLink ──1:N──► ShareAccessLog (CASCADE)
ShareLink ──1:N──► ClickTrackingLog (CASCADE)
```
