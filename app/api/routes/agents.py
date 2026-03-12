"""
Agent 调用路由：invoke（同步）。
"""
from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from langchain_core.messages import HumanMessage

from app.api.deps import AgentDep, WorkflowGraphDep
from app.api.schemas import InvokeRequest, InvokeResponse
from app.agents.agent import parse_agent_result

router = APIRouter(prefix="/api/v1", tags=["agents"])


@router.post("/invoke", response_model=InvokeResponse)
async def invoke_agents(req: InvokeRequest, agent: AgentDep) -> InvokeResponse:
    """同步调用 LangChain Agent，返回最终答案。"""
    config: dict = {"recursion_limit": 10}
    if req.thread_id:
        config["configurable"] = {"thread_id": req.thread_id}

    def _run():
        result = agent.invoke(
            {"messages": [HumanMessage(content=req.query)]},
            config=config,
        )
        return result

    try:
        result = await run_in_threadpool(_run)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    messages = result.get("messages", [])
    answer, route, docs = parse_agent_result(messages)

    return InvokeResponse(answer=answer, route=route, docs=docs)


@router.post("/workflow", response_model=InvokeResponse)
async def invoke_workflow(req: InvokeRequest, graph: WorkflowGraphDep) -> InvokeResponse:
    """同步调用 LangGraph 工作流（混用时的图入口），固定为 检索 → 回答。"""
    config: dict = {}
    if req.thread_id:
        config["configurable"] = {"thread_id": req.thread_id}

    def _run():
        return graph.invoke({"query": req.query}, config=config or None)

    try:
        result = await run_in_threadpool(_run)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return InvokeResponse(
        answer=result.get("answer", ""),
        route="rag",
        docs=result.get("docs", []),
    )
