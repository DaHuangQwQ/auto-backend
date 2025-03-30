from typing import Union

from pydantic import BaseModel, Field

from packages.tools.plan import Plan


class Res(BaseModel):
    """用户响应"""

    res: str


# 用户描述执行的行为
class Act(BaseModel):
    """要执行的行为"""

    action: Union[Res, Plan] = Field(
        description="要执行的行为。如果要回应用户，使用Res。如果需要进一步使用工具获取答案，使用Plan。"
    )
