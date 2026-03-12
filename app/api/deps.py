"""
FastAPI 依赖注入：配置、Agent 实例、工作流图等。
"""
from typing import Annotated

from fastapi import Depends

from app.config import Settings, get_settings
from app.agents.agent import get_agent
from app.agents.workflow_graph import get_workflow_graph


def get_config() -> Settings:
    return get_settings()


def get_compiled_agent():
    """返回 LangChain Agent 单例。"""
    return get_agent()


def get_compiled_workflow_graph():
    """返回 LangGraph 工作流图单例（混用时的图入口）。"""
    return get_workflow_graph()


# 类型别名，便于路由中注解
ConfigDep = Annotated[Settings, Depends(get_config)]
AgentDep = Annotated[object, Depends(get_compiled_agent)]
WorkflowGraphDep = Annotated[object, Depends(get_compiled_workflow_graph)]
