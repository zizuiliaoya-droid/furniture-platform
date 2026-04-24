# 应用设计计划

## 计划概述
基于开发文档中已定义的项目结构和数据模型，进行组件识别、服务层设计和依赖关系梳理。

---

## 澄清问题

### Question 1
首页仪表盘的统计数据 API，是创建一个独立的 dashboard app，还是在现有 app 中添加统计接口？

A) 创建独立的 dashboard app（/api/dashboard/stats/）
B) 在各模块的 views.py 中分别添加统计接口，前端聚合
C) 在 common/ 中添加一个统计视图，聚合查询各模块数据
D) Other (please describe after [Answer]: tag below)

[Answer]: A

### Question 2
分享页面的点击追踪（US-7.4），追踪数据存储方式？

A) 扩展现有 ShareAccessLog 模型，增加 event_type 和 object_detail 字段
B) 创建独立的 ClickTrackingLog 模型
C) Other (please describe after [Answer]: tag below)

[Answer]: B

---

## 执行计划

### 步骤 1：后端组件设计
- [x] 定义 auth_app 组件（认证与用户管理）
- [x] 定义 products 组件（产品管理）
- [x] 定义 catalog 组件（产品图册）
- [x] 定义 cases 组件（客户案例）
- [x] 定义 documents 组件（内部文档）
- [x] 定义 quotes 组件（报价方案）
- [x] 定义 sharing 组件（分享功能）
- [x] 定义 search 组件（全局搜索）
- [x] 定义 common 组件（公共工具）
- [x] 定义 dashboard 组件（仪表盘统计）

### 步骤 2：前端组件设计
- [x] 定义页面组件结构（pages/）
- [x] 定义公共组件结构（components/）
- [x] 定义布局组件结构（layouts/）
- [x] 定义服务层结构（services/）
- [x] 定义状态管理结构（store/）

### 步骤 3：组件方法签名
- [x] 定义各后端 Service 类的方法签名
- [x] 定义各前端 Service 的 API 调用方法
- [x] 定义 Store 的状态和 actions

### 步骤 4：服务层设计
- [x] 定义后端服务编排模式
- [x] 定义前端数据流模式

### 步骤 5：组件依赖关系
- [x] 绘制后端组件依赖矩阵
- [x] 绘制前端组件依赖关系
- [x] 定义前后端通信模式
