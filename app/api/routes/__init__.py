"""聚合所有 API 路由。"""
from fastapi import APIRouter

from app.api.routes import health, agents

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(agents.router)
