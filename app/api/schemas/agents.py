"""Agent 相关请求/响应模型。"""
from pydantic import BaseModel, Field


class InvokeRequest(BaseModel):
    query: str = Field(..., description="用户问题", min_length=1)
    thread_id: str | None = Field(None, description="会话 ID，用于持久化时区分会话")


class InvokeResponse(BaseModel):
    answer: str = Field(..., description="最终回答")
    route: str = Field(..., description="实际走的路由: rag | general")
    docs: list[str] = Field(default_factory=list, description="若走 RAG，返回引用文档")
