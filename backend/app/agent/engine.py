import os
from typing import Annotated, TypedDict, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
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
        self.tool_node = ToolNode(self.tools)
        
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        self.graph = self._build_graph()
    
    def _build_graph(self):
        workflow = StateGraph(AgentState)
        
        workflow.add_node("agent", self._call_model)
        workflow.add_node("tools", self.tool_node)
        
        workflow.set_entry_point("agent")
        
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END,
            },
        )
        
        workflow.add_edge("tools", "agent")
        
        return workflow.compile()
    
    def _call_model(self, state: AgentState):
        messages = state["messages"]
        response = self.llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def _should_continue(self, state: AgentState):
        messages = state["messages"]
        last_message = messages[-1]
        
        if last_message.tool_calls:
            return "continue"
        return "end"
    
    async def stream_chat(self, user_message: str, history: list[dict]):
        """
        流式聊天，实时返回 Agent 的思考过程和工具调用
        
        Args:
            user_message: 用户消息
            history: 历史消息
            
        Yields:
            Agent 思考步骤、工具调用、工具返回、最终回答
        """
        messages = []
        
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        
        messages.append(HumanMessage(content=user_message))
        
        state = {"messages": messages}
        
        all_messages = list(messages)
        
        async for event in self.graph.astream(state):
            for node_name, node_output in event.items():
                print(f"\n[节点执行] {node_name}")
                
                if node_name == "agent":
                    for message in node_output.get("messages", []):
                        all_messages.append(message)
                        if isinstance(message, AIMessage):
                            if message.content:
                                print(f"[思考] {message.content}")
                                yield {
                                    "type": "thought",
                                    "content": message.content
                                }
                            
                            if message.tool_calls:
                                for tool_call in message.tool_calls:
                                    print(f"[工具调用] {tool_call['name']}")
                                    print(f"[工具入参] {tool_call['args']}")
                                    yield {
                                        "type": "tool_call",
                                        "tool_name": tool_call["name"],
                                        "tool_input": tool_call["args"]
                                    }
                
                elif node_name == "tools":
                    for message in node_output.get("messages", []):
                        all_messages.append(message)
                        if isinstance(message, ToolMessage):
                            print(f"[工具返回] {message.content}")
                            yield {
                                "type": "tool_result",
                                "tool_output": message.content
                            }
        
        final_answer = ""
        
        for msg in reversed(all_messages):
            if isinstance(msg, AIMessage) and not msg.tool_calls:
                if msg.content:
                    final_answer = msg.content
                    break
        
        if final_answer:
            print(f"[最终回答] {final_answer}")
            yield {
                "type": "final_answer",
                "content": final_answer
            }
        
        yield {"type": "done"}


def create_agent_engine():
    return AgentEngine()
