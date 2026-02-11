import os
from typing import Annotated, TypedDict, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from app.agent.midware import SkillMiddleware

import json

from app.tools.tools import get_tools

load_dotenv()


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


class AgentEngine:
    def __init__(self):
        self.llm = ChatOpenAI(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("OPENAI_MODEL_NAME"),
            temperature=0.7,
            streaming=True
        )
        self.tools = get_tools()
        
        self.agent = create_agent(
            system_prompt="你是一名非常有用的企业个人助手。",
            model=self.llm,
            tools=self.tools,
            middleware=[SkillMiddleware()]
        )

    async def stream_chat(self, user_message: str, history: list[dict]):
        """
        新版 LangChain Agent 流式聊天
        """
        messages = []
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        messages.append(HumanMessage(content=user_message))

        all_messages = list(messages)

        # 2. 新版 Agent 流式
        async for stream_mode, chunk in self.agent.astream(
            {"messages": messages},
            stream_mode=["updates", "messages"],  # 同时拿步骤 + 打字机
        ):
            if stream_mode == "updates":
                for node_name, node_output in chunk.items():
                    if node_name == "model":  # 大模型节点
                        for msg in node_output.get("messages", []):
                            all_messages.append(msg)
                            if isinstance(msg, AIMessage):
                                # 思考
                                if msg.content:
                                    yield {
                                        "type": "thought",
                                        "content": msg.content
                                    }
                                # 工具调用
                                if msg.tool_calls:
                                    for tc in msg.tool_calls:
                                        yield {
                                            "type": "tool_call",
                                            "tool_name": tc["name"],
                                            "tool_input": tc["args"]
                                        }
                    elif node_name == "tools": # 工具节点
                        for msg in node_output.get("messages", []):
                            all_messages.append(msg)
                            if isinstance(msg, ToolMessage):
                                # 工具调用结果
                                if msg.content:
                                    yield {
                                        "type": "tool_result",
                                        "tool_output": msg.content
                                    }
                                yield {
                                    "type": "tool_result",
                                    "tool_output": msg.content
                                }

        # 3. 取最终回答
        final_answer = ""
        for msg in reversed(all_messages):
            if isinstance(msg, AIMessage) and not msg.tool_calls:
                final_answer = msg.content
                break

        if final_answer:
            yield {
                "type": "final_answer",
                "content": final_answer
            }

        yield {"type": "done"}


def create_agent_engine():
    return AgentEngine()
