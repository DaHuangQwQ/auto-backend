import operator
from typing import Annotated, List, Tuple, TypedDict

from pydantic import BaseModel, Field


# 用于存储输入、计划、过去的步骤和响应
class PlanExecute(TypedDict):
    input: str
    # 每个计划
    plan: List[str]
    # 步骤执行的情况
    past_steps: Annotated[List[Tuple], operator.add]
    res: str


# 用于描述未来要执行的计划
class Plan(BaseModel):
    """未来要执行的计划"""

    steps: List[str] = Field(description="需要执行的不同步骤，应该按顺序排列")
