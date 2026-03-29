"""Bitwing Core 설정 관리 모듈."""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """환경변수 기반 애플리케이션 설정."""

    # Database
    DB_HOST: str = "192.168.219.200"
    DB_PORT: int = 3306
    DB_NAME: str = "bitwing"
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_CHARSET: str = "utf8mb4"

    # Anthropic Claude API
    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"

    # Server
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8281
    API_KEY: str = ""

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8281/api/v1/auth/google/callback"

    # 파일 스토리지
    FILE_STORAGE_PATH: str = "/data/bitwing"

    # JWT
    JWT_SECRET: str = ""

    # Logging
    LOG_LEVEL: str = "DEBUG"

    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""

    # OCR
    OCR_ENGINE: str = "tesseract"

    # NAS
    NAS202_MOUNT: str = "/mnt/nas202"
    NAS202_HOST: str = "192.168.219.202"

    # AI Server (Ollama)
    AI_SERVER_HOST: str = "192.168.219.80"
    AI_SERVER_PORT: int = 8080

    @property
    def database_url(self) -> str:
        """SQLAlchemy async 접속 URL 생성."""
        from urllib.parse import quote_plus
        password = quote_plus(self.DB_PASSWORD)
        return (
            f"mysql+aiomysql://{self.DB_USER}:{password}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"?charset={self.DB_CHARSET}"
        )

    @property
    def sync_database_url(self) -> str:
        """동기 접속 URL (Celery 등에서 사용)."""
        from urllib.parse import quote_plus
        password = quote_plus(self.DB_PASSWORD)
        return (
            f"mysql+mysqldb://{self.DB_USER}:{password}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"?charset={self.DB_CHARSET}"
        )

    @property
    def redis_url(self) -> str:
        """Redis 접속 URL."""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    """설정 싱글톤 반환."""
    return Settings()
