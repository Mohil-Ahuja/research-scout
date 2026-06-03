import os

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ModuleNotFoundError:  # Keeps lightweight unit tests runnable before installation.
    from pydantic import BaseModel as BaseSettings

    def SettingsConfigDict(**kwargs):
        return kwargs


class Settings(BaseSettings):
    xai_api_key: str | None = None
    grok_model: str = "grok-3-mini"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    arxiv_timeout_seconds: float = 20.0
    arxiv_retries: int = 2
    default_max_results: int = 20
    default_top_k: int = 5
    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    def __init__(self, **values):
        for field in ("xai_api_key", "grok_model", "embedding_model", "arxiv_timeout_seconds",
                      "arxiv_retries", "default_max_results", "default_top_k"):
            env_name = field.upper()
            if field not in values and os.getenv(env_name) is not None:
                values[field] = os.environ[env_name]
        super().__init__(**values)
