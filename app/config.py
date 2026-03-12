"""
应用配置：从环境变量加载，供 API 与 Agent 层共用。
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    app_name: str = "Multi-Agent API"
    app_version: str = "0.1.0"
    debug: bool = False

    # LLM（Agent 用）
    openai_api_key: str = ""
    openai_base_url: str | None = None  # 兼容代理或兼容 OpenAI 的端点
    llm_model: str = "gpt-4.1-mini"

    # LangSmith（可选）
    langsmith_tracing: bool = False
    langsmith_api_key: str = ""
    langsmith_project: str = "multi-agent"

    def llm_kwargs(self) -> dict:
        """供 ChatOpenAI 使用的参数字典。"""
        d: dict = {"model": self.llm_model}
        if self.openai_api_key:
            d["api_key"] = self.openai_api_key
        if self.openai_base_url:
            d["base_url"] = self.openai_base_url
        return d


@lru_cache
def get_settings() -> Settings:
    return Settings()
