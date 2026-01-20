from typing import TypedDict
from pydantic import BaseModel
from langgraph.graph import MessagesState


class ChatbotParams(BaseModel):
    session_id: str
    query: str
    
class Skill(TypedDict):
    name: str
    description: str
    content: str