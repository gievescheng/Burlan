from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


# ── Document ───────────────────────────────────────────

class DocumentCreate(BaseModel):
    document_no: str = Field(..., min_length=1)
    title: str = ""
    category: str = "procedure"
    classification: str = "controlled"
    owner: str = ""
    department: str = ""
    current_revision: str = ""
    status: str = "active"
    description: str = ""
    notes: str = ""


class DocumentUpdate(BaseModel):
    title: str | None = None
    category: str | None = None
    classification: str | None = None
    owner: str | None = None
    department: str | None = None
    current_revision: str | None = None
    status: str | None = None
    description: str | None = None
    notes: str | None = None


class DocumentOut(BaseModel):
    id: str
    document_no: str
    title: str
    category: str
    classification: str
    owner: str
    department: str
    current_revision: str
    status: str
    description: str
    notes: str
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── DocumentRevision ───────────────────────────────────

class DocumentRevisionCreate(BaseModel):
    document_id: str = Field(..., min_length=1)
    revision: str = Field(..., min_length=1)
    change_summary: str = ""
    change_reason: str = ""
    prepared_by: str = ""
    prepared_at: datetime | None = None
    reviewed_by: str = ""
    reviewed_at: datetime | None = None
    approved_by: str = ""
    approved_at: datetime | None = None
    effective_date: date | None = None
    obsolete_date: date | None = None
    file_path: str = ""
    file_checksum: str = ""
    notes: str = ""


class DocumentRevisionUpdate(BaseModel):
    revision: str | None = None
    change_summary: str | None = None
    change_reason: str | None = None
    prepared_by: str | None = None
    prepared_at: datetime | None = None
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    approved_by: str | None = None
    approved_at: datetime | None = None
    effective_date: date | None = None
    obsolete_date: date | None = None
    file_path: str | None = None
    file_checksum: str | None = None
    status: str | None = None
    is_current: bool | None = None
    notes: str | None = None


class DocumentRevisionOut(BaseModel):
    id: str
    document_id: str
    revision: str
    change_summary: str
    change_reason: str
    prepared_by: str
    prepared_at: datetime | None
    reviewed_by: str
    reviewed_at: datetime | None
    approved_by: str
    approved_at: datetime | None
    effective_date: date | None
    obsolete_date: date | None
    file_path: str
    file_checksum: str
    status: str
    is_current: bool
    notes: str
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
