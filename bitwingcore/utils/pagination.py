"""페이지네이션 헬퍼."""

import math
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select


async def paginate(
    db: AsyncSession,
    query: Select,
    page: int = 1,
    size: int = 50,
) -> tuple[list[Any], dict[str, int]]:
    """쿼리 결과를 페이지네이션하여 반환.

    Args:
        db: DB 세션
        query: SQLAlchemy Select 쿼리
        page: 페이지 번호 (1부터)
        size: 페이지당 항목 수

    Returns:
        (항목 리스트, 페이지 메타 정보)
    """
    page = max(1, page)
    size = max(1, min(size, 200))

    # 전체 개수
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # 페이지 데이터
    offset = (page - 1) * size
    result = await db.execute(query.offset(offset).limit(size))
    items = list(result.scalars().all())

    meta = {
        "page": page,
        "size": size,
        "total": total,
        "total_pages": math.ceil(total / size) if total > 0 else 0,
    }

    return items, meta
