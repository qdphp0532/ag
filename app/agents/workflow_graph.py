"""
LangGraph 工作流骨架：多节点编排，节点内使用 LangChain 的 LLM 与检索。
与 agent.py（LangChain Agent）混用，复杂流程走本图，简单问答走 Agent。
"""
from functools import lru_cache
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.config import get_settings
from app.agents.tools.retrieval import retriever


class WorkflowState(TypedDict):
    query: str
    docs: list[str]
    answer: str


def _retrieve_node(state: WorkflowState) -> dict:
    """检索节点：使用 LangChain 侧的 retriever。"""
    docs = retriever(state["query"])
    return {"docs": docs}


def _respond_node(state: WorkflowState) -> dict:
    """回答节点：使用 LangChain 的 ChatOpenAI，基于检索结果生成答案。"""
    settings = get_settings()
    llm = ChatOpenAI(**settings.llm_kwargs())
    docs = state.get("docs") or []
    system = (
        "Answer the user's question using only the provided information below.\n"
        + "\n".join(docs)
    )
    msg = llm.invoke(
        [
            SystemMessage(content=system),
            HumanMessage(content=state["query"]),
        ]
    )
    content = msg.content if hasattr(msg, "content") else str(msg)
    return {"answer": content}


def _build_workflow_graph():
    builder = (
        StateGraph(WorkflowState)
        .add_node("retrieve", _retrieve_node)
        .add_node("respond", _respond_node)
        .add_edge(START, "retrieve")
        .add_edge("retrieve", "respond")
        .add_edge("respond", END)
    )
    return builder.compile()


@lru_cache
def get_workflow_graph():
    """返回 LangGraph 工作流图单例。"""
    return _build_workflow_graph()
