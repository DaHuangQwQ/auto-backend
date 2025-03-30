from typing import Literal

from langchain_core.language_models import BaseChatModel
from langgraph.constants import START
from langgraph.graph import StateGraph
from langgraph.prebuilt import create_react_agent

from packages.tools import db_tool
from packages.tools.plan import Plan, PlanExecute
from packages.tools.replan import Act, Res
from packages.tools.types import db_prompt, plan_prompt, replanner_prompt

tools = [db_tool]


async def workflow(llm: BaseChatModel):
    agent_executor = create_react_agent(llm, tools, prompt=db_prompt)

    # 创建一个计划生成器，结构化输出
    planner = plan_prompt | llm.with_structured_output(Plan)

    replanner = replanner_prompt | llm.with_structured_output(Act)

    async def plan_step(state: PlanExecute):
        plan = await planner.ainvoke({"messages": [("user", state["input"])]})
        return {"plan": plan.steps}

    # 用于执行步骤
    async def execute_step(state: PlanExecute):
        plan = state["plan"]
        plan_str = "\n".join(f"{i + 1}. {step}" for i, step in enumerate(plan))
        task = plan[0]
        task_format = f"""
对于以下计划：
{plan_str}\n\n你的任务是执行第{1}步，{task}。
    """
        agent_res = await agent_executor.ainvoke({"messages": [("user", task_format)]})
        return {
            "past_steps": state["past_steps"]
            + [(task, agent_res["messages"][-1].content)]
        }

    # 用于重新计划步骤
    async def replan_step(state: PlanExecute):
        res = await replanner.ainvoke(state)
        if isinstance(res.action, Res):
            return {"res": res.action.res}
        else:
            return {"plan": res.action.steps}

    # 用于判断是否结束
    def should_end(state: PlanExecute) -> Literal["agent", "__end__"]:
        if "res" in state and state["res"]:
            return "__end__"
        else:
            return "agent"

    workflow = StateGraph(PlanExecute)

    workflow.add_node("planner", plan_step)
    workflow.add_node("agent", execute_step)
    workflow.add_node("replan", replan_step)

    workflow.add_edge(START, "planner")
    workflow.add_edge("planner", "agent")
    workflow.add_edge("agent", "replan")
    workflow.add_conditional_edges("replan", should_end)

    app = workflow.compile()
    # graph_image = app.get_graph().draw_mermaid_png()
    # with open("langsmith_demo.png", "wb") as f:
    #     f.write(graph_image)

    config = {"recursion_limit": 50}

    inputs = {
        "input": """
{
    "describe": "查询用户信息",
    "data": {
            "id": 1
        }
}
    """
    }

    async for event in app.astream(inputs, config=config):
        for k, v in event.items():
            if k != "__end__":
                print(v)
