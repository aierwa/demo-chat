from langchain.agents.middleware import ModelRequest, ModelResponse, AgentMiddleware
from langchain.messages import SystemMessage
from typing import Callable
from ..agent.skills import SKILLS
from ..tools.tools import load_skill

class SkillMiddleware(AgentMiddleware):  
    """向系统提示注入技能描述的中间件。"""

    # 将 load_skill 工具注册为类变量
    tools = [load_skill]  

    def __init__(self):
        """从 SKILLS 初始化并生成技能提示。"""
        # 从 SKILLS 列表构建技能提示
        skills_list = []
        for skill in SKILLS:
            skills_list.append(
                f"- **{skill['name']}**: {skill['description']}"
            )
        self.skills_prompt = "\n".join(skills_list)

    def awrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        """同步：将技能描述注入系统提示。"""
            
        # 构建技能附录
        skills_addendum = ( 
            f"""
            当你需要处理特殊类型的请求时，请使用 load_skill 工具获取技能详细信息。
            可用技能: 
            {self.skills_prompt}
            """
        )

        # 追加到系统消息内容块
        # new_content = list(request.system_message.content_blocks) + [
        #     {"type": "text", "text": skills_addendum}
        # ]
        # new_system_message = SystemMessage(content_blocks=new_content) # 实测这个写法效果不好
        new_system_message = SystemMessage(content = request.system_message.content + skills_addendum)
        print(new_system_message)

        modified_request = request.override(system_message=new_system_message)
        return handler(modified_request)