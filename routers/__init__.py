from fastapi import APIRouter

from routers.multi_agent import multi_agent_router

all_router = APIRouter()

all_router.include_router(multi_agent_router)