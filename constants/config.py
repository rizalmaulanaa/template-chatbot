import os
import json

from pathlib import Path
from langfuse.langchain import CallbackHandler

from constants.params import Skill
from utils.helpers import read_skill_md

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

PATH = (Path(__file__)).resolve()
PATH = '/'.join(str(PATH).split('/')[:-2])

MCP_CONFIG = all_env_variables(prefix="MCP_")
MCP_TOOLS = all_env_variables(prefix="MCP_TOOLS__")
MCP_TOOLS = {k: split_string(v) for k, v in MCP_TOOLS.items()}

MCP_SERVER_LIST = {
    "ticketing": {
        "transport": "sse",
        "url": MCP_CONFIG.get("SERVER_URL"), 
    }
}

MIDDLEWARE_LIST_TOOLS = {
    "create_ticket": "Create a new ticket in the ticketing system", 
    "update_ticket": "Update an existing ticket in the ticketing system",
    "delete_ticket": "Delete a ticket from the ticketing system",
}

LANGFUSE_HANDLER = CallbackHandler()

SKILLS = [
    {
        "name": "ticketing_system",
        "description": "Database schema and business logic for ticketing system including ticket management, priorities, and status tracking.",
    }
]

for skill in SKILLS:
    path_skill_md = f"{PATH}/services/skills/{skill['name']}.md"
    skill["content"] = read_skill_md(path_skill_md)