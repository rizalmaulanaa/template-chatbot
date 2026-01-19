import uuid

from typing import Dict
from langchain.messages import HumanMessage, AIMessage, ToolMessage
from fastapi import APIRouter, HTTPException, Request, Depends

from constants.params import ChatbotParams
from services.agent_manager import make_graph_supervisor


multi_agent_router = APIRouter(
    tags=["MULTI AGENT ENDPOINT"],
    responses={404: {"description": "Not found"}},
    prefix="/multi-agent"
)

@multi_agent_router.post("/generate-answer")
async def generate_answer(
    payload: ChatbotParams
):
    run_id = str(uuid.uuid4())
    
    try:
        config = {
            "configurable": {
                "thread_id": payload.session_id,
            },
            "run_name" : f"{payload.session_id}_{run_id}",
            "run_id" : run_id,
        }
        
        chatbot_graph = await make_graph_supervisor()
        response = await chatbot_graph.ainvoke(
            {"messages": [{"role": "user", "content": payload.query}]},
            config=config
        )
        
        final_ai_message = next(
            msg for msg in reversed(response["messages"])
            if isinstance(msg, AIMessage)
        )
                    
        # response = parse_response(response)
        return {
            "status": "success",
            "data": final_ai_message.content
        }
    except Exception as e:
        return {
            "status": "error",
            "data": {"final_answer" : f"Found error with {e}"}
        }