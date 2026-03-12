"""pytest 公共 fixture：TestClient、覆盖配置等。"""
import os

import pytest
from fastapi.testclient import TestClient

# 测试时避免真实 API 调用（可选：mock 或使用 test key）
os.environ.setdefault("OPENAI_API_KEY", "test-key-not-used")

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
