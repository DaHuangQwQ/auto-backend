from langchain_core.tools import tool


# db_prompt.pretty_print()
@tool
def db_tool(query: str):
    """Query the database based on the SQL statement."""

    return {"id": 1, "name": "DaHuang", "query": query}
