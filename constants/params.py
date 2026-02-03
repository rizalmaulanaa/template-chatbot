from typing import TypedDict, List, Literal
from pydantic import BaseModel, Field


class ChatbotParams(BaseModel):
    session_id: str
    query: str

class Skill(TypedDict):
    name: str
    description: str
    content: str

class ParsingOutput(BaseModel):
    """Individual message component in the response"""
    type: Literal["info", "success", "error", "warning", "data"] = Field(
        description="Type of message being returned"
    )
    message: str = Field(
        description="The actual message content or data to display"
    )