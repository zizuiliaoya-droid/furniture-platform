# 部署架构 — Unit 1 后端

## 测试环境部署架构

```
GitHub Repository (backend)
        │
        │ git push main
        ▼
Railway (自动部署)
├── Build: Dockerfile
│   ├── python:3.12-slim 基础镜像
│   ├── 安装 WeasyPrint 系统依赖
│   ├── pip install requirements.txt
│   └── collectstatic
│
├── Run: entrypoint.sh
│   ├── makemigrations + migrate
│   ├── create_admin.py
│   └── gunicorn (2 workers)
│
├── PostgreSQL Plugin
│   └── DATABASE_URL 自动注入
│
├── 持久化卷
│   └── /app/media (媒体文件)
│
└── 网络
    ├── HTTPS 自动配置
    ├── 域名: *.railway.app
    └── CORS: 允许 Vercel 前端域名
```

### 测试环境 URL 结构
```
后端 API:  https://<app-name>.railway.app/api/
静态文件:  https://<app-name>.railway.app/static/ (WhiteNoise)
媒体文件:  https://<app-name>.railway.app/media/ (Django)
```

---

## 生产环境部署架构

```
Synology DS920+ NAS
├── Docker Compose
│   │
│   ├── db (postgres:16-alpine)
│   │   ├── Port: 5432 (内部)
│   │   ├── Volume: postgres_data
│   │   └── Healthcheck: pg_isready
│   │
│   ├── backend (Django + Gunicorn)
│   │   ├── Port: 8000 (内部)
│   │   ├── Workers: 4
│   │   ├── Volume: media_data, static_data
│   │   ├── Depends: db (healthy)
│   │   └── Restart: always
│   │
│   └── frontend (React + Nginx)
│       ├── Port: 80 (外部)
│       ├── Nginx 路由:
│       │   ├── /          → 前端静态文件
│       │   ├── /api/*     → proxy_pass backend:8000
│       │   ├── /media/*   → alias /app/media/
│       │   └── /static/*  → alias /app/staticfiles/
│       ├── Volume: media_data (只读), static_data (只读)
│       └── Depends: backend
│
├── NAS Task Scheduler
│   └── 每日 02:00 执行 backup.sh (pg_dump)
│
├── Hyper Backup
│   └── 备份 Docker volumes (postgres_data + media_data)
│
└── 网络访问
    ├── 局域网: http://<nas-ip>
    └── 外网: Synology QuickConnect
```

### 生产环境 URL 结构
```
局域网:
  前端:    http://<nas-ip>/
  API:     http://<nas-ip>/api/
  媒体:    http://<nas-ip>/media/

外网 (QuickConnect):
  前端:    https://<quickconnect-id>.quickconnect.to/
  分享:    https://<quickconnect-id>.quickconnect.to/s/{token}
```

---

## 部署流程

### 测试环境（自动）
```
1. 开发者 push 代码到 GitHub main 分支
2. Railway 自动检测变更
3. Railway 构建 Docker 镜像
4. Railway 部署新版本（零停机）
5. 自动执行 entrypoint.sh（迁移+启动）
```

### 生产环境（手动）
```
1. SSH 到 NAS 或通过 DSM 终端
2. cd /volume1/docker/furniture-app
3. git pull（或上传新代码）
4. docker-compose build backend
5. docker-compose up -d
6. 验证服务正常运行
```

### 首次部署（生产环境）
```
1. 在 NAS 上安装 Docker（通过 DSM 套件中心）
2. 创建项目目录: /volume1/docker/furniture-app
3. 上传代码和 docker-compose.yml
4. 复制 .env.example → .env，填写配置
5. docker-compose up -d
6. 验证: http://<nas-ip>
7. 配置 NAS Task Scheduler 定时备份
8. 配置 Hyper Backup
```
