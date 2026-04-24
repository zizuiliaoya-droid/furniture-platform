# Unit 1 后端代码生成计划

## 单元上下文
- **单元名称**: furniture-backend
- **仓库**: 独立 GitHub 仓库
- **技术栈**: Django 5.x + DRF 3.15+ + PostgreSQL 16
- **代码位置**: 工作区根目录下的 `backend/` 目录
- **故事覆盖**: US-1.2 ~ US-8.2（除 US-1.1 台灯交互为纯前端）

---

## 代码生成步骤

### Step 1: 项目骨架与配置 ✅
- [x] Django 项目结构 (config/)
- [x] settings.py（完整配置）
- [x] urls.py, wsgi.py
- [x] requirements.txt, .env.example, manage.py

### Step 2: 公共工具模块 (common/) ✅
- [x] common/file_storage.py — FileStorageService
- [x] common/pagination.py — StandardPagination
- [x] common/exceptions.py — 全局异常处理器

### Step 3: 认证与用户管理 (auth_app/) ✅
- [x] models.py, serializers.py, permissions.py, services.py, views.py, urls.py
- [x] 覆盖故事: US-1.2, US-1.3, US-1.4, US-1.5, US-1.6

### Step 4: 产品管理 (products/) ✅
- [x] models.py, serializers.py, services.py, views.py, urls.py
- [x] 覆盖故事: US-2.1 ~ US-2.12

### Step 5: 产品图册 (catalog/) ✅
- [x] views.py, urls.py
- [x] 覆盖故事: US-3.1, US-3.2

### Step 6: 客户案例 (cases/) ✅
- [x] models.py, serializers.py, views.py, urls.py
- [x] 覆盖故事: US-4.1 ~ US-4.5

### Step 7: 内部文档 (documents/) ✅
- [x] models.py, serializers.py, views.py, urls.py
- [x] 覆盖故事: US-5.1 ~ US-5.6

### Step 8: 报价方案 (quotes/) ✅
- [x] models.py, serializers.py, services.py, views.py, urls.py
- [x] templates/quotes/pdf_template.html
- [x] 覆盖故事: US-6.1 ~ US-6.6

### Step 9: 分享功能 (sharing/) ✅
- [x] models.py, serializers.py, services.py, views.py, urls.py
- [x] 覆盖故事: US-7.1 ~ US-7.4

### Step 10: 全局搜索 (search/) ✅
- [x] views.py, urls.py
- [x] 覆盖故事: US-8.1

### Step 11: 仪表盘 (dashboard/) ✅
- [x] services.py, views.py, urls.py
- [x] 覆盖故事: US-8.2

### Step 12: 部署配置 ✅
- [x] scripts/create_admin.py
- [x] entrypoint.sh
- [x] Dockerfile（含 WeasyPrint 依赖）
- [x] Procfile, runtime.txt

### Step 13: 代码摘要文档
- [ ] aidlc-docs/construction/furniture-backend/code/code-summary.md
