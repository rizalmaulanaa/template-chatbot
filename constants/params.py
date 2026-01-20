from pydantic import BaseModel
from langgraph.graph import MessagesState


class ChatbotParams(BaseModel):
    session_id: str
    query: str

class ChatbotState(MessagesState):
    query: str