from typing import TypedDict

class Skill(TypedDict):
    """ 技能定义 """
    name: str  # 技能名称
    description: str  # 技能描述
    content: str  # 技能内容
