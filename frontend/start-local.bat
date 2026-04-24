@echo off
chcp 65001 >nul
cd /d %~dp0

if not exist node_modules (
    echo [安装前端依赖...]
    call npm install --registry https://registry.npmmirror.com
)

echo.
echo [启动前端服务器 http://localhost:5173]
npm run dev
