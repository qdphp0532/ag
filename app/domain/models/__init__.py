"""领域模型（表定义），依赖 app.db.base.Base。"""
from app.domain.models.example import Example  # noqa: F401

__all__ = ["Example"]
