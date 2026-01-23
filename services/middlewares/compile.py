from typing import List
from langchain.agents.middleware import HumanInTheLoopMiddleware

from constants.config import MIDDLEWARE_LIST_TOOLS
from services.middlewares.skill import SkillMiddleware


def get_middlewares(
    tools_names: List[str],
    use_skill_middleware: bool = True,
) -> List:
    middlewares = []
    
    # Build interrupt_on config for all tools at once
    interrupt_on = {}
    description_parts = []
    
    for tool_name in tools_names:
        if tool_name in MIDDLEWARE_LIST_TOOLS:
            desc_tool = MIDDLEWARE_LIST_TOOLS.get(tool_name)
            
            # Add this tool to the interrupt config
            interrupt_on[tool_name] = True
            description_parts.append(f"{tool_name}: {desc_tool}")
    
    # Only create ONE middleware instance if we have any tools to monitor
    if interrupt_on:
        # Special case for execute_sql if needed
        if "execute_sql" in tools_names:
            interrupt_on["execute_sql"] = {"allowed_decisions": ["approve", "reject"]}
        
        # Combine descriptions
        description_prefix = "\n".join(description_parts)
        
        temp = HumanInTheLoopMiddleware(
            interrupt_on=interrupt_on,
            description_prefix=description_prefix,
        )
        
        middlewares.append(temp)
        
    if use_skill_middleware:
        middlewares.append(SkillMiddleware())
            
    return middlewares