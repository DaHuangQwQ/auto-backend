from typing import Literal

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode


def ai_agent(llm: BaseChatModel):
    @tool
    def search(query: str):
        """Query the database based on the SQL statement."""
        return query

    tools = [search]

    # 工具节点
    tool_node = ToolNode(tools)

    model = llm.bind_tools(tools)

    def should_continue(state: MessagesState) -> Literal["tools", END]:
        msgs = state["messages"]
        last_msg = msgs[-1]
        # 如果 LLM 调用了工具，则转到 tools 节点
        if last_msg.tool_calls:
            return "tools"
        return END

    def call_model(state: MessagesState):
        msgs = state["messages"]
        res = model.invoke(msgs)
        return {"messages": [res]}

    # 用状态初始化图，定义一个新的图
    workflow = StateGraph(MessagesState)

    # 定义图的节点
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)

    # 定义入口
    workflow.set_entry_point("agent")
    # 定义条件边
    workflow.add_conditional_edges(
        # 在调用 agent 节点后采取
        "agent",
        # 决定下一个节点调用的函数
        should_continue,
    )

    # 添加 agent 到 tools 的普通边，这意味着调用 tools 后，立刻调用 agent 节点
    workflow.add_edge("tools", "agent")

    # 初始化内存，在图运行之间持久化状态
    checkpointer = MemorySaver()

    # 编译图
    # 编译成 langchain 可运行对象
    app = workflow.compile(checkpointer=checkpointer)

    # 执行图
    res = app.invoke(
        {
            "messages": [
                HumanMessage(
                    content="""
{
    "describe": "查询用户信息",
    "data": {
            "id": 1
        }
}
"""
                )
            ]
        },
        config={"configurable": {"thread_id": 42}},
    )

    print(res["messages"][-1].content)

    # graph_image = app.get_graph().draw_mermaid_png()
    # with open("HelloWorld.png", "wb") as f:
    #     f.write(graph_image)
