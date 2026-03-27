"""
应用配置 — 从环境变量读取所有配置项
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用全局配置"""

    # ─── 应用基础 ───
    APP_NAME: str = "LifeButler"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # ─── AI 模型 ───
    CUSTOM_API_KEY: str = ""
    AI_MODEL: str = "claude-sonnet-4-6"
    AI_BASE_URL: str = "https://cursor.scihub.edu.kg/api"
    AI_TEMPERATURE: float = 0.7
    AI_MAX_TOKENS: int = 4096

    # ─── 数据库 ───
    DATABASE_URL: str = "sqlite+aiosqlite:///./lifebutler.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    # ─── 安全 ───
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ENCRYPTION_KEY: str = "dev-encryption-key-change-in-prod"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24小时
    ALGORITHM: str = "HS256"

    # ─── 外部 API ───
    QWEATHER_API_KEY: str = ""
    AMAP_API_KEY: str = ""
    QQ_EMAIL_ADDRESS: str = ""
    QQ_EMAIL_AUTH_CODE: str = ""
    NOTION_API_KEY: str = ""
    NOTION_DATABASE_ID: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 全局配置单例
settings = Settings()
