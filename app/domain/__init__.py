"""领域层：模型与仓库。"""
from app.domain.models import Example
from app.domain.repositories import ExampleRepo

__all__ = ["Example", "ExampleRepo"]
