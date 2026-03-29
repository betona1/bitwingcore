"""Pydantic 요청/응답 스키마."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


# === 공통 ===
class PaginationParams(BaseModel):
    """페이지네이션 파라미터."""
    page: int = Field(1, ge=1)
    size: int = Field(50, ge=1, le=200)


# === 채팅 ===
class ChatRequest(BaseModel):
    """채팅 요청."""
    message: str = Field(..., min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    """채팅 응답."""
    success: bool
    message: str
    data: dict | None = None
    intent: str | None = None
    manager: str | None = None


# === 일정 ===
class CalendarCreate(BaseModel):
    """일정 생성 요청."""
    title: str = Field(..., max_length=500)
    description: str | None = None
    start_at: datetime
    end_at: datetime
    location: str | None = None
    reminder_minutes: int = 30


class CalendarUpdate(BaseModel):
    """일정 수정 요청."""
    title: str | None = None
    description: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    location: str | None = None
    reminder_minutes: int | None = None
    status: str | None = None


# === 할일 ===
class TodoCreate(BaseModel):
    """할일 생성 요청."""
    title: str = Field(..., max_length=500)
    description: str | None = None
    priority: str = "normal"
    due_date: date | None = None
    assigned_manager: str | None = None


class TodoUpdate(BaseModel):
    """할일 수정 요청."""
    title: str | None = None
    description: str | None = None
    priority: str | None = None
    status: str | None = None
    due_date: date | None = None


# === 메모 ===
class MemoCreate(BaseModel):
    """메모 생성 요청."""
    title: str | None = None
    content: str = Field(..., min_length=1)
    tags: list[str] | None = None
    category: str | None = None


class MemoUpdate(BaseModel):
    """메모 수정 요청."""
    title: str | None = None
    content: str | None = None
    tags: list[str] | None = None
    category: str | None = None


# === 가계부 ===
class FinanceCreate(BaseModel):
    """가계부 거래 생성 요청."""
    type: str = Field(..., pattern="^(income|expense)$")
    amount: Decimal = Field(..., gt=0)
    category: str
    subcategory: str | None = None
    description: str | None = None
    payment_method: str | None = None
    merchant: str | None = None
    transaction_date: date


class FinanceUpdate(BaseModel):
    """가계부 거래 수정 요청."""
    type: str | None = None
    amount: Decimal | None = None
    category: str | None = None
    description: str | None = None
    payment_method: str | None = None
    transaction_date: date | None = None


# === PC 관리 ===
class PCCreate(BaseModel):
    """PC 등록 요청."""
    hostname: str
    ip_address: str | None = None
    os_type: str = "windows"
    employee_name: str | None = None
    department: str | None = None


class PCCommand(BaseModel):
    """PC 원격 명령 요청."""
    command: str


# === 이메일 ===
class EmailSyncRequest(BaseModel):
    """이메일 동기화 요청."""
    provider: str = "gmail"
    max_count: int = 50


# === 파일 ===
class FileRegister(BaseModel):
    """파일 등록 요청."""
    filename: str
    filepath: str
    file_size: int | None = None
    mime_type: str | None = None
    category: str | None = None
    access_level: str = "public"


# === 연동 ===
class IntegrationCreate(BaseModel):
    """연동 설정 생성."""
    service: str
    config: dict | None = None
