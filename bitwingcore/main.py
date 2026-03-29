"""Bitwing Core — FastAPI 메인 애플리케이션."""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from bitwingcore.config import get_settings
from bitwingcore.utils.logger import setup_logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """애플리케이션 시작/종료 이벤트 관리."""
    settings = get_settings()
    setup_logger(settings.LOG_LEVEL)
    logger.info("Bitwing Core 서버 시작")

    # DB 연결 확인
    from bitwingcore.database import engine
    async with engine.begin() as conn:
        await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
    logger.info("데이터베이스 연결 확인 완료 ({})", settings.DB_HOST)

    yield

    logger.info("Bitwing Core 서버 종료")


def create_app() -> FastAPI:
    """FastAPI 앱 생성 팩토리."""
    app = FastAPI(
        title="Bitwing Core",
        description="AI 비서 시스템 서버",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check
    @app.get("/health")
    async def health_check() -> dict:
        """서버 상태 확인."""
        return {"status": "ok", "version": "0.1.0", "service": "bitwing-core"}

    # API 라우터 등록
    from bitwingcore.api import ALL_ROUTERS

    for router in ALL_ROUTERS:
        app.include_router(router, prefix="/api/v1")

    # WebSocket 라우터
    from bitwingcore.api.websocket import router as ws_router

    app.include_router(ws_router, prefix="/api/v1")

    return app


app = create_app()
