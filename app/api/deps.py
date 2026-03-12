"""
FastAPI 依赖注入：配置与 Agent 实例。
"""
from typing import Annotated

from fastapi import Depends

from app.config import Settings, get_settings
from app.agents.agent import get_agent


def get_config() -> Settings:
    return get_settings()


def get_compiled_agent():
    """返回 LangChain Agent 单例。"""
    return get_agent()


# 类型别名，便于路由中注解
ConfigDep = Annotated[Settings, Depends(get_config)]
AgentDep = Annotated[object, Depends(get_compiled_agent)]
