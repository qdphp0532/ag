"""
会话管理：Session 工厂与 get_session 上下文。
供路由、领域层仓库等使用，不包含业务模型。
"""
from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session, sessionmaker

from app.db.engine import get_engine


def get_session_factory() -> sessionmaker[Session]:
    """返回绑定当前引擎的 Session 工厂。"""
    return sessionmaker(
        bind=get_engine(),
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """供调用方使用的会话上下文：提交成功即 commit，异常则 rollback。"""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
