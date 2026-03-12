"""
使用 LangChain 框架实现的 Agent：LLM + bind_tools 与手写工具循环。
不依赖 create_agent / LangGraph，仅使用 langchain_core + langchain_openai。
"""
import json
from functools import lru_cache

from langchain_openai import ChatOpenAI
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    ToolMessage,
    SystemMessage,
)

from app.config import get_settings
from app.agents.tools import get_agent_tools, get_tools_by_name

SYSTEM_PROMPT = (
    "You are a helpful assistant. When the user asks about specific facts "
    "(e.g. who, where, what, when), use the retrieve_documents tool first to "
    "get relevant passages, then answer based only on that information. "
    "For time/date questions use get_current_time. For general questions you may answer directly without calling tools."
)

RECURSION_LIMIT = 10


def _run_agent_loop(query: str) -> dict:
    """执行 Agent 循环：LLM + 工具调用直到无 tool_calls。"""
    settings = get_settings()
    tools = get_agent_tools()
    tools_by_name = get_tools_by_name()
    llm = ChatOpenAI(**settings.llm_kwargs()).bind_tools(tools)

    messages: list = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=query),
    ]
    for _ in range(RECURSION_LIMIT):
        response = llm.invoke(messages)
        if not getattr(response, "tool_calls", None):
            messages.append(response)
            return {"messages": messages}

        messages.append(response)
        for tc in response.tool_calls:
            tool_name = getattr(tc, "name", None) or (tc.get("name", "") if isinstance(tc, dict) else "")
            args = getattr(tc, "args", None) or (tc.get("args", {}) if isinstance(tc, dict) else {})
            tool_id = getattr(tc, "id", None) or (tc.get("id", "") if isinstance(tc, dict) else "")
            if tool_name in tools_by_name:
                result = tools_by_name[tool_name].invoke(args)
            else:
                result = f"Unknown tool: {tool_name}"
            messages.append(
                ToolMessage(content=result if isinstance(result, str) else json.dumps(result), tool_call_id=tool_id)
            )

    return {"messages": messages}


def invoke_agent(query: str, config: dict | None = None) -> dict:
    """对外接口：与 create_agent 的 invoke 返回格式一致，包含 messages。"""
    _ = config  # thread_id 等可在此扩展（如 checkpointer）
    return _run_agent_loop(query)


def parse_agent_result(messages: list) -> tuple[str, str, list[str]]:
    """从 agent 返回的 messages 中解析 answer、route、docs。"""
    answer = ""
    route = "general"
    docs: list[str] = []

    for msg in messages:
        if isinstance(msg, AIMessage):
            if msg.content:
                answer = msg.content if isinstance(msg.content, str) else str(msg.content)
        if isinstance(msg, ToolMessage):
            route = "rag"
            try:
                part = json.loads(msg.content)
                docs = part if isinstance(part, list) else [msg.content]
            except Exception:
                docs = [msg.content] if msg.content else []

    if not answer and messages:
        last = messages[-1]
        if hasattr(last, "content") and last.content:
            answer = last.content if isinstance(last.content, str) else str(last.content)

    return answer, route, docs


class _AgentAdapter:
    """兼容 FastAPI 依赖注入：提供 .invoke(inputs, config) 接口。"""

    def invoke(self, inputs: dict, config: dict | None = None) -> dict:
        messages_in = inputs.get("messages", [])
        content = messages_in[-1].content if messages_in else ""
        return invoke_agent(content, config=config)


@lru_cache
def get_agent() -> _AgentAdapter:
    """返回 Agent 适配器单例（进程内缓存）。"""
    return _AgentAdapter()
