# Unit 1 后端 NFR 需求计划

## 澄清问题

### Question 1
后端 API 的并发用户预期？（影响 Gunicorn worker 数量和数据库连接池配置）

A) 极低（1-5 人同时在线，小团队内部使用）
B) 低（5-20 人同时在线）
C) 中等（20-50 人同时在线）
D) Other (please describe after [Answer]: tag below)

[Answer]: C

### Question 2
数据库备份策略（生产环境 NAS）？

A) 仅依赖 NAS Hyper Backup 整体备份
B) 定时 pg_dump 导出 SQL + Hyper Backup 双重备份
C) Other (please describe after [Answer]: tag below)

[Answer]: B

---

## 执行计划

### 步骤 1：性能与可扩展性需求
- [x] 定义 API 响应时间目标
- [x] 定义文件上传/处理性能目标
- [x] 定义数据库查询优化策略

### 步骤 2：安全需求
- [x] 定义认证安全策略
- [x] 定义数据保护策略
- [x] 定义 CORS 和 API 安全

### 步骤 3：可靠性与运维需求
- [x] 定义日志策略
- [x] 定义备份与恢复策略
- [x] 定义监控策略

### 步骤 4：技术栈决策
- [x] 确认后端技术栈选择及理由
