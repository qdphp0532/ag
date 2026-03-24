"""Agent 可调用的数据库工具（只读、安全）。"""
import json

from langchain_core.tools import tool

from app.config import get_settings
from app.db.engine import get_engine
from app.db.session import get_session
from app.domain.repositories import ExampleRepo


def _db_available() -> bool:
    url = get_settings().database_url
    return bool(url and not url.startswith("sqlite:///:memory:"))


@tool
def list_db_tables() -> str:
    """列出当前连接数据库中的表名（开发/演示用）。

    仅在用户明确问「有哪些表」「数据库结构」「demo 库」时使用。
    不要用于商品推荐、评测、百科类问题。

    无需参数。返回表名列表的 JSON 字符串。
    """
    if not _db_available():
        return json.dumps({"error": "database not configured"})
    try:
        from sqlalchemy import inspect
        engine = get_engine()
        insp = inspect(engine)
        tables = insp.get_table_names()
        return json.dumps(tables, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def query_examples(limit: int = 10) -> str:
    """读取 examples 表的演示数据（id/title/content）。

    仅在用户明确问示例表、Example 记录、本项目的 demo 数据时使用。
    不要用于任何商品、新闻、评测类咨询（那些应使用 content_search）。

    Args:
        limit: 最多返回条数，默认 10，最大 50
    """
    if not _db_available():
        return json.dumps({"error": "database not configured"})
    try:
        with get_session() as session:
            items = ExampleRepo.list_all(session, limit=min(limit, 50))
        data = [{"id": r.id, "title": r.title, "content": r.content} for r in items]
        return json.dumps(data, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})
