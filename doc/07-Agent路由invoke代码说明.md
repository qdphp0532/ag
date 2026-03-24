# `invoke_agents` 路由代码说明与仿照开发

对应文件：`app/api/routes/agents.py` 中 `POST /api/v1/invoke` 的处理函数。

## 逐段说明（约 16–29 行）

| 代码 | 用处 |
|------|------|
| `@router.post("/invoke", response_model=InvokeResponse)` | 声明 **POST** 路径与 **成功时** 的响应体模型（OpenAPI / 自动校验序列化）。 |
| `async def invoke_agents(req: InvokeRequest, agent: AgentDep)` | **异步** 路由：请求体用 `InvokeRequest`；`AgentDep` 通过 FastAPI **依赖注入** 拿到已编译的 LangChain agent 单例。 |
| `def _run(): return agent.invoke({...})` | LangChain 的 `invoke` 多为 **同步阻塞**；包成函数是为了交给线程池执行，避免卡住事件循环。 |
| `{"messages": [{"role": "user", "content": req.query}]}` | Agent 的 **标准输入结构**：一轮用户消息；与 `create_agent` 的状态约定一致。 |
| `await run_in_threadpool(_run)` | FastAPI 提供的工具：在 **线程池** 里跑同步代码，保持路由 `async` 且不阻塞其他请求。 |
| `try/except` + `raise AppException(...)` | 把任意底层异常转成 **业务统一错误**（配合 `setup_exception_handlers` 返回固定 JSON 结构）。 |
| `result.get("messages", [])` | 取 agent 返回字典里的 **消息列表**（多轮对话、工具调用都会体现在 messages 里）。 |
| `parse_agent_result(messages)` | 从原始 messages 里抽出 **`answer` / `route` / `docs`**，适配 API 的 `InvokeResponse`。 |
| `return InvokeResponse(...)` | 构造并返回 **Pydantic 响应模型**，FastAPI 负责序列化为 JSON。 |

## 仿照开发时可以怎么做

### 1. 新增一个「同类」接口（改路径/入参/出参）

1. 在 `app/api/schemas/`（或同模块）里定义 **Request / Response** 的 Pydantic 模型。
2. 在路由模块里 `APIRouter` 上挂新路径，例如 `@router.post("/xxx")`。
3. 需要 agent 时继续用 **`agent: AgentDep`**；需要配置时用 **`config: ConfigDep`**（见 `app/api/deps.py`）。
4. 若调用的是 **同步** SDK（含 `agent.invoke`），继续用 **`run_in_threadpool`** 包一层。
5. 若调用 **原生 async** API（如 `agent.ainvoke`），可直接 `await`，不必进线程池。
6. 错误处理：业务可预期用 **`raise AppException(...)`**；或扩展 `setup_exception_handlers` 注册更多异常类型。

### 2. 新增另一种「后端能力」而不是改 Agent

- 把重逻辑放在 **`app/domain/`** 或 **`app/agents/`** 的纯函数/服务里。
- 路由层只做：**校验入参 → 调服务 → 映射响应**，保持与 `invoke_agents` 相同的分层。

### 3. 流式输出（SSE / 逐 token）

- 不能简单复用「一次性 `InvokeResponse`」；需用 **`StreamingResponse`** 或 LangChain 的 **stream / astream_events**，单独开路由，文档与测试单独写。

## 相关文件

- 依赖注入：`app/api/deps.py`
- 请求响应模型：`app/api/schemas/agents.py`
- Agent 构建与结果解析：`app/agents/agent.py`（`parse_agent_result`）
