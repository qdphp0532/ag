"""健康检查与 invoke 路由的简单测试。"""
from unittest.mock import patch, MagicMock

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
            AIMessage(
                content="",
                tool_calls=[{"name": "retrieve_documents", "args": {"query": "Where did Harrison work?"}, "id": "1"}],
            ),
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
    assert data["route"] == "retrieval"
    assert data["docs"] == ["Harrison worked at Kensho"]


@patch("app.api.deps.get_agent")
def test_invoke_direct_answer(mock_get_agent, client: TestClient) -> None:
    """不走工具时应返回 general。"""
    from langchain_core.messages import AIMessage

    mock_agent = MagicMock()
    mock_agent.invoke.return_value = {"messages": [AIMessage(content="Paris is the capital of France.")]}
    mock_get_agent.return_value = mock_agent

    r = client.post("/api/v1/invoke", json={"query": "What is the capital of France?"})
    assert r.status_code == 200
    data = r.json()
    assert data["answer"] == "Paris is the capital of France."
    assert data["route"] == "general"
    assert data["docs"] == []
