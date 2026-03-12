"""
应用入口：创建 FastAPI 应用、注册路由与生命周期。
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.core import setup_exception_handlers
from app.api.routes import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动：预加载 Agent 与工作流图（触发单例）
    from app.agents.agent import get_agent
    from app.agents.workflow_graph import get_workflow_graph
    get_agent()
    get_workflow_graph()
    yield
    # 关闭：可做连接池、缓存清理
    pass


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="LangChain Agent + FastAPI 包装",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    setup_exception_handlers(app)
    app.include_router(api_router)
    return app


app = create_app()
