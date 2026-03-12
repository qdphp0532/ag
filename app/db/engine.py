"""
数据库引擎与生命周期。
- 仅负责连接、建表（create_all）、释放连接池。
- 不包含模型与仓库；表结构由领域层模型注册到 Base.metadata。
"""
import os
from functools import lru_cache

from sqlalchemy import create_engine

from app.config import get_settings
from app.db.base import Base


def _make_engine():
    url = get_settings().database_url
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    kwargs = {"connect_args": connect_args, "echo": get_settings().debug}
    if url.startswith("mysql"):
        kwargs["pool_pre_ping"] = True
    return create_engine(url, **kwargs)


@lru_cache
def get_engine():
    """获取全局引擎单例。"""
    return _make_engine()


def init_db() -> None:
    """创建所有表（若不存在）。调用前需已导入领域层 models，使 Base.metadata 包含表定义。"""
    url = get_settings().database_url
    if url.startswith("sqlite"):
        path = url.replace("sqlite:///", "").split("?")[0]
        if path and path != ":memory:":
            d = os.path.dirname(path)
            if d:
                os.makedirs(d, exist_ok=True)
    Base.metadata.create_all(bind=get_engine())


def dispose_db() -> None:
    """释放引擎连接池。应在应用关闭时调用。"""
    get_engine().dispose()
