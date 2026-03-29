"""Bitwing Core 로깅 설정 모듈."""

import sys

from loguru import logger


def setup_logger(log_level: str = "DEBUG") -> None:
    """loguru 로거 설정."""
    logger.remove()

    # 콘솔 출력
    logger.add(
        sys.stderr,
        level=log_level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
    )

    # 파일 로깅
    logger.add(
        "/var/log/bitwing/bitwing_{time:YYYY-MM-DD}.log",
        level=log_level,
        rotation="00:00",
        retention="30 days",
        encoding="utf-8",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
    )
