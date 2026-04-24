@echo off
chcp 65001 >nul
echo ========================================
echo   智楷家具内部管理平台 - 本地启动
echo ========================================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python
    pause
    exit /b 1
)

:: 检查 Node
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Node.js
    pause
    exit /b 1
)

:: 后端虚拟环境
if not exist backend\venv (
    echo [创建 Python 虚拟环境...]
    cd backend
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -q -r requirements.txt
    cd ..
)

:: 启动后端（独立脚本，环境变量可靠）
echo [启动后端...]
start "Django Backend" cmd /k "cd /d %~dp0backend && start-local.bat"

:: 等后端启动
timeout /t 6 /nobreak >nul

:: 启动前端
echo [启动前端...]
start "React Frontend" cmd /k "cd /d %~dp0frontend && start-local.bat"

echo.
echo ========================================
echo   启动完成！
echo ========================================
echo   前端: http://localhost:5173
echo   后端: http://localhost:8000
echo   管理员: admin / admin123456
echo   关闭服务请关闭对应的命令行窗口
echo ========================================
pause
