# 单元测试指南

## 后端单元测试

### 测试框架
- Django TestCase + DRF APITestCase
- pytest-django（推荐）

### 安装测试依赖
```bash
pip install pytest pytest-django factory-boy
```

### pytest 配置（backend/pytest.ini）
```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = tests.py test_*.py *_tests.py
```

### 运行全部测试
```bash
cd backend
pytest
```

### 关键测试场景

#### 认证模块
- 正确凭据登录成功，返回 Token
- 错误密码登录失败，返回 400
- 禁用用户登录失败
- 登出删除 Token
- 管理员创建/禁用用户
- 员工无权访问管理员接口（403）

#### 产品模块
- 产品 CRUD 完整流程
- 产品搜索（名称/编号/描述/配置）
- 分类树查询（三维度）
- 分类删除限制（有子分类或产品时禁止）
- 图片上传和缩略图生成
- Excel 导入（成功/失败/编号重复）
- 软删除（is_active=False）

#### 报价模块
- 报价单 CRUD
- 明细金额自动计算（subtotal = price × qty × (1 - discount/100)）
- 总金额自动更新
- 状态流转验证（DRAFT→SENT→CONFIRMED，不可回退）
- 报价复制（含明细）
- PDF 导出

#### 分享模块
- 创建分享链接（含/不含密码）
- 访问验证（过期/次数限制/禁用）
- 密码验证
- 访问计数递增
- 点击追踪记录

---

## 前端单元测试

### 测试框架
- Vitest + React Testing Library

### 安装测试依赖
```bash
cd frontend
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom
```

### Vitest 配置（vite.config.ts 添加）
```typescript
export default defineConfig({
  test: {
    environment: 'jsdom',
    globals: true,
  },
});
```

### 运行测试
```bash
npm run test
```

### 关键测试场景
- authStore：登录/登出状态管理
- productStore：筛选/分页状态
- ProtectedRoute：未认证重定向
- API 拦截器：401 自动跳转登录
