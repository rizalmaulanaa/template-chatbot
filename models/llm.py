import os

from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek


def get_model():
    llm = ChatDeepSeek(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        model=os.getenv("DEEPSEEK_MODEL_NAME"),
        base_url=os.getenv("DEEPSEEK_BASE_URL"),
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
    return llm

def get_model_openai():
    llm = ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        model=os.getenv("OPENAI_MODEL_NAME"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
    return llm