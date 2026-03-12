"""检索类工具：知识库、文档等。实现与 @tool 同文件，避免与 agents/retrieval 重复。"""
import json

from langchain_core.tools import tool


def retriever(query: str) -> list[str]:
    """根据 query 返回文档片段。可替换为向量库、ES 等。"""
    # 示例数据；与 main.py 一致
    return ["Harrison worked at Kensho"]


@tool
def retrieve_documents(query: str) -> str:
    """从内部知识库检索与问题相关的文档片段。

    当用户问的是关于具体事实的问题（例如某人是谁、在哪里工作、发生了什么）
    时，应优先调用此工具获取文档后再回答。

    Args:
        query: 用户的原始问题或关键词
    """
    docs = retriever(query)
    return json.dumps(docs, ensure_ascii=False)
