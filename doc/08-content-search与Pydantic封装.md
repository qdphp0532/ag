# 内容检索结果是否要用 Pydantic 封装？

## 结论（建议）

**推荐在「收到 HTTP JSON 之后」用 Pydantic 做一次解析/校验**，再交给 Agent 或业务逻辑使用。

- **不是必须**：若你只把整段 JSON 当字符串塞给模型、且不关心字段类型，可以继续用 `dict`。
- **有明显收益**时更值得做：需要类型安全、IDE 补全、统一字段默认值、过滤未知字段、或要把同一结构暴露给 FastAPI 的 OpenAPI 文档。

## 好处

1. **契约明确**：`ContentSearchApiResponse` / `ContentSearchItem` 即「接口返回长什么样」的可执行文档。
2. **尽早发现接口变更**：字段类型不对、必填缺失时，`ValidationError` 比后面随机 `KeyError` 好查。
3. **`extra="ignore"`**：第三方多返回字段时不易打断流程；若需保留可改为 `extra="allow"` 并用单独字段承接。
4. **与 LangChain Tool 的配合**：`@tool` 最终给模型看的往往是可 JSON 序列化的内容。用 **`model_dump()`** 转成 `dict` 返回，兼容性好。

## 本项目中的实现位置

- 模型定义：`app/domain/content_search_schemas.py`
- 工具内校验：`app/agents/tools/content_search.py` 在 `response.json()` 后 `ContentSearchApiResponse.model_validate(...)`，成功则 `model_dump()`；校验失败时返回带 `error` 的 dict，便于 Agent 向用户说明。

## 环境变量

- `CONTENT_SEARCH_X_API_KEY`：检索接口的 `x-api-key`，勿写入代码仓库（由 `app.config.Settings` 从 `.env` 加载）。

## 本地调试本文件

- **推荐**（在仓库根目录 `ag/` 下）：`python -m app.agents.tools.content_search`
- **直接跑脚本**：`python app/agents/tools/content_search.py` 也可；文件开头会在 `__main__` 时把仓库根目录插入 `sys.path`，否则会报 `ModuleNotFoundError: No module named 'app'`。
