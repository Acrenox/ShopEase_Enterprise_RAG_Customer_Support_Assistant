from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'ShopEase Enterprise RAG Customer Support Assistant'
    app_env: str = 'development'
    log_level: str = 'INFO'

    llm_provider: str = 'local'

    azure_openai_api_key: str | None = None
    azure_openai_endpoint: str | None = None
    azure_openai_api_version: str | None = '2024-02-01'
    azure_openai_chat_deployment: str | None = None
    azure_openai_embedding_deployment: str | None = None

    google_api_key: str | None = None
    gemini_model: str = 'gemini-2.5-flash'
    gemini_embedding_model: str | None = None

    top_k: int = 8
    final_k: int = 4
    chunk_size: int = 700
    chunk_overlap: int = 100
    similarity_threshold: float = 0.35

    api_prefix: str = '/api/v1'
    api_key: str | None = None


settings = Settings()
