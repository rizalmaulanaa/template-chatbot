from typing import Any, Dict, List
from langchain_core.tools import StructuredTool


def split_agent_tools(
    tools: List[StructuredTool], 
    list_tool_available: List[str]
) -> List[StructuredTool]:
    used_tools = [tool for tool in tools if tool.name in list_tool_available]
    return used_tools