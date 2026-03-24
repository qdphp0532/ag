"""通用小工具：测试、回显等。"""
from langchain_core.tools import tool


@tool
def echo(text: str) -> str:
    """原样返回传入文本。仅在用户明确要求「复述一遍」「echo」等调试场景使用。

    正常问答、检索、推荐时不要调用。

    Args:
        text: 需要原样返回的文本
    """
    return text
