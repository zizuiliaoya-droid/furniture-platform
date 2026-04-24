# 基础设施设计 — Unit 1 后端

## 逻辑组件 → 基础设施映射

| 逻辑组件 | 测试环境（Railway） | 生产环境（NAS Docker） |
|----------|---------------------|----------------------|
| WSGI Server | Railway 内置（Gunicorn） | Docker: Gunicorn |
| Reverse Proxy | 无（Railway 直接暴露） | Docker: Nginx（前端容器） |
| 关系数据库 | Railway PostgreSQL 插件 | Docker: postgres:16-alpine |
| 文件存储 | Railway 持久化存储卷 | Docker Volume → NAS 本地磁盘 |
| 静态文件 | WhiteNoise（Django 直接服务） | Nginx /static/* |
| 媒体文件 | Django MEDIA_URL（开发模式） | Nginx /media/* |
| PDF 引擎 | WeasyPrint（Dockerfile 安装依赖） | WeasyPrint（同 Dockerfile） |
| CI/CD | GitHub → Railway 自动部署 | 手动 docker-compose up |
| 域名/SSL | Railway 自动 HTTPS | QuickConnect / DDNS |
| 备份 | 无（测试数据不重要） | pg_dump + Hyper Backup |

---

## 测试环境配置

### Railway 项目配置

```
Railway Project
├── Backend Service (Django)
│   ├── 构建: Dockerfile
│   ├── 启动: gunicorn config.wsgi --bind 0.0.0.0:$PORT --workers 2
│   ├── 环境变量:
│   │   ├── DJANGO_SECRET_KEY=<random-string>
│   │   ├── DJANGO_DEBUG=False
│   │   ├── DJANGO_ALLOWED_HOSTS=*.railway.app
│   │   ├── CORS_ALLOWED_ORIGINS=https://<vercel-domain>
│   │   ├── ADMIN_USERNAME=admin
│   │   ├── ADMIN_PASSWORD=<secure-password>
│   │   └── DATABASE_URL=<auto-injected>
│   └── 持久化卷: /app/media
│
└── PostgreSQL Plugin
    └── DATABASE_URL 自动注入到 Backend Service
```

### Dockerfile（后端）

```dockerfile
FROM python:3.12-slim

# WeasyPrint 系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libcairo2 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
```

### entrypoint.sh

```bash
#!/bin/bash
set -e

echo "Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Creating admin user..."
python scripts/create_admin.py

echo "Starting Gunicorn..."
exec gunicorn config.wsgi \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers ${GUNICORN_WORKERS:-2} \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
```

---

## 生产环境配置

### docker-compose.yml（后端相关部分）

```yaml
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    restart: always
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: ${DB_NAME:-furniture_app}
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-postgres}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-postgres}"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: always
    ports:
      - "8000:8000"
    environment:
      - DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
      - DJANGO_DEBUG=False
      - DJANGO_ALLOWED_HOSTS=${DJANGO_ALLOWED_HOSTS:-localhost}
      - CORS_ALLOWED_ORIGINS=${CORS_ALLOWED_ORIGINS:-http://localhost}
      - DB_NAME=${DB_NAME:-furniture_app}
      - DB_USER=${DB_USER:-postgres}
      - DB_PASSWORD=${DB_PASSWORD:-postgres}
      - DB_HOST=db
      - DB_PORT=5432
      - ADMIN_USERNAME=${ADMIN_USERNAME:-admin}
      - ADMIN_PASSWORD=${ADMIN_PASSWORD:-admin123456}
      - GUNICORN_WORKERS=4
    volumes:
      - media_data:/app/media
      - static_data:/app/staticfiles
    depends_on:
      db:
        condition: service_healthy

volumes:
  postgres_data:
  media_data:
  static_data:
```

### .env.example

```bash
# Django
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,your-nas-ip

# CORS
CORS_ALLOWED_ORIGINS=http://localhost,http://your-nas-ip

# Database
DB_NAME=furniture_app
DB_USER=postgres
DB_PASSWORD=your-db-password

# Admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-admin-password
```

---

## 备份基础设施

### pg_dump 定时备份脚本

```bash
#!/bin/bash
# backup.sh - 放在 NAS 上通过 Task Scheduler 每日执行
BACKUP_DIR="/volume1/docker/furniture-backup"
DATE=$(date +%Y%m%d_%H%M%S)
KEEP_DAYS=7

# 执行备份
docker exec furniture-db pg_dump -U postgres furniture_app > \
    "${BACKUP_DIR}/furniture_${DATE}.sql"

# 清理旧备份
find "${BACKUP_DIR}" -name "*.sql" -mtime +${KEEP_DAYS} -delete

echo "Backup completed: furniture_${DATE}.sql"
```

### 恢复流程
```bash
# 1. 停止后端服务
docker-compose stop backend

# 2. 恢复数据库
docker exec -i furniture-db psql -U postgres furniture_app < backup_file.sql

# 3. 恢复媒体文件（从 Hyper Backup）
# 通过 NAS Hyper Backup 界面恢复 media_data volume

# 4. 重启服务
docker-compose start backend
```
