# 服务层设计

## 后端服务编排模式

### 架构模式
采用 **Service Layer Pattern**：Views（API 入口）→ Services（业务逻辑）→ Models（数据访问）

```
Request → URL Router → View (DRF ViewSet/APIView)
                          ↓
                     Serializer (验证+序列化)
                          ↓
                     Service (业务逻辑)
                          ↓
                     Model (ORM 数据访问)
                          ↓
                     Response
```

### 服务职责划分

| 层级 | 职责 | 示例 |
|------|------|------|
| View | 请求处理、权限检查、调用 Service | ProductViewSet.create() |
| Serializer | 数据验证、序列化/反序列化 | ProductCreateSerializer |
| Service | 业务逻辑编排、跨模型操作 | QuoteService.duplicate() |
| Model | 数据访问、简单计算 | QuoteItem.save() 自动计算 subtotal |

### 跨组件服务调用

| 调用方 | 被调用方 | 场景 |
|--------|----------|------|
| quotes | products | 报价明细添加产品时查询产品信息和配置 |
| sharing | products/cases/quotes/catalog | 获取分享内容时查询对应模块数据 |
| search | products/cases/documents/quotes | 全局搜索时跨模块查询 |
| dashboard | products/cases/quotes | 聚合统计各模块数据 |
| catalog | products | 图册浏览复用产品数据 |
| cases | products | 案例关联产品 |

### 文件存储服务（横切关注点）

FileStorageService 被以下组件共用：
- products（产品图片）
- cases（案例图片）
- documents（文档文件）

统一的文件路径格式：`{subdirectory}/{YYYYMMDD}/{uuid}_{filename}`

---

## 前端数据流模式

### 架构模式
```
用户操作 → Page Component → Service (API 调用) → Backend API
                ↓                                      ↓
           Store (Zustand)                        Response
                ↓                                      ↓
           UI 更新 ← ← ← ← ← ← ← ← ← ← ← ← 数据返回
```

### 状态管理策略

| 数据类型 | 管理方式 | 说明 |
|----------|----------|------|
| 认证状态 | authStore (Zustand) | 全局持久化，Token + User |
| 产品列表 | productStore (Zustand) | 全局，含分页/筛选/搜索状态 |
| 页面局部数据 | React useState/useEffect | 表单数据、详情数据、临时状态 |
| 服务端缓存 | 无（直接请求） | 简单场景不引入额外缓存层 |

### API 拦截器设计

```typescript
// Axios 请求拦截器
- 自动附加 Authorization: Token {token}

// Axios 响应拦截器
- 401: 清除 Token → 跳转登录页
- 403: 显示权限不足提示
- 500: 显示服务器错误提示
```

### 路由守卫设计

```
ProtectedRoute 组件:
  ├── 检查 authStore.isAuthenticated
  ├── 未认证 → 重定向到 /login
  ├── 已认证 → 检查角色权限
  │   ├── 权限不足 → 显示 403 页面
  │   └── 权限通过 → 渲染子组件
  └── 公开路由（/login, /s/:token）→ 直接渲染
```
