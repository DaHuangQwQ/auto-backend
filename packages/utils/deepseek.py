from langchain_deepseek import ChatDeepSeek

chatDeepSeek = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)
