"""内容检索第三方 API 的响应结构（Pydantic 校验与文档化）。"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ContentSearchItem(BaseModel):
    """单条检索结果。"""

    model_config = ConfigDict(extra="ignore")

    title: str = ""
    context: str = ""
    article_link: str = ""
    source: str = ""
    publish_time: str = ""
    icon: str = ""
    images: list[Any] = Field(default_factory=list)
    type: str = ""


class ContentSearchApiResponse(BaseModel):
    """univeral_search 接口整体响应。"""

    model_config = ConfigDict(extra="ignore")

    requestid: str = ""
    query: str = ""
    search_time: str = ""
    search_num: int = 0
    request_from: str = ""
    items: list[ContentSearchItem] = Field(default_factory=list)
