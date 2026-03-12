"""健康检查与 invoke 路由的简单测试。"""
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") == "ok"


def test_invoke_requires_body(client: TestClient) -> None:
    r = client.post("/api/v1/invoke", json={})
    assert r.status_code == 422  # validation error, no query


@patch("app.api.deps.get_agent")
def test_invoke_returns_structure(mock_get_agent, client: TestClient) -> None:
    """Mock Agent 实例，invoke 返回带 messages 的结果，校验响应结构。"""
    from langchain_core.messages import AIMessage, ToolMessage

    mock_agent = MagicMock()
    mock_agent.invoke.return_value = {
        "messages": [
            ToolMessage(content='["Harrison worked at Kensho"]', tool_call_id="1"),
            AIMessage(content="Harrison worked at Kensho."),
        ]
    }
    mock_get_agent.return_value = mock_agent

    r = client.post(
        "/api/v1/invoke",
        json={"query": "Where did Harrison work?"},
    )
    assert r.status_code == 200
    assert r.headers.get("content-type", "").startswith("application/json")
    data = r.json()
    assert data["answer"] == "Harrison worked at Kensho."
    assert data["route"] == "rag"
    assert data["docs"] == ["Harrison worked at Kensho"]


@patch("app.api.deps.get_workflow_graph")
def test_workflow_returns_structure(mock_get_graph, client: TestClient) -> None:
    """Mock 工作流图，校验 /workflow 响应结构。"""
    mock_graph = MagicMock()
    mock_graph.invoke.return_value = {
        "answer": "Harrison worked at Kensho.",
        "docs": ["Harrison worked at Kensho"],
    }
    mock_get_graph.return_value = mock_graph

    r = client.post(
        "/api/v1/workflow",
        json={"query": "Where did Harrison work?"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["answer"] == "Harrison worked at Kensho."
    assert data["route"] == "rag"
    assert data["docs"] == ["Harrison worked at Kensho"]
