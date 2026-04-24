# 构建指南

## 前置条件
- Python 3.12+
- Node.js 20+
- PostgreSQL 16（或 Docker）
- Docker & Docker Compose（生产部署）

---

## 后端构建（backend/）

### 1. 创建虚拟环境并安装依赖
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 填写数据库连接信息
```

### 3. 数据库迁移
```bash
python manage.py makemigrations auth_app products cases documents quotes sharing dashboard
python manage.py migrate
```

### 4. 创建管理员
```bash
python scripts/create_admin.py
```

### 5. 收集静态文件
```bash
python manage.py collectstatic --noinput
```

### 6. 启动开发服务器
```bash
python manage.py runserver 0.0.0.0:8000
```

---

## 前端构建（frontend/）

### 1. 安装依赖
```bash
cd frontend
npm install
```

### 2. 配置环境变量
```bash
cp .env.example .env
# VITE_API_BASE_URL=http://localhost:8000（本地开发可不设置，使用 Vite proxy）
```

### 3. 启动开发服务器
```bash
npm run dev
```

### 4. 生产构建
```bash
npm run build
# 输出到 dist/ 目录
```

---

## Docker Compose 构建（生产环境）

### 1. 准备配置
```bash
cp .env.example .env
# 编辑 .env 填写生产环境配置
```

### 2. 构建并启动
```bash
docker-compose up -d --build
```

### 3. 验证服务
```bash
docker-compose ps
# 确认 db、backend、frontend 三个服务都是 Up 状态
curl http://localhost/api/auth/me/  # 应返回 401（未认证）
```

### 4. 查看日志
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

---

## Railway 部署（测试环境）

### 后端
1. 在 Railway 创建新项目
2. 连接 GitHub 后端仓库
3. 添加 PostgreSQL 插件
4. 设置环境变量（DJANGO_SECRET_KEY, CORS_ALLOWED_ORIGINS 等）
5. Railway 自动检测 Dockerfile 并部署

### 前端
1. 在 Vercel 导入 GitHub 前端仓库
2. 设置环境变量：VITE_API_BASE_URL = Railway 后端 URL
3. Vercel 自动构建并部署

---

## 常见问题

### WeasyPrint 安装失败
WeasyPrint 需要系统级依赖（cairo, pango）。在 Docker 中已通过 Dockerfile 安装。本地开发如遇问题：
```bash
# macOS
brew install cairo pango gdk-pixbuf libffi

# Ubuntu
sudo apt-get install libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libcairo2
```

### 数据库连接失败
确认 PostgreSQL 服务已启动，.env 中的数据库配置正确。Docker 环境中 DB_HOST 应为 `db`（服务名）。
