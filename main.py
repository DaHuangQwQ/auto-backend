import asyncio

from packages.utils.deepseek import chatDeepSeek
from packages.workflow import workflow

if __name__ == "__main__":
    asyncio.run(workflow(chatDeepSeek))
