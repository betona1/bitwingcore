"""파일 API — 파일 업로드/다운로드/관리."""

import os
import uuid

from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bitwingcore.auth import verify_api_key
from bitwingcore.config import get_settings
from bitwingcore.database import get_db
from bitwingcore.models.managed_file import ManagedFile
from bitwingcore.utils.pagination import paginate
from bitwingcore.utils.response import error_response, success_response

router = APIRouter(prefix="/files", tags=["files"])


@router.get("")
async def list_files(
    category: str | None = None,
    access_level: str | None = None,
    page: int = 1,
    size: int = 50,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """파일 목록 조회."""
    query = select(ManagedFile).order_by(ManagedFile.created_at.desc())

    if category:
        query = query.where(ManagedFile.category == category)
    if access_level:
        query = query.where(ManagedFile.access_level == access_level)

    items, meta = await paginate(db, query, page=page, size=size)

    return success_response(
        data={
            "items": [
                {
                    "id": f.id,
                    "filename": f.filename,
                    "filepath": f.filepath,
                    "file_size": f.file_size,
                    "mime_type": f.mime_type,
                    "category": f.category,
                    "access_level": f.access_level,
                    "created_at": str(f.created_at),
                }
                for f in items
            ],
            "meta": meta,
        }
    )


@router.post("/upload")
async def upload_file(
    file: UploadFile,
    category: str = "general",
    access_level: str = "public",
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """파일 업로드."""
    settings = get_settings()
    storage_path = settings.FILE_STORAGE_PATH

    # 저장 디렉토리 생성
    upload_dir = os.path.join(storage_path, category)
    os.makedirs(upload_dir, exist_ok=True)

    # 고유 파일명 생성
    ext = os.path.splitext(file.filename or "file")[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(upload_dir, unique_name)

    # 파일 저장
    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    # DB 등록
    managed = ManagedFile(
        filename=file.filename or unique_name,
        filepath=filepath,
        file_size=len(content),
        mime_type=file.content_type,
        category=category,
        access_level=access_level,
    )
    db.add(managed)
    await db.commit()
    await db.refresh(managed)

    return success_response(
        data={
            "id": managed.id,
            "filename": managed.filename,
            "file_size": managed.file_size,
        },
        message="파일을 업로드했습니다.",
    )


@router.get("/{file_id}")
async def get_file_info(
    file_id: int,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """파일 상세 정보 조회."""
    result = await db.execute(select(ManagedFile).where(ManagedFile.id == file_id))
    managed = result.scalar_one_or_none()
    if not managed:
        error_response("파일을 찾을 수 없습니다.", 404)

    return success_response(
        data={
            "id": managed.id,
            "filename": managed.filename,
            "filepath": managed.filepath,
            "file_size": managed.file_size,
            "mime_type": managed.mime_type,
            "category": managed.category,
            "access_level": managed.access_level,
            "allowed_managers": managed.allowed_managers,
            "uploaded_by": managed.uploaded_by,
            "created_at": str(managed.created_at),
        }
    )


@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """파일 삭제."""
    result = await db.execute(select(ManagedFile).where(ManagedFile.id == file_id))
    managed = result.scalar_one_or_none()
    if not managed:
        error_response("파일을 찾을 수 없습니다.", 404)

    # 물리 파일 삭제
    if os.path.exists(managed.filepath):
        os.remove(managed.filepath)

    await db.delete(managed)
    await db.commit()

    return success_response(message="파일을 삭제했습니다.")
