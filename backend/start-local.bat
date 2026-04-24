@echo off
chcp 65001 >nul
cd /d %~dp0

call venv\Scripts\activate.bat

set DB_ENGINE=sqlite
set DJANGO_DEBUG=True
set DJANGO_SECRET_KEY=local-dev-secret-key
set DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
set CORS_ALLOWED_ORIGINS=http://localhost:5173
set ADMIN_USERNAME=admin
set ADMIN_PASSWORD=admin123456

echo [迁移数据库...]
python manage.py makemigrations --noinput 2>nul
python manage.py migrate --noinput
python scripts\create_admin.py 2>nul

echo.
echo [启动后端服务器 http://localhost:8000]
python manage.py runserver 0.0.0.0:8000
