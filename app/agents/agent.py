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
    "你是一个内容创作者，根据用户的问题，调用搜索工具进行内容获取,目前有 content_search工具进行内容搜索，goods_search工具进行商品搜索，你可以根据用户的问题，选择使用哪个工具进行搜索，进行内容分析，提取要点，并且改写，针对用户的 query 词，你需要自己评估分析可能需要搜索的关键词， 然后根据关键词 检索与问题相关的文档片段 ，根据返回的片段聚合内容结果创作一个吸引用户购买的短文，:\n"
)

user_prompt = "用户的问题是："


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
        {"messages": [{"role": "user", "content": user_prompt + query}]},
    )


def _tool_name(tool_call: Any) -> str:
    if isinstance(tool_call, dict):
        return str(tool_call.get("name", ""))
    return str(getattr(tool_call, "name", ""))


def parse_agent_result(messages: list[Any]) -> tuple[str, str, list[str]]:
    """从 agent 返回的 messages 中解析 answer、route、docs。"""
    #print(messages)
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
            if tool_name == "content_search":
                route = "content_search"
                raw = msg.content
                if raw:
                    part: Any = None
                    if isinstance(raw, str):
                        try:
                            part = json.loads(raw)
                        except Exception:
                            part = None
                    elif isinstance(raw, dict):
                        part = raw
                    if isinstance(part, dict) and part.get("items"):
                        docs = []
                        for it in part["items"]:
                            if not isinstance(it, dict):
                                continue
                            t = (it.get("title") or "").strip()
                            c = (it.get("context") or "").strip()
                            if t or c:
                                docs.append(f"{t}\n{c}".strip())
                    elif isinstance(part, list) and all(
                        isinstance(item, str) for item in part
                    ):
                        docs = part
                    elif raw:
                        docs = [raw if isinstance(raw, str) else json.dumps(part or raw, ensure_ascii=False)]
            elif tool_name == "goods_search":
                route = "goods_search"
                print(msg.content)
                raw = msg.content
                if raw:
                    try:
                        part = json.loads(raw) if isinstance(raw, str) else raw
                    except Exception:
                        part = None
                    if isinstance(part, list) and all(isinstance(item, str) for item in part):
                        docs = part
                    elif raw:
                        docs = [raw if isinstance(raw, str) else str(raw)]
            elif tool_name and route == "general":
                route = "tool"

    return answer, route, docs


@lru_cache
def get_agent():
    """返回统一的 agent 单例。"""
    return _build_agent()
