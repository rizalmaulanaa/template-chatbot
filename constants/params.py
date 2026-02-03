from typing import TypedDict, Literal
from pydantic import BaseModel, Field
from langgraph.graph import MessagesState

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

class GradeDocuments(BaseModel):  
    """Grade documents using a binary score for relevance check."""
    binary_score: str = Field(
        description="Relevance score: 'yes' if relevant, or 'no' if not relevant"
    )

class RAGState(MessagesState):
    query: str
    retrieved_docs: list[str]
    final_answer: str
    iteration_count: int