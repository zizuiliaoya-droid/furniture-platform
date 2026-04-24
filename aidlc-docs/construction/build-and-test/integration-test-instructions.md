# 集成测试指南

## 测试环境搭建

### 使用 Docker Compose 启动完整环境
```bash
docker-compose up -d
# 等待所有服务就绪
sleep 10
```

---

## 集成测试场景

### 场景 1：完整登录流程
1. POST /api/auth/login/ → 获取 Token
2. GET /api/auth/me/ （携带 Token）→ 返回用户信息
3. POST /api/auth/logout/ → Token 失效
4. GET /api/auth/me/ → 401

### 场景 2：产品管理完整流程
1. 管理员登录
2. POST /api/categories/ → 创建分类
3. POST /api/products/ → 创建产品
4. POST /api/products/{id}/upload_images/ → 上传图片
5. GET /api/products/{id}/ → 验证产品详情含图片和缩略图
6. POST /api/products/{id}/configs/ → 添加配置
7. GET /api/catalog/ → 验证图册中可见

### 场景 3：报价→分享→外部访问
1. 管理员登录
2. POST /api/quotes/ → 创建报价单
3. POST /api/quotes/{id}/items/ → 添加明细
4. 验证 total_amount 自动计算
5. POST /api/shares/ → 创建分享链接
6. GET /api/share/{token}/ → 无需认证访问分享内容
7. 验证 access_count 递增

### 场景 4：分享密码验证
1. 创建带密码的分享链接
2. GET /api/share/{token}/ → 返回 requires_password: true
3. POST /api/share/{token}/verify/ （错误密码）→ 400
4. POST /api/share/{token}/verify/ （正确密码）→ 返回内容

### 场景 5：权限控制
1. 员工登录
2. GET /api/products/ → 200（只返回 is_active=True）
3. POST /api/products/ → 403（无权创建）
4. DELETE /api/products/{id}/ → 403（无权删除）
5. GET /api/auth/users/ → 403（无权查看用户列表）

### 场景 6：文件上传与下载
1. POST /api/documents/upload/ → 上传文件
2. 验证文件存储在 MEDIA_ROOT
3. GET /api/documents/{id}/download/ → 下载文件
4. 验证文件内容一致

### 场景 7：仪表盘统计
1. 创建若干产品、案例、报价单
2. GET /api/dashboard/stats/ → 验证统计数据正确
3. 验证 daily 数组包含 30 天数据

---

## 运行集成测试

### 手动测试（推荐初期）
使用 Postman 或 curl 按上述场景逐步验证。

### 自动化测试（后续）
```bash
# 使用 pytest + requests 编写集成测试
cd backend
pytest tests/integration/ -v
```

---

## 清理
```bash
docker-compose down -v  # 删除容器和数据卷
```
