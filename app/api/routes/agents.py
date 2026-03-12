"""
Agent 调用路由：统一入口。
"""
from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool

from app.api.deps import AgentDep
from app.api.schemas import InvokeRequest, InvokeResponse
from app.agents.agent import parse_agent_result
from app.core import AppException

router = APIRouter(prefix="/api/v1", tags=["agents"])


@router.post("/invoke", response_model=InvokeResponse)
async def invoke_agents(req: InvokeRequest, agent: AgentDep) -> InvokeResponse:
    """同步调用统一的 LangChain agent。"""
    def _run():
        return agent.invoke({"messages": [{"role": "user", "content": req.query}]})

    try:
        result = await run_in_threadpool(_run)
    except Exception as e:
        raise AppException(message="agent invoke failed", details=str(e)) from e

    messages = result.get("messages", [])
    answer, route, docs = parse_agent_result(messages)

    return InvokeResponse(answer=answer, route=route, docs=docs)
