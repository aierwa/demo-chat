@echo off
chcp 65001 >nul
echo ========================================
echo AI Assistant - 启动脚本
echo ========================================

echo.
echo [1/3] 检查后端虚拟环境...
if not exist "backend\venv\Scripts\activate.bat" (
    echo 后端虚拟环境不存在，请先运行 setup.bat
    pause
    exit /b 1
)

echo.
echo [2/3] 启动后端服务...
start "AI Assistant Backend" cmd /k "cd backend && venv\Scripts\activate && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo.
echo [3/3] 启动前端服务...
start "AI Assistant Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo 服务启动中...
echo ========================================
echo.
echo 前端地址: http://localhost:5173
echo 后端地址: http://localhost:8000
echo API 文档: http://localhost:8000/docs
echo.
echo 按任意键关闭此窗口（服务将继续运行）
pause >nul
