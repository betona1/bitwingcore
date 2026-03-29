"""Bitwing Core 데이터베이스 연결 모듈."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from bitwingcore.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    echo=settings.LOG_LEVEL == "DEBUG",
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """모든 ORM 모델의 베이스 클래스."""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 의존성 — DB 세션 제공."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
