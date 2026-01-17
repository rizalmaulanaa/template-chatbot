import os
import json


def parse_value(value: str):
    """Try to parse string into Python type (int, float, bool, list, dict)."""
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value
    
def split_string(value: str, delimiter: str = ","):
    """Split a string by delimiter into a list."""
    return [item.strip() for item in value.split(delimiter) if item.strip()]

def all_env_variables(prefix: str = None):
    """
    Get all environment variables. 
    If prefix is provided, filter by it and strip the prefix from keys.
    """
    env_dict = dict(os.environ)
    if prefix:
        env_dict = {
            k[len(prefix):]: v  # strip prefix from key
            for k, v in env_dict.items()
            if k.startswith(prefix)
        }
    
    return {k: parse_value(v) for k, v in env_dict.items()}

MCP_CONFIG = all_env_variables(prefix="MCP_")
MCP_TOOLS = all_env_variables(prefix="MCP_TOOLS__")
MCP_TOOLS = {k: split_string(v) for k, v in MCP_TOOLS.items()}

MCP_SERVER_LIST = {
    "ticketing": {
        "transport": "sse",
        "url": MCP_CONFIG.get("SERVER_URL"), 
    }
}