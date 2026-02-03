import os

from langchain_deepseek import ChatDeepSeek
from langchain_google_genai import ChatGoogleGenerativeAI


def get_model() -> ChatGoogleGenerativeAI:
    llm = ChatGoogleGenerativeAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        model=os.getenv("GEMINI_MODEL_NAME"),
        temperature=0.4,
        top_k=32,
        top_p=1,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        streaming=True,
    )
    return llm

# def get_model() -> ChatDeepSeek:
#     llm = ChatDeepSeek(
#         api_key=os.getenv("DEEPSEEK_API_KEY"),
#         model=os.getenv("DEEPSEEK_MODEL_NAME"),
#         base_url=os.getenv("DEEPSEEK_BASE_URL"),
#         temperature=0,
#         max_tokens=None,
#         timeout=None,
#         max_retries=2,
#         streaming=True,
#     )
#     return llm