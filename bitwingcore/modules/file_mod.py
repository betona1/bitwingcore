"""파일 관리 모듈."""

import os
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bitwingcore.config import get_settings
from bitwingcore.models.managed_file import ManagedFile
from bitwingcore.modules.base import BaseModule, ModuleRegistry
from bitwingcore.utils.pagination import paginate


@ModuleRegistry.register("file_mod")
class FileModule(BaseModule):
    """파일 업로드/다운로드/관리 모듈."""

    display_name = "파일 관리"
    description = "파일 업로드, 목록 조회, 접근 권한 관리"
    supported_intents = [
        "file.upload",
        "file.list",
    ]

    async def execute(
        self,
        intent: str,
        params: dict[str, Any],
        db: AsyncSession,
    ) -> dict[str, Any]:
        """파일 모듈 실행."""
        action = intent.split(".")[-1]

        if action == "upload":
            return await self._register(params, db)
        if action == "list":
            return await self._list(params, db)

        return {"message": "지원하지 않는 동작입니다."}

    async def _register(self, params: dict[str, Any], db: AsyncSession) -> dict[str, Any]:
        """파일 메타 등록 (실제 업로드는 API 레이어에서 처리)."""
        filepath = params.get("filepath", "")
        filename = params.get("filename", os.path.basename(filepath))

        managed = ManagedFile(
            filename=filename,
            filepath=filepath,
            file_size=params.get("file_size"),
            mime_type=params.get("mime_type"),
            category=params.get("category"),
            access_level=params.get("access_level", "public"),
            allowed_managers=params.get("allowed_managers"),
            uploaded_by=params.get("uploaded_by"),
        )
        db.add(managed)
        await db.commit()
        await db.refresh(managed)

        return {
            "id": managed.id,
            "filename": managed.filename,
            "filepath": managed.filepath,
            "access_level": managed.access_level,
        }

    async def _list(self, params: dict[str, Any], db: AsyncSession) -> dict[str, Any]:
        """파일 목록 조회."""
        query = select(ManagedFile).order_by(ManagedFile.created_at.desc())

        category = params.get("category")
        if category:
            query = query.where(ManagedFile.category == category)

        access_level = params.get("access_level")
        if access_level:
            query = query.where(ManagedFile.access_level == access_level)

        page = params.get("page", 1)
        items, meta = await paginate(db, query, page=page)

        return {
            "items": [
                {
                    "id": f.id,
                    "filename": f.filename,
                    "filepath": f.filepath,
                    "file_size": f.file_size,
                    "mime_type": f.mime_type,
                    "category": f.category,
                    "access_level": f.access_level,
                    "created_at": f.created_at,
                }
                for f in items
            ],
            "meta": meta,
        }
