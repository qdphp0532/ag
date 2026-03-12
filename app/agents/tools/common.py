"""通用小工具：测试、回显等。"""
from langchain_core.tools import tool


@tool
def echo(text: str) -> str:
    """原样返回用户输入，用于测试或重复用户内容。

    Args:
        text: 任意文本
    """
    return text
