from typing import Dict, Any, List
from langchain_core.tools import tool
from ..rag.rag_manager import RAGManager
from ..agent.skills import SKILLS



_rag_manager = None


def get_rag_manager():
    """获取RAG管理器实例（单例模式）"""
    global _rag_manager
    if _rag_manager is None:
        _rag_manager = RAGManager()
    return _rag_manager


@tool
def search_order(order_id: str) -> Dict[str, Any]:
    """
    根据订单号搜索订单信息
    
    Args:
        order_id: 订单号
        
    Returns:
        订单信息字典
    """
    print(f"[工具调用] 搜索订单: {order_id}")

    # 模拟1-5秒延迟延迟
    import time
    import random
    time.sleep(random.uniform(1, 5))
    
    mock_orders = {
        "123456": {
            "order_id": "123456",
            "amount": 1000.00,
            "status": "已支付",
            "items": ["商品A", "商品B"],
            "create_time": "2024-01-01 10:00:00"
        },
        "789012": {
            "order_id": "789012",
            "amount": 2500.00,
            "status": "待支付",
            "items": ["商品C", "商品D", "商品E"],
            "create_time": "2024-01-02 14:30:00"
        }
    }
    
    return mock_orders.get(order_id, {
        "order_id": order_id,
        "amount": 0.00,
        "status": "未找到",
        "items": [],
        "create_time": ""
    })


@tool
def calculator(expression: str) -> float:
    """
    计算数学表达式
    
    Args:
        expression: 数学表达式，如 "100 * 0.9" 或 "1000 * 0.9"
        
    Returns:
        计算结果
    """
    print(f"[工具调用] 计算表达式: {expression}")
    
    try:
        result = eval(expression)
        return float(result)
    except Exception as e:
        print(f"[计算错误] {e}")
        return 0.0


@tool
def rag_search(query: str) -> str:
    """
    检索企业内部知识库
    
    Args:
        query: 查询问题，如"公司的请假制度是什么？"
        
    Returns:
        检索到的相关文档内容
    """
    print(f"[工具调用] RAG检索: {query}")
    
    import time
    max_retries = 3
    last_error = None
    
    for attempt in range(max_retries):
        try:
            rag_manager = get_rag_manager()
            results = rag_manager.search(query, n_results=5)  # 增加结果数量，提高召回率
            
            if not results:
                return "未在知识库中找到相关内容"
            
            formatted_results = []
            for i, result in enumerate(results, 1):
                formatted_results.append(
                    f"[相关内容 {i}] 来源: {result['source']}\n"
                    f"{result['content']}"
                )
            
            return "\n\n".join(formatted_results)
        except Exception as e:
            last_error = e
            print(f"[RAG检索错误] 尝试 {attempt + 1}/{max_retries}: {e}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 指数退避: 1s, 2s
                print(f"[RAG检索] 等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
    
    return f"检索失败: {str(last_error)}"


@tool
def load_skill(skill_name: str) -> str:
    """
    加载指定技能的详细内容。
    当你需要关于如何处理特定类型请求的详细信息时，请使用此工具。它将为你提供该技能领域的全面说明和使用指导方针。
    
    Args:
        skill_name: 技能名称
        
    Returns:
        技能详细描述
    """
    print(f"[工具调用] 加载技能: {skill_name}")
    
    for skill in SKILLS:
        if skill["name"] == skill_name:
            return f"Loaded skill: {skill_name}\n\n{skill['content']}"

    # Skill not found
    available = ", ".join(s["name"] for s in SKILLS)
    return f"Skill '{skill_name}' not found. Available skills: {available}"


def get_tools():
    """
    获取所有可用工具
    
    Returns:
        工具列表
    """
    return [search_order, calculator, rag_search]
