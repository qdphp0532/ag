# AG

一个面向 AI Agent 开发的轻量基础框架，当前主线是：

- FastAPI 提供 HTTP 接口
- LangChain `create_agent()` 作为统一 Agent 入口
- `agents/tools/` 管理可扩展工具
- `db/ + domain/` 管理数据库连接、模型和仓库

这个仓库的目标不是堆很多能力，而是提供一个足够清晰、足够稳定、方便继续演进的起点。

## 适合做什么

- 做一个可调用工具的单 Agent 服务
- 快速验证 RAG、时间工具、数据库只读查询这类能力
- 作为后续业务 Agent 的基础脚手架

当前不默认做的事：

- 多 Agent 协作
- 复杂工作流图编排
- 长会话持久化记忆
- 高度抽象的插件系统

这些能力以后可以加，但默认骨架先保持简单。

## 项目结构

```text
ag/
├── app/
│   ├── main.py                 # FastAPI 入口
│   ├── config.py               # 统一配置
│   ├── api/                    # 路由、schema、依赖注入
│   ├── agents/                 # Agent 入口与工具注册
│   ├── db/                     # 引擎、Base、Session
│   ├── domain/                 # 模型与仓库
│   └── core/                   # 异常等基础设施
├── doc/                        # 研发文档
├── scripts/                    # demo / 辅助脚本
├── tests/                      # 测试
└── requirements.txt
```

你可以把主调用链理解成：

`HTTP 请求 -> Agent -> Tool -> 返回结果`

## 环境准备

项目要求：

- Python 3.10+
- 建议使用独立虚拟环境
- 当前依赖组合已在 Python 3.12 下验证

你可以使用 `venv`、`conda`、`uv` 等任意环境管理方式。下面给两个常见示例。

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

然后按你的模型提供方填写 `.env`。

## 环境变量示例

仓库已提供 [.env.example](/Users/yongzhang/code/ai/ag/.env.example)。

最小可运行配置通常只需要：

```env
DEFAULT_LLM_PROVIDER=openai
OPENAI_API_KEY=your_api_key
LLM_MODEL=gpt-4.1-mini
```

如果你不用 OpenAI，也可以切到 `qwen`、`deepseek`、`doubao`。

## 启动服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动后可访问：

- 文档：`http://localhost:8000/docs`
- 健康检查：`GET /health`
- Agent 调用：`POST /api/v1/invoke`

## 调用示例

```bash
curl http://localhost:8000/health
```

```bash
curl -X POST http://localhost:8000/api/v1/invoke \
  -H "Content-Type: application/json" \
  -d '{"query":"Where did Harrison work?"}'
```

返回结构：

```json
{
  "answer": "Harrison worked at Kensho.",
  "route": "retrieval",
  "docs": ["Harrison worked at Kensho"]
}
```

`route` 当前有三种：

- `general`：模型直接回答，没有调用工具
- `tool`：调用了非检索类工具
- `retrieval`：调用了 `retrieve_documents`

## 开发入口

如果你要学习这个框架怎么写，建议按这个顺序看：

1. [app/agents/tools/retrieval.py](/Users/yongzhang/code/ai/ag/app/agents/tools/retrieval.py)
2. [app/agents/agent.py](/Users/yongzhang/code/ai/ag/app/agents/agent.py)
3. [app/api/routes/agents.py](/Users/yongzhang/code/ai/ag/app/api/routes/agents.py)
4. [app/config.py](/Users/yongzhang/code/ai/ag/app/config.py)

先理解工具怎么写，再看 Agent 怎么调用工具，最后看 API 怎么暴露出来。

## 怎么写第一个 Demo

最适合的第一个 demo 是“内部知识问答”：

1. 修改 [app/agents/tools/retrieval.py](/Users/yongzhang/code/ai/ag/app/agents/tools/retrieval.py) 里的示例文档
2. 启动服务
3. 通过 `/api/v1/invoke` 发问题
4. 验证 Agent 是否先调工具再回答

不要一开始就做复杂工作流、持久化记忆或多 Agent。

## 怎么扩展

### 1. 新增工具

在 `app/agents/tools/` 下新增模块，然后在 [app/agents/tools/__init__.py](/Users/yongzhang/code/ai/ag/app/agents/tools/__init__.py) 注册。

### 2. 新增数据库模型

在 `app/domain/models/` 下新增模型，在 `app/domain/repositories/` 下新增仓库。

### 3. 新增数据库工具

在 [app/agents/tools/db.py](/Users/yongzhang/code/ai/ag/app/agents/tools/db.py) 中添加只读工具。

当前约定是：

- 仓库方法由调用方传入 `Session`
- Agent 的数据库工具只做只读查询

## 测试

```bash
python -m pytest tests/ -q
```

当前仓库已在 Python 3.12 环境下验证：

```text
4 passed
```

## 文档

更详细的说明在 `doc/`：

- [doc/00-快速开始.md](/Users/yongzhang/code/ai/ag/doc/00-%E5%BF%AB%E9%80%9F%E5%BC%80%E5%A7%8B.md)
- [doc/01-架构与领域.md](/Users/yongzhang/code/ai/ag/doc/01-%E6%9E%B6%E6%9E%84%E4%B8%8E%E9%A2%86%E5%9F%9F.md)
- [doc/02-工具开发.md](/Users/yongzhang/code/ai/ag/doc/02-%E5%B7%A5%E5%85%B7%E5%BC%80%E5%8F%91.md)
- [doc/03-选型与扩展.md](/Users/yongzhang/code/ai/ag/doc/03-%E9%80%89%E5%9E%8B%E4%B8%8E%E6%89%A9%E5%B1%95.md)
- [doc/04-数据库与存储.md](/Users/yongzhang/code/ai/ag/doc/04-%E6%95%B0%E6%8D%AE%E5%BA%93%E4%B8%8E%E5%AD%98%E5%82%A8.md)

## 当前状态

这是一个适合继续开发的基础框架，不是大而全平台。

如果你后面准备继续扩展，推荐优先顺序是：

1. 新工具
2. 新业务模型和仓库
3. 流式输出
4. 记忆与持久化
5. 复杂工作流
