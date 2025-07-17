from langchain_openai import ChatOpenAI
from langchain_community.llms.tongyi import Tongyi
from init_env import *


def get_llm_deepseek(model="deepseek-chat", api_key=API_KEY_DEEPSEEK):
    llm = ChatOpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
        model=model
    )
    return llm


def get_llm_tongyi(model="qwen-plus-latest", api_key=API_KEY_DASHSCOPE):
    llm = Tongyi(
        api_key=api_key,
        model=model
    )
    return llm
