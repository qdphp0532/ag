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
    """列出当前数据库中的表名。用于了解有哪些表可查询。

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
    """查询 examples 表示例数据。用于回答与示例记录相关的问题。

    Args:
        limit: 最多返回条数，默认 10
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
