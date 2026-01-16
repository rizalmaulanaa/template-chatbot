import os
from langchain_deepseek import ChatDeepSeek


def get_model():
    llm = ChatDeepSeek(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        model=os.getenv("DEEPSEEK_MODEL_NAME"),
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
    return llm