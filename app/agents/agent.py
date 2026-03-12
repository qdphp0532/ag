"""统一的 LangChain agent 入口。"""
import json
from functools import lru_cache
from typing import Any

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, ToolMessage
from langchain_openai import ChatOpenAI

from app.agents.tools import get_agent_tools
from app.config import get_settings

SYSTEM_PROMPT = (
    "You are a helpful assistant. "
    "Use retrieve_documents before answering fact-based questions. "
    "Use get_current_time for current date or time questions. "
    "Use list_db_tables or query_examples for database questions. "
    "Answer directly when no tool is needed."
)


def _build_agent():
    settings = get_settings()
    model = ChatOpenAI(**settings.llm_kwargs())
    return create_agent(
        model=model,
        tools=get_agent_tools(),
        system_prompt=SYSTEM_PROMPT,
    )


def invoke_agent(query: str) -> dict[str, Any]:
    """同步调用 agent。"""
    return get_agent().invoke(
        {"messages": [{"role": "user", "content": query}]},
    )


def _tool_name(tool_call: Any) -> str:
    if isinstance(tool_call, dict):
        return str(tool_call.get("name", ""))
    return str(getattr(tool_call, "name", ""))


def parse_agent_result(messages: list[Any]) -> tuple[str, str, list[str]]:
    """从 agent 返回的 messages 中解析 answer、route、docs。"""
    answer = ""
    route = "general"
    docs: list[str] = []
    pending_tool_names: list[str] = []

    for msg in messages:
        if isinstance(msg, AIMessage):
            if msg.content:
                answer = msg.content if isinstance(msg.content, str) else str(msg.content)
            tool_calls = getattr(msg, "tool_calls", None) or []
            pending_tool_names.extend(_tool_name(tc) for tc in tool_calls)
            continue

        if isinstance(msg, ToolMessage):
            tool_name = pending_tool_names.pop(0) if pending_tool_names else ""
            if tool_name == "retrieve_documents":
                route = "retrieval"
                if msg.content:
                    try:
                        part = json.loads(msg.content)
                    except Exception:
                        part = None
                    if isinstance(part, list) and all(isinstance(item, str) for item in part):
                        docs = part
                    elif msg.content:
                        docs = [msg.content]
            elif tool_name and route == "general":
                route = "tool"

    return answer, route, docs


@lru_cache
def get_agent():
    """返回统一的 agent 单例。"""
    return _build_agent()
