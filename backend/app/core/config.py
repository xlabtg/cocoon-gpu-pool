"""Application configuration."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Cocoon GPU Pool Monitoring"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://cocoon:cocoon@localhost:5432/cocoon_pool"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Worker Monitoring
    WORKER_SCRAPE_INTERVAL: int = 15  # seconds
    WORKER_BASE_PORT: int = 12000
    WORKER_PORT_INCREMENT: int = 10
    MAX_WORKERS: int = 10

    # TON Blockchain
    TON_API_URL: str = "https://toncenter.com/api/v2"
    TON_API_KEY: Optional[str] = None

    # Alerting
    ALERT_CHECK_INTERVAL: int = 60  # seconds
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[str] = None

    # Telegram Bot
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_WEBHOOK_URL: Optional[str] = None

    # Prometheus
    PROMETHEUS_PORT: int = 9090
    METRICS_PORT: int = 8000

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
