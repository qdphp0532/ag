"""Agent 相关请求/响应模型。"""
from pydantic import BaseModel, Field


class InvokeRequest(BaseModel):
    query: str = Field(..., description="用户问题", min_length=1)


class InvokeResponse(BaseModel):
    answer: str = Field(..., description="最终回答")
    route: str = Field(..., description="实际执行路径: general | retrieval | tool")
    docs: list[str] = Field(default_factory=list, description="若使用检索工具，返回命中的文档片段")
