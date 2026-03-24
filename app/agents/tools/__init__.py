"""
Agent 工具包：按领域分文件，在此统一注册。
- 各子模块定义 @tool，本文件汇总为 AGENT_TOOLS，供 Agent 绑定与按名分发。
- 对外保持 from app.agents.tools import get_agent_tools, get_tools_by_name, retrieve_documents，content_search 等不变。
"""
from langchain_core.tools import BaseTool

from app.agents.tools.retrieval import retrieve_documents, retriever
from app.agents.tools.time_tools import get_current_time
from app.agents.tools.common import echo
from app.agents.tools.db import list_db_tables, query_examples
from app.agents.tools.content_search import content_search
from app.agents.tools.goods_search import goods_search


# -----------------------------------------------------------------------------
# 统一注册：新增工具时在此加入列表即可
# -----------------------------------------------------------------------------

# 顺序影响模型「先看到谁」：主业务工具放最前，演示/少用工具靠后
AGENT_TOOLS: list[BaseTool] = [
    content_search,
    goods_search,
    get_current_time,
    #list_db_tables,
    #query_examples,
    #echo,
]


def get_tools_by_name() -> dict[str, BaseTool]:
    """工具名 -> 工具实例，供 Agent 循环按 name 调用。"""
    return {t.name: t for t in AGENT_TOOLS}


def get_agent_tools() -> list[BaseTool]:
    """返回当前提供给 Agent 的工具列表（用于 bind_tools）。"""
    return AGENT_TOOLS.copy()


__all__ = [
    "AGENT_TOOLS",
    "get_agent_tools",
    "get_tools_by_name",
    #"retrieve_documents",
    #"retriever",
    "get_current_time",
    #"echo",
    #   "list_db_tables",
    #"query_examples",
    "content_search",
    "goods_search",
]
