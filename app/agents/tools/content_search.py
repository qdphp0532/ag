"""调用 ai 应用研究院内容库检索工具方法。"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# 直接执行本文件时（非 python -m），Python 默认不把仓库根目录加入 sys.path，会导致 No module named 'app'
if __name__ == "__main__":
    _repo_root = Path(__file__).resolve().parents[3]
    if str(_repo_root) not in sys.path:
        sys.path.insert(0, str(_repo_root))

import httpx
from langchain_core.tools import tool
from pydantic import ValidationError

from app.config import get_settings
from app.domain.content_search_schemas import ContentSearchApiResponse

@tool("content_search",description="联网内容检索：评测、口碑、新闻稿、电商讨论等事实型素材。")
def content_search(query: str, limit: int = 10) -> dict[str, Any]:
    """联网内容检索：评测、口碑、新闻稿、电商讨论等事实型素材。

    何时调用：用户问具体商品/品类好不好、值不值得买、对比、口碑、翻车、续航拍照等
    需要站外或库内文章支撑时，必须先调用本工具再作答；不要凭想象写评测细节。

    query 写法：只传简短检索词（如「荣耀 Magic7 评测」「2025 折叠屏 口碑」），
    不要把整段用户原话粘贴进来；可包含品牌+型号+场景。需要多角度时可分两次调用不同关键词。

    何时不要调用：纯打招呼、仅问现在几点、与商品/消费无关的闲聊、或用户明确只要
    数据库里 demo 示例表内容（那种用 query_examples / list_db_tables）。

    Args:
        query: 2–12 字左右的搜索关键词（中文为主）
        limit: 召回条数，默认 10，最大建议别超过 20

    Returns:
        字典含 items[].title / context 等字段；请基于这些片段归纳回答并注明信息来源倾向。
    """
    url = "https://gw-openapi.zhidemai.com/univeral_search"
    api_key = get_settings().AI_APPLICATION_X_API_KEY
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
    }
    request_data = {
        "query": query,
        "ranker_advanced": True,
        "request_from": "zhangdama_demo_test",
        "time_range": "OneMonth",
        "recall_num": int(limit),
        "rewrite": False,
    }
    try:
        response = httpx.post(url, headers=headers, json=request_data, timeout=30.0)
        response.raise_for_status()
        raw: Any = response.json()
        try:
            parsed = ContentSearchApiResponse.model_validate(raw)
            return parsed.model_dump()
        except ValidationError as e:
            return {
                "error": "content_search_response_validation_failed",
                "message": str(e),
                "query": query,
            }
    except httpx.HTTPStatusError as e:
        raise Exception(f"HTTP error occurred: {e}") from e
    except Exception as e:
        raise Exception(f"An error occurred: {e}") from e


if __name__ == "__main__":
    query = "最新发布的手机评价"
    # @tool 装饰后得到 StructuredTool，不能当普通函数调用，需 .invoke({"参数名": 值})
    result = content_search.invoke({"query": query})
    print(result)
