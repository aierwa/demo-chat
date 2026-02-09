from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.models.schemas import ChatRequest
from app.agent.engine import create_agent_engine
import json

router = APIRouter()
agent_engine = create_agent_engine()


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    流式聊天接口，实时返回 Agent 的思考过程和工具调用
    """
    
    async def generate():
        try:
            history = [{"role": msg.role, "content": msg.content} for msg in request.history]
            
            async for chunk in agent_engine.stream_chat(request.message, history):
                data = json.dumps(chunk, ensure_ascii=False)
                yield f"data: {data}\n\n"
            
        except Exception as e:
            print(f"[错误] {e}")
            error_data = json.dumps({
                "type": "error",
                "content": str(e)
            }, ensure_ascii=False)
            yield f"data: {error_data}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
