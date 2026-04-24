# Unit 1 后端功能设计计划

## 澄清问题

### Question 1
报价单状态流转是否严格单向？例如"已确认"的报价单能否改回"草稿"？

A) 严格单向：草稿→已发送→已确认，任意状态可→已取消，不可回退
B) 允许回退：已发送可回退到草稿，已确认不可回退
C) 完全灵活：任意状态可切换到任意状态
D) Other (please describe after [Answer]: tag below)

[Answer]: A

### Question 2
产品删除策略 — 当产品被案例关联或报价单引用时：

A) 软删除（标记 is_active=false），保留数据完整性
B) 硬删除产品，但案例关联和报价明细中的产品名称快照保留
C) 禁止删除被引用的产品，提示用户先解除关联
D) Other (please describe after [Answer]: tag below)

[Answer]: A

### Question 3
仪表盘统计 API 的数据范围？

A) 全量统计（所有数据的总数）+ 本月新增数
B) 全量统计 + 本月新增 + 最近 7 天趋势数据
C) 全量统计 + 本月新增 + 最近 30 天每日统计（用于图表）
D) Other (please describe after [Answer]: tag below)

[Answer]: C

---

## 执行计划

### 步骤 1：领域实体设计
- [x] 定义所有实体及其属性、约束
- [x] 定义实体间关系（FK、M2M、树形）
- [x] 定义新增模型（ClickTrackingLog、Dashboard 聚合）

### 步骤 2：业务规则设计
- [x] 认证与权限规则
- [x] 产品管理业务规则（分类、图片、配置、导入）
- [x] 报价计算与状态流转规则
- [x] 分享验证与访问控制规则
- [x] 文件存储与缩略图规则

### 步骤 3：业务逻辑模型
- [x] 各 Service 的详细业务流程
- [x] 跨模块交互流程
- [x] 错误处理与边界情况
