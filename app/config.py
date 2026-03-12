"""
应用配置：从环境变量加载，供 API 与 Agent 层共用。
支持多厂商大模型（OpenAI、Qwen、DeepSeek、豆包等），通过 DEFAULT_LLM_PROVIDER 或按厂商取配置。
"""
from functools import lru_cache
from typing import Any

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


# 已知厂商标识，用于校验与文档
LLM_PROVIDER_NAMES = ("openai", "qwen", "deepseek", "doubao")


class LLMProviderConfig(BaseModel):
    """单一大模型厂商的配置：API Key、Base URL、模型名。"""

    api_key: str = ""
    base_url: str | None = None
    model: str | None = None

    def to_llm_kwargs(self) -> dict[str, Any]:
        """供 ChatOpenAI 使用的参数字典（兼容 OpenAI 协议的厂商均可复用）。"""
        d: dict[str, Any] = {"model": self.model or "gpt-4.1-mini"}
        if self.api_key:
            d["api_key"] = self.api_key
        if self.base_url:
            d["base_url"] = self.base_url
        return d


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

    # 默认使用的 LLM 厂商
    default_llm_provider: str = "openai"

    # OpenAI（兼容代理或兼容 OpenAI 的端点；与历史 .env 兼容）
    openai_api_key: str = ""
    openai_base_url: str | None = None
    llm_model: str = "gpt-4.1-mini"

    # Qwen 通义千问
    qwen_api_key: str = ""
    qwen_base_url: str | None = None
    qwen_model: str = "qwen-plus"

    # DeepSeek
    deepseek_api_key: str = ""
    deepseek_base_url: str | None = None
    deepseek_model: str = "deepseek-chat"

    # 豆包 Doubao
    doubao_api_key: str = ""
    doubao_base_url: str | None = None
    doubao_model: str = "doubao-pro-32k"

    # LangSmith（可选）
    langsmith_tracing: bool = False
    langsmith_api_key: str = ""
    langsmith_project: str = "multi-agent"

    # 数据库（可选）
    database_url: str = "sqlite:///./data/app.db"

    def get_llm_config(self, provider: str | None = None) -> LLMProviderConfig:
        """按厂商名获取 LLM 配置；provider 为空时使用 default_llm_provider。"""
        name = (provider or self.default_llm_provider).strip().lower()
        if name == "openai":
            return LLMProviderConfig(
                api_key=self.openai_api_key,
                base_url=self.openai_base_url,
                model=self.llm_model or "gpt-4.1-mini",
            )
        if name == "qwen":
            return LLMProviderConfig(
                api_key=self.qwen_api_key,
                base_url=self.qwen_base_url,
                model=self.qwen_model or "qwen-plus",
            )
        if name == "deepseek":
            return LLMProviderConfig(
                api_key=self.deepseek_api_key,
                base_url=self.deepseek_base_url,
                model=self.deepseek_model or "deepseek-chat",
            )
        if name == "doubao":
            return LLMProviderConfig(
                api_key=self.doubao_api_key,
                base_url=self.doubao_base_url,
                model=self.doubao_model or "doubao-pro-32k",
            )
        # 未知厂商回退到 OpenAI 配置
        return LLMProviderConfig(
            api_key=self.openai_api_key,
            base_url=self.openai_base_url,
            model=self.llm_model or "gpt-4.1-mini",
        )

    def llm_kwargs(self, provider: str | None = None) -> dict[str, Any]:
        """供 ChatOpenAI 使用的参数字典；不传 provider 时使用默认厂商。"""
        return self.get_llm_config(provider).to_llm_kwargs()


@lru_cache
def get_settings() -> Settings:
    return Settings()
