from pydantic import BaseModel
from typing import Optional, Any, Dict


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[Message]


class ChatStreamChunk(BaseModel):
    type: str
    content: Optional[str] = None
    tool_name: Optional[str] = None
    tool_input: Optional[Any] = None
    tool_output: Optional[Any] = None
