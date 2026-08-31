"""
Global application settings and environment configuration management using Pydantic Settings.
"""

from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application Info
    PROJECT_NAME: str = "NetOps Nexus"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Server Binding
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:5173"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:80",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "*",
    ]

    # Security & Cryptography
    SECRET_KEY: str = "netops-nexus-dev-secret-key-change-in-production-minimum-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    BCRYPT_ROUNDS: int = 12

    # Database Settings
    DATABASE_URL: str = "sqlite+aiosqlite:///./netops_nexus.db"
    SYNC_DATABASE_URL: str = "sqlite:///./netops_nexus.db"
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    # Redis Cache & Bus
    REDIS_URL: str = "redis://localhost:6379/0"
    USE_REDIS: bool = False

    # Lab Network Mode
    LAB_MODE: bool = True
    LAB_TICK_INTERVAL_SECONDS: int = 5
    LAB_DEVICE_COUNT: int = 24
    LAB_SITE_COUNT: int = 4

    # Monitoring & Polling
    TELEMETRY_POLL_INTERVAL_SECONDS: int = 10
    ALERT_EVALUATION_INTERVAL_SECONDS: int = 15
    DISCOVERY_WORKER_CONCURRENCY: int = 10
    METRIC_RETENTION_DAYS: int = 30

    # Security Scanning
    ENABLE_SECURITY_AUDIT_ON_STARTUP: bool = True
    CIS_BENCHMARK_STRICT_MODE: bool = False

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
