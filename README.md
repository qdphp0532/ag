# AG

一个用于 AI Agent 开发的轻量 Python 基础框架。

当前版本只保留一条清晰主线：

- FastAPI 提供 HTTP 接口
- LangChain `create_agent()` 作为统一 Agent 入口
- `app/agents/tools/` 组织 Agent 可调用工具
- `app/db/` 和 `app/domain/` 负责数据库连接、模型和仓库

它的定位不是“大而全平台”，而是一个适合继续开发、方便理解和方便改造的起点。

## 当前能力

当前仓库已经有这些基础能力：

- `GET /health` 健康检查
- `POST /api/v1/invoke` 统一 Agent 调用入口
- 检索工具：`retrieve_documents`
- 时间工具：`get_current_time`
- 通用测试工具：`echo`
- 数据库只读工具：`list_db_tables`、`query_examples`

注意：

- 当前检索能力还是示例实现，默认返回固定文档片段
- 当前没有多 Agent 协作
- 当前没有独立 LangGraph 工作流入口
- 当前没有长会话持久化记忆

## 项目结构

```text
ag/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   ├── deps.py
│   │   ├── routes/
│   │   └── schemas/
│   ├── agents/
│   │   ├── agent.py
│   │   └── tools/
│   ├── db/
│   ├── domain/
│   └── core/
├── doc/
├── scripts/
├── tests/
├── .env.example
└── requirements.txt
```

主调用链可以理解成：

`HTTP 请求 -> Agent -> Tool -> 返回 answer / route / docs`

## 环境要求

- Python 3.10+
- 建议使用独立虚拟环境
- 当前依赖组合已在 Python 3.12 下验证

环境管理工具不限，`venv`、`conda`、`uv` 都可以。

## 安装

使用 `venv`：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

使用 `conda`：

```bash
conda create -n ag python=3.12 -y
conda activate ag
pip install -r requirements.txt
cp .env.example .env
```

然后按实际模型提供方填写 `.env`。

## 配置

示例配置文件见 [.env.example](./.env.example)。

最小可运行配置通常只需要：

```env
DEFAULT_LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key
LLM_MODEL=gpt-4.1-mini
```

也支持：

- `qwen`
- `deepseek`
- `doubao`

数据库默认使用：

```env
DATABASE_URL=sqlite:///./data/app.db
```

应用启动时会自动创建表。

## 启动服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

可访问：

- Swagger 文档：`http://localhost:8000/docs`
- 健康检查：`http://localhost:8000/health`

## API 示例

健康检查：

```bash
curl http://localhost:8000/health
```

调用 Agent：

```bash
curl -X POST http://localhost:8000/api/v1/invoke \
  -H "Content-Type: application/json" \
  -d '{"query":"Where did Harrison work?"}'
```

当前响应结构：

```json
{
  "answer": "Harrison worked at Kensho.",
  "route": "retrieval",
  "docs": ["Harrison worked at Kensho"]
}
```

`route` 目前有三种：

- `general`：模型直接回答
- `tool`：调用了非检索类工具
- `retrieval`：调用了 `retrieve_documents`

## 当前工具

工具统一注册在 [app/agents/tools/__init__.py](./app/agents/tools/__init__.py)。

当前内置工具：

- [app/agents/tools/retrieval.py](./app/agents/tools/retrieval.py)
  说明：示例检索工具，默认返回固定文档片段
- [app/agents/tools/time_tools.py](./app/agents/tools/time_tools.py)
  说明：返回当前时间
- [app/agents/tools/common.py](./app/agents/tools/common.py)
  说明：回显文本，主要用于测试
- [app/agents/tools/db.py](./app/agents/tools/db.py)
  说明：数据库表查看和示例数据查询

## 数据库说明

数据库相关代码拆成了两层：

- `app/db/`：连接、引擎、Base、Session
- `app/domain/`：模型和仓库

当前约定：

- 仓库方法由调用方传入 `Session`
- Agent 数据库工具只做只读操作
- 默认 SQLite 会在启动时自动建表

如果你想快速写入一条示例数据，可以看 [scripts/mysql_demo.py](./scripts/mysql_demo.py)。

## 推荐学习顺序

如果你是第一次接触这个框架，建议按这个顺序看代码：

1. [app/agents/tools/retrieval.py](./app/agents/tools/retrieval.py)
2. [app/agents/agent.py](./app/agents/agent.py)
3. [app/api/routes/agents.py](./app/api/routes/agents.py)
4. [app/config.py](./app/config.py)
5. [app/agents/tools/db.py](./app/agents/tools/db.py)

顺序不要反过来。先看工具，再看 Agent，再看 API。

## 第一个 Demo 建议

最适合的第一个 demo 是“内部知识问答”：

1. 修改 [app/agents/tools/retrieval.py](./app/agents/tools/retrieval.py) 中的示例知识
2. 启动服务
3. 调用 `/api/v1/invoke`
4. 观察 Agent 是否先调用工具再回答

做完这个 demo，你基本就能理解这个框架最核心的写法。

不建议第一个 demo 就做：

- 多 Agent
- 复杂工作流
- 写数据库
- 长会话记忆

## 测试

```bash
python -m pytest tests/ -q
```

当前仓库已验证：

```text
4 passed
```

## 文档

详细说明见 `doc/`：

- [doc/00-快速开始.md](./doc/00-快速开始.md)
- [doc/01-架构与领域.md](./doc/01-架构与领域.md)
- [doc/02-工具开发.md](./doc/02-工具开发.md)
- [doc/03-选型与扩展.md](./doc/03-选型与扩展.md)
- [doc/04-数据库与存储.md](./doc/04-数据库与存储.md)
- [doc/05-数据库与领域拆分说明.md](./doc/05-数据库与领域拆分说明.md)
- [doc/06-大模型多厂商配置.md](./doc/06-大模型多厂商配置.md)
