from typing import List

from constants.config import USED_MIDDLEWARE
from services.middlewares.mapping_middleware import MAPPING_MIDDLEWARE


def get_middlewares(tools_names: List[str]) -> List:
    middlewares = []

    for middleware in USED_MIDDLEWARE:
        func_middleware = MAPPING_MIDDLEWARE[middleware]

        if 'hitl' == middleware:
            temp_hitl = func_middleware(tools_names)
            if temp_hitl:
                middlewares.append(temp_hitl)
        else:
            middlewares.append(func_middleware)

    return middlewares