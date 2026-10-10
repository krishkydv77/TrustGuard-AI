from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "TrustGuard AI"
    environment: str = "development"
    api_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./safeassist_db"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    redis_url: str = ""
    jwt_secret_key: str = "dev-only-change-this-secret-before-deployment-32chars"
    jwt_expire_minutes: int = 60
    cors_origins: str = "http://localhost:8501"
    moderation_review_threshold: float = 0.45
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()
