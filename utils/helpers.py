from typing import Any, Dict, List

def convert_openai_tools(
    tools: List[Dict[str, Any]], 
    list_tool_available: List[str]
) -> List[Dict[str, Any]]:
    used_tools = []

    for tool in tools:
        if tool.name in list_tool_available:
            temp = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                }
            }
            used_tools.append(temp)

    return used_tools

def parse_response(response):
    result = {
       "final_answer": response.get("final_answer"),
       "retrieved_data": response.get("retrieved_data"),
    }
    return result