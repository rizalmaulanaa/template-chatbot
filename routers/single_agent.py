import json
import uuid

from typing import Dict, Any
from langgraph.types import Command
from langchain.messages import AIMessage
from fastapi.responses import StreamingResponse
from langgraph.graph.state import CompiledStateGraph
from fastapi import APIRouter, HTTPException, Request, Depends

from constants.log import LOGGER
from constants.params import ChatbotParams
from utils.helpers import extract_agent_response


single_agent_router = APIRouter(
    tags=["SINGLE AGENT ENDPOINT"],
    responses={404: {"description": "Not found"}},
    prefix="/single-agent"
)

def get_single_agent(request: Request) -> CompiledStateGraph:
    """Dependency to get tools from app context"""
    if not hasattr(request.app, 'context') or 'single_agent' not in request.app.context:
        raise HTTPException(
            status_code=503,
            detail="Tools not available"
        )
    return request.app.context['single_agent']

@single_agent_router.post("/generate-answer")
async def generate_answer(
    payload: ChatbotParams,
    single_agent: CompiledStateGraph = Depends(get_single_agent)
) -> Dict[str, Any]:
    run_id = str(uuid.uuid4())
    
    try:
        config = {
            "configurable": {
                "thread_id": payload.session_id,
            },
            "run_name": f"{payload.session_id}_{run_id}",
            "run_id": run_id,
        }

        response = await single_agent.ainvoke(
            {"messages": [{"role": "user", "content": payload.query}]},
            config=config
        )

        # Extract and return the complete response
        return extract_agent_response(response, payload.session_id, run_id)
        
    except Exception as e:
        LOGGER.error(f"Error in generate_answer: {e}", exc_info=True)
        return {
            "status": "error",
            "data": {
                "requires_approval": False,
                "session_id": payload.session_id,
                "run_id": run_id,
                "error": str(e),
                "final_answer": "Internal server error: {str(e)}"
            }
        }
        
@single_agent_router.post("/continue-answer")
async def continue_answer(
    payload: ChatbotParams,
    single_agent: CompiledStateGraph = Depends(get_single_agent)
) -> Dict[str, Any]:
    run_id = str(uuid.uuid4())
    
    try:
        config = {
            "configurable": {
                "thread_id": payload.session_id,
            },
            "run_name" : f"{payload.session_id}_{run_id}",
            "run_id" : run_id,
        }

        response = await single_agent.ainvoke(
            Command( 
                resume={"decisions": [{"type": payload.query}]}
            ), 
            config=config
        )
         
        # Extract and return the complete response
        return extract_agent_response(response, payload.session_id, run_id)
        
    except Exception as e:
        LOGGER.error(f"Error in generate_answer: {e}", exc_info=True)
        return {
            "status": "error",
            "data": {
                "requires_approval": False,
                "session_id": payload.session_id,
                "run_id": run_id,
                "error": str(e),
                "final_answer": "Internal server error: {str(e)}"
            }
        }
        
async def chat_stream_generator(
    payload: ChatbotParams, 
    single_agent: CompiledStateGraph
):
    run_id = str(uuid.uuid4())
    
    config = {
        "configurable": {
            "thread_id": payload.session_id,
        },
        "run_name": f"{payload.session_id}_{run_id}",
        "run_id": run_id,
    }
    
    async for mode_stream, chunk in single_agent.astream( 
        {"messages": [{"role": "user", "content": payload.query}]},
        config,
        stream_mode=["messages", "updates"],
    ):
        if mode_stream == "messages":
            message_chunk, metadata  = chunk
            chunk_data = {
                "type": metadata['langgraph_node'],
                "content": message_chunk.content
            }
            yield f"data: {json.dumps(chunk_data)}\n\n" 
        else:
            if "__interrupt__" in chunk:
                chunk_data = {
                    "type": "interrupt",
                    "content": "interrupt received"
                }
                yield f"data: {json.dumps(chunk_data)}\n\n"
        
async def continue_stream_generator(
    payload: ChatbotParams, 
    single_agent: CompiledStateGraph
):
    run_id = str(uuid.uuid4())
    
    config = {
        "configurable": {
            "thread_id": payload.session_id,
        },
        "run_name": f"{payload.session_id}_{run_id}",
        "run_id": run_id,
    }
    
    async for mode_stream, chunk in single_agent.astream( 
        Command( 
            resume={"decisions": [{"type": payload.query}]}
        ),
        config,
        stream_mode=["messages", "updates"],
    ):
        if mode_stream == "messages":
            message_chunk, metadata  = chunk
            chunk_data = {
                "type": metadata['langgraph_node'],
                "content": message_chunk.content
            }
            yield f"data: {json.dumps(chunk_data)}\n\n" 
        else:
            if "__interrupt__" in chunk:
                chunk_data = {
                    "type": "interrupt",
                    "content": "interrupt received"
                }
                yield f"data: {json.dumps(chunk_data)}\n\n"
        
@single_agent_router.post("/stream/generate-answer")
async def stream_generate_answer(
    payload: ChatbotParams,
    single_agent: CompiledStateGraph = Depends(get_single_agent)
) -> StreamingResponse:
    try:
        return StreamingResponse(
            chat_stream_generator(
                payload=payload,
                single_agent=single_agent
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        ) 
    except Exception as e:
        return {
            "response" : f"Error found at system with message : {e}",
            "code" : "400"
        }
        
@single_agent_router.post("/stream/continue-answer")
async def stream_continue_answer(
    payload: ChatbotParams,
    single_agent: CompiledStateGraph = Depends(get_single_agent)
) -> StreamingResponse:
    try:
        return StreamingResponse(
            continue_stream_generator(
                payload=payload,
                single_agent=single_agent
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        ) 
    except Exception as e:
        return {
            "response" : f"Error found at system with message : {e}",
            "code" : "400"
        }