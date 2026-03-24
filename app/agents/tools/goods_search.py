"""调用 ai 研究院商品搜索接口。"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any
import uuid 

# 直接执行本文件时（非 python -m），Python 默认不把仓库根目录加入 sys.path，会导致 No module named 'app'
if __name__ == "__main__":
    _repo_root = Path(__file__).resolve().parents[3]
    if str(_repo_root) not in sys.path:
        sys.path.insert(0, str(_repo_root))

import httpx
from langchain_core.tools import tool
from pydantic import ValidationError

from app.config import get_settings
from app.domain.goods_search_schemas import GoodsSearchApiRequest, GoodsSearchApiResponse


@tool("goods_search",description="根据商品词进行商品搜索，返回各个电商平台的商品信息，包含标题，链接，图片，价格等内容。")
def goods_search(query: str, limit: int = 10) -> dict[str, Any]:
    """ 根据商品词进行商品搜索，返回各个电商平台的商品信息，包含标题，链接，图片，价格等内容。

    Args:
        query: 商品检索词（写入请求体 product_query）
        limit: 返回条数上限（写入请求体 size）
    """
    settings = get_settings()
    url = "https://gw-openapi.zhidemai.com/product/v1"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": settings.AI_APPLICATION_X_API_KEY,
    }
    # Pydantic 模型 → HTTP JSON：先构造实例，再 model_dump；不要用「类」当 body
    req = GoodsSearchApiRequest(product_query=query, size=min(int(limit), 10),request_from="zhangdama_demo_test",question_id="zy_demo_test",query_process=1)
 
    request_data = req.model_dump(mode="json")

    try:
        response = httpx.post(url, headers=headers, json=request_data, timeout=30.0)
        #print("response.json()",response.json())
        response.raise_for_status()
        raw: Any = response.json()
        try:
            parsed = GoodsSearchApiResponse.model_validate(raw)
            return parsed.model_dump()
        except ValidationError as e:
            return {
                "error": "goods_search_response_validation_failed",
                "message": str(e),
                "query": query,
            }
    except httpx.HTTPStatusError as e:
        raise Exception(f"HTTP error occurred: {e}") from e
    except Exception as e:
        raise Exception(f"An error occurred: {e}") from e


if __name__ == "__main__":
    result = goods_search.invoke({"query": "iPhone 16 Plus", "limit": 5})
    print(result)
