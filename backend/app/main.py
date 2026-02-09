from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.chat import router as chat_router
from app.tools.tools import get_rag_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    在启动时初始化RAG知识库
    """
    print("=" * 50)
    print("应用启动中...")
    print("=" * 50)
    
    try:
        print("初始化RAG知识库...")
        rag_manager = get_rag_manager()
        rag_manager.initialize_knowledge_base()
        
        kb_info = rag_manager.get_knowledge_base_info()
        print(f"知识库信息: {kb_info}")
    except Exception as e:
        print(f"初始化RAG知识库失败: {e}")
    
    print("=" * 50)
    print("应用启动完成")
    print("=" * 50)
    
    yield
    
    print("应用关闭中...")


app = FastAPI(
    title="AI Assistant API",
    description="AI Assistant with Agent Logic Visualization",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api/chat", tags=["chat"])


@app.get("/")
async def root():
    return {
        "message": "AI Assistant API",
        "version": "1.0.0",
        "endpoints": {
            "chat_stream": "/api/chat/stream"
        }
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
