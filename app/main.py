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
    from app.agents.agent import get_agent
    from app.domain import models  # noqa: F401  # 注册表到 Base.metadata
    from app.db import init_db, dispose_db
    get_agent()
    init_db()
    yield
    dispose_db()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="LangChain Agent API",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    setup_exception_handlers(app)
    app.include_router(api_router)
    return app


app = create_app()
