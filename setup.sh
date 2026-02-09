#!/bin/bash

echo "========================================"
echo "AI Assistant - 环境初始化脚本"
echo "========================================"

echo ""
echo "[1/4] 创建后端虚拟环境..."
cd backend
if [ ! -d "venv" ]; then
    python -m venv venv
    echo "虚拟环境创建成功"
else
    echo "虚拟环境已存在"
fi

echo ""
echo "[2/4] 激活虚拟环境并安装依赖..."
source venv/Scripts/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "[3/4] 配置环境变量..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "已创建 .env 文件，请编辑配置 OpenAI API 信息"
    echo ""
    echo "重要：请编辑 backend/.env 文件，配置以下信息："
    echo "  - OPENAI_BASE_URL"
    echo "  - OPENAI_API_KEY"
    echo "  - OPENAI_MODEL_NAME"
    echo ""
else
    echo ".env 文件已存在"
fi

cd ..

echo ""
echo "[4/4] 安装前端依赖..."
cd frontend
npm install
cd ..

echo ""
echo "========================================"
echo "初始化完成！"
echo "========================================"
echo ""
echo "下一步："
echo "1. 编辑 backend/.env 文件，配置 OpenAI API 信息"
echo "2. 运行 ./start.sh 启动服务"
echo ""
