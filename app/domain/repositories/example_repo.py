"""Example 实体的仓库：封装 CRUD，供 API 或工具调用。"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.models.example import Example


class ExampleRepo:
    @staticmethod
    def list_all(session: Session, limit: int = 50) -> list[Example]:
        stmt = select(Example).order_by(Example.id.desc()).limit(limit)
        return list(session.scalars(stmt).all())

    @staticmethod
    def get_by_id(session: Session, id: int) -> Example | None:
        return session.get(Example, id)

    @staticmethod
    def create(session: Session, *, title: str, content: str | None = None) -> Example:
        obj = Example(title=title, content=content)
        session.add(obj)
        session.flush()
        return obj
