from pydantic import BaseModel


class ChatbotParams(BaseModel):
    session_id: str
    query: str