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
from constants.config import LANGFUSE_HANDLER


multi_agent_router = APIRouter(
    tags=["MULTI AGENT ENDPOINT"],
    responses={404: {"description": "Not found"}},
    prefix="/multi-agent"
)

def get_supervisor_agent(request: Request) -> CompiledStateGraph:
    """Dependency to get tools from app context"""
    if not hasattr(request.app, 'context') or 'supervisor_agent' not in request.app.context:
        raise HTTPException(
            status_code=503,
            detail="Tools not available"
        )
    return request.app.context['supervisor_agent']

@multi_agent_router.post("/generate-answer")
async def generate_answer(
    payload: ChatbotParams,
    supervisor_agent: CompiledStateGraph = Depends(get_supervisor_agent)
) -> Dict[str, Any]:
    run_id = str(uuid.uuid4())
    
    try:
        config = {
            "configurable": {
                "thread_id": payload.session_id,
            },
            "run_name": f"{payload.session_id}_{run_id}",
            "run_id": run_id,
            "callbacks": [LANGFUSE_HANDLER],
        }

        response = await supervisor_agent.ainvoke(
            {"messages": [{"role": "user", "content": payload.query}]},
            config=config
        )
        
        # Check if there's an interrupt
        interrupts = response.get('__interrupt__', [])
        
        # Get the final AI message
        final_ai_message = next(
            (msg for msg in reversed(response["messages"]) if isinstance(msg, AIMessage)),
            None
        )
        
        if interrupts:
            interrupt_data = interrupts[0].value
            action_requests = interrupt_data.get('action_requests', [])
            
            # Get the action details
            action = action_requests[0] if action_requests else {}
            
            return {
                "status": "interrupted",
                "data": {
                    "final_answer": final_ai_message.content,
                    "message": f"About to execute: {action.get('name')}",
                    "description": action.get('description'),
                    "tool_name": action.get('name'),
                    "tool_args": action.get('args'),
                    "session_id": payload.session_id,
                    "requires_approval": True
                }
            }
        
        if not final_ai_message:
            return {
                "status": "error",
                "data": {"final_answer": "No AI response found"}
            }
                    
        return {
            "status": "success",
            "data": {"final_answer": final_ai_message.content}
        }
    except Exception as e:
        LOGGER.error(f"Error in generate_answer: {e}", exc_info=True)
        return {
            "status": "error",
            "data": {"final_answer": f"Found error with {e}"}
        }
        
@multi_agent_router.post("/continue-answer")
async def continue_answer(
    payload: ChatbotParams,
    supervisor_agent: CompiledStateGraph = Depends(get_supervisor_agent)
) -> Dict[str, Any]:
    run_id = str(uuid.uuid4())
    
    try:
        config = {
            "configurable": {
                "thread_id": payload.session_id,
            },
            "run_name" : f"{payload.session_id}_{run_id}",
            "run_id" : run_id,
            "callbacks" : [LANGFUSE_HANDLER],
        }

        response = await supervisor_agent.ainvoke(
            Command( 
                resume={"decisions": [{"type": payload.query}]}
            ), 
            config=config
        )
         
        final_ai_message = next(
            msg for msg in reversed(response["messages"])
            if isinstance(msg, AIMessage)
        )
                    
        return {
            "status": "success",
            "data": {"final_answer": final_ai_message.content}
        }
    except Exception as e:
        return {
            "status": "error",
            "data": {"final_answer" : f"Found error with {e}"}
        }
        
async def chat_stream_generator(
    payload: ChatbotParams, 
    supervisor_agent: CompiledStateGraph
):
    run_id = str(uuid.uuid4())
    
    config = {
        "configurable": {
            "thread_id": payload.session_id,
        },
        "run_name": f"{payload.session_id}_{run_id}",
        "run_id": run_id,
        "callbacks": [LANGFUSE_HANDLER],
    }
    current_agent = None
    
    async for _, mode_stream, chunk in supervisor_agent.astream( 
        {"messages": [{"role": "user", "content": payload.query}]},
        config,
        stream_mode=["messages", "updates"],
        subgraphs=True,
    ):
        if mode_stream == "messages":
            message_chunk, metadata  = chunk
            if agent_name := metadata.get("lc_agent_name"):  
                if agent_name != current_agent:  
                    current_agent = agent_name
                    
            chunk_data = {
                "type": current_agent or metadata['langgraph_node'],
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
    supervisor_agent: CompiledStateGraph
):
    run_id = str(uuid.uuid4())
    
    config = {
        "configurable": {
            "thread_id": payload.session_id,
        },
        "run_name": f"{payload.session_id}_{run_id}",
        "run_id": run_id,
        "callbacks": [LANGFUSE_HANDLER],
    }
    current_agent = None
    
    async for _, mode_stream, chunk in supervisor_agent.astream( 
        Command( 
            resume={"decisions": [{"type": payload.query}]}
        ),
        config,
        stream_mode=["messages", "updates"],
        subgraphs=True,
    ):
        if mode_stream == "messages":
            message_chunk, metadata  = chunk
            if agent_name := metadata.get("lc_agent_name"):  
                if agent_name != current_agent:  
                    current_agent = agent_name
                    
            chunk_data = {
                "type": current_agent or metadata['langgraph_node'],
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
        
@multi_agent_router.post("/stream/generate-answer")
async def stream_generate_answer(
    payload: ChatbotParams,
    supervisor_agent: CompiledStateGraph = Depends(get_supervisor_agent)
) -> StreamingResponse:
    try:
        return StreamingResponse(
            chat_stream_generator(
                payload=payload,
                supervisor_agent=supervisor_agent
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
        
@multi_agent_router.post("/stream/continue-answer")
async def stream_continue_answer(
    payload: ChatbotParams,
    supervisor_agent: CompiledStateGraph = Depends(get_supervisor_agent)
) -> StreamingResponse:
    try:
        return StreamingResponse(
            continue_stream_generator(
                payload=payload,
                supervisor_agent=supervisor_agent
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