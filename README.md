# AI Assistant - 个人助手（带 Agent 逻辑展示）

一个基于 Vue3 + FastAPI + LangChain 的 AI 助手应用，支持实时展示 Agent 的思考过程和工具调用。

## 功能特性

- 💬 **智能对话**: 基于 LLM 的自然语言对话
- 🤖 **Agent 逻辑展示**: 实时展示 Agent 的思考步骤、工具调用详情
- 🔧 **工具调用**: 支持订单搜索、计算器等工具
- 📊 **流式交互**: 采用流式模式，逐步渲染内容
- 🎨 **现代化界面**: 基于 Vue3 + Element Plus 的响应式界面

## 技术栈

### 前端
- Vue3 + TypeScript
- Vite
- Pinia（状态管理）
- Element Plus（UI 组件库）
- Axios（HTTP 客户端）

### 后端
- Python + FastAPI
- LangChain/LangGraph（Agent 引擎）
- OpenAI API（LLM）
- Uvicorn（ASGI 服务器）

## 项目结构

```
demo-chat/
├── frontend/                 # 前端项目
│   ├── src/
│   │   ├── api/             # API 接口
│   │   ├── components/      # Vue 组件
│   │   ├── stores/          # Pinia 状态管理
│   │   ├── types/           # TypeScript 类型定义
│   │   ├── App.vue          # 根组件
│   │   └── main.ts          # 入口文件
│   ├── package.json
│   └── vite.config.ts
├── backend/                  # 后端项目
│   ├── app/
│   │   ├── agent/           # Agent 引擎
│   │   ├── api/             # API 路由
│   │   ├── models/          # 数据模型
│   │   └── tools/           # 工具层
│   ├── requirements.txt
│   └── .env.example
├── docs/                     # 文档
├── setup.bat / setup.sh      # 环境初始化脚本（Windows/Linux）
└── start.bat / start.sh      # 启动脚本（Windows/Linux）
```

## 快速开始

### 1. 环境要求

- Node.js >= 18
- Python >= 3.9
- OpenAI API Key

### 2. 初始化项目

**Windows 用户**:
```bash
setup.bat
```

**Linux/Mac 用户**:
```bash
./setup.sh
```

该脚本会：
- 创建 Python 虚拟环境
- 安装后端依赖
- 安装前端依赖
- 创建 `.env` 配置文件

### 3. 配置 OpenAI API

编辑 `backend/.env` 文件，配置以下信息：

```env
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL_NAME=gpt-4
```

### 4. 启动服务

**Windows 用户**:
```bash
start.bat
```

**Linux/Mac 用户**:
```bash
./start.sh
```

该脚本会：
- 启动后端服务（端口 8000）
- 启动前端服务（端口 5173）

### 5. 访问应用

- 前端地址: http://localhost:5173
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

## 使用说明

### 基础对话

点击右下角的聊天按钮，打开聊天窗口，输入问题即可开始对话。

### Agent 工具调用

Agent 支持以下工具：

1. **订单搜索**: 查询订单信息
   - 示例: "查询订单号 123456 的信息"
   - 示例: "订单 789012 的金额是多少"

2. **计算器**: 执行数学计算
   - 示例: "计算 100 * 0.9"
   - 示例: "订单号 123456 的金额的 9 折是多少"

### Agent 逻辑展示

聊天窗口会实时展示 Agent 的思考过程：

- 💭 **思考**: Agent 的决策过程
- 🔧 **工具调用**: 调用的工具名称和参数
- ✅ **工具返回**: 工具执行结果
- 🎯 **最终回答**: Agent 生成的最终回答

## 开发说明

### 前端开发

```bash
cd frontend
npm install
npm run dev
```

### 后端开发

**Windows 用户**:
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Linux/Mac 用户**:
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 添加新工具

在 `backend/app/tools/tools.py` 中添加新工具：

```python
from langchain_core.tools import tool

@tool
def your_tool(param: str) -> dict:
    """
    工具描述
    
    Args:
        param: 参数说明
        
    Returns:
        返回结果
    """
    # 实现工具逻辑
    return {"result": "..."}
```

然后在 `get_tools()` 函数中注册工具。

## API 接口

### POST /api/chat/stream

流式聊天接口，实时返回 Agent 的思考过程和工具调用。

**请求体**:
```json
{
  "message": "用户消息",
  "history": [
    {"role": "user", "content": "历史消息"}
  ]
}
```

**响应流** (Server-Sent Events):
```
data: {"type": "thought", "content": "思考内容"}

data: {"type": "tool_call", "tool_name": "search_order", "tool_input": {"order_id": "123456"}}

data: {"type": "tool_result", "tool_output": {...}}

data: {"type": "final_answer", "content": "最终回答"}

data: {"type": "done"}
```

## 注意事项

1. 确保 OpenAI API Key 有效且有足够的额度
2. 首次运行需要安装依赖，可能需要几分钟
3. 前端和后端需要同时运行才能正常使用
4. 如遇网络问题，可尝试配置代理

## 许可证

MIT License
