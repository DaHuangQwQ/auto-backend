from langchain_core.prompts import ChatPromptTemplate

db_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a helpful assistant.
            """,
        ),
        ("placeholder", "{messages}"),
    ]
)

# db_prompt.pretty_print()


# 创建一个计划生成的提示模版
plan_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
你是一个 web 程序，要求严格按照程序的运行步骤，
对于给定的目标，提出一个简单的逐步计划。
这个计划应该包含独立的任务，如果正确执行讲得出正确的答案。
不要添加任何多余的步骤。
最后一步的结果应该是最终答案。
确保每一步都有所有必要的信息 - 不要跳过步骤。
            """,
        ),
        ("placeholder", "{messages}"),
    ]
)


# 重新计划的提示次模版
replanner_prompt = ChatPromptTemplate.from_template("""
对于给定的目标，提出一个简单的逐步计划。
这个计划应该包含独立的任务，如果正确执行讲得出正确的答案。
不要添加任何多余的步骤。
最后一步的结果应该是最终答案。
确保每一步都有所有必要的信息 - 不要跳过步骤。

你的目标是：
{input}

你的原计划是：
{plan}

你目前已完成的步骤是：
{past_steps}

相应地更新你的计划。
如果不需要更多步骤并且可以返回给用户，那么就这样回应。
如果需要，填写计划。
只添加仍然需要完成的步骤。不要返回己完成的步骤作为计划的一部分。
""")
