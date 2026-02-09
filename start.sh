#!/bin/bash

echo "========================================"
echo "AI Assistant - 启动脚本"
echo "========================================"

echo ""
echo "[1/3] 检查后端虚拟环境..."
if [ ! -d "backend/venv" ]; then
    echo "后端虚拟环境不存在，请先运行 ./setup.sh"
    read -p "按任意键退出..."
    exit 1
fi

echo ""
echo "[2/3] 启动后端服务..."
cd backend
source venv/Scripts/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

echo ""
echo "[3/3] 启动前端服务..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================"
echo "服务启动中..."
echo "========================================"
echo ""
echo "前端地址: http://localhost:5173"
echo "后端地址: http://localhost:8000"
echo "API 文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服务"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo ''; echo '服务已停止'; exit 0" INT TERM

wait
