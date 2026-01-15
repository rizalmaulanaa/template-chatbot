import os
import json


def parse_value(value: str):
    """Try to parse string into Python type (int, float, bool, list, dict)."""
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value

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
    
    return {k.lower(): parse_value(v) for k, v in env_dict.items()}