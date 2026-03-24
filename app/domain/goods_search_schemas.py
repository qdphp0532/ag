"""商品搜索第三方 API 的请求/响应结构（与线上 rows 字段对齐，Pydantic 校验）。"""

from __future__ import annotations

import json
from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


def _str_or_empty(v: Any) -> str:
    if v is None:
        return ""
    return str(v)


def _pictures_field(v: Any) -> str | list[str]:
    if v is None or v == "":
        return ""
    if isinstance(v, list):
        return [_str_or_empty(x) for x in v]
    return _str_or_empty(v)


def _price_tags_field(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, (list, dict)):
        return json.dumps(v, ensure_ascii=False)
    return str(v)


SafeStr = Annotated[str, BeforeValidator(_str_or_empty)]
PicturesField = Annotated[str | list[str], BeforeValidator(_pictures_field)]
PriceTagsField = Annotated[str, BeforeValidator(_price_tags_field)]


class GoodsSearchApiRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    request_from: str = "zhangdama_demo_test"
    question_id: str = ""
    product_query: str = ""
    query_process: int = 0
    size: int = 20
    #mall_id: str = ""
    #brand_name: str = ""
    #category_name: str = ""
    #min_price: float = 0
    #max_price: float = 0
    #sort: str = ""
    #fields: str = ""


class GoodsSearchApiRow(BaseModel):
    """单条商品结果（与接口 `data.rows[]` 一致；部分字段接口可能用字符串承载数字或 JSON）。"""

    model_config = ConfigDict(extra="ignore")

    product_query: SafeStr = ""
    title: SafeStr = ""
    url: SafeStr = ""
    main_picture: SafeStr = ""
    pictures: PicturesField = ""
    page_price: SafeStr = ""
    price: SafeStr = ""
    promotional_info: SafeStr = ""
    sales_cnt: SafeStr = ""
    comment_cnt: SafeStr = ""
    good_comments_share: SafeStr = ""
    mall_id: SafeStr = ""
    mall_name: SafeStr = ""
    brand_id: SafeStr = ""
    brand_name: SafeStr = ""
    price_tags: PriceTagsField = ""
    shop_name: SafeStr = ""
    shop_type: SafeStr = ""
    shop_level: SafeStr = ""
    standard_month_sale_qty: SafeStr = ""
    score: SafeStr = ""
    #price_info_180_days: SafeStr = "" #数据太大，提供模型的时候忽略这个字段
    union_spec: SafeStr = ""
    WhiteImage: SafeStr = ""
    # 部分渠道/版本可能返回，demo 未出现，保留为可选
    original_url: SafeStr = ""
    cate1_name: SafeStr = ""
    cate2_name: SafeStr = ""
    cate3_name: SafeStr = ""

class GoodsSearchApiData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    rows: list[GoodsSearchApiRow] = Field(default_factory=list)


class GoodsSearchApiResponse(BaseModel):
    """商品搜索接口整体响应。"""

    model_config = ConfigDict(extra="ignore")

    error_code: int = 0
    error_msg: str = ""
    data: GoodsSearchApiData | None = None
