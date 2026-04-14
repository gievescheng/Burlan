from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


# ── TrainingCourse ─────────────────────────────────────

class TrainingCourseCreate(BaseModel):
    course_no: str = Field(..., min_length=1)
    title: str = ""
    category: str = "technical"
    description: str = ""
    prerequisites: str = ""
    required_for: str = ""
    duration_hours: float = 0.0
    validity_months: int = 0
    passing_score: float = 0.0
    related_document_id: str | None = None
    status: str = "active"
    notes: str = ""


class TrainingCourseUpdate(BaseModel):
    title: str | None = None
    category: str | None = None
    description: str | None = None
    prerequisites: str | None = None
    required_for: str | None = None
    duration_hours: float | None = None
    validity_months: int | None = None
    passing_score: float | None = None
    related_document_id: str | None = None
    status: str | None = None
    notes: str | None = None


class TrainingCourseOut(BaseModel):
    id: str
    course_no: str
    title: str
    category: str
    description: str
    prerequisites: str
    required_for: str
    duration_hours: float
    validity_months: int
    passing_score: float
    related_document_id: str | None
    status: str
    notes: str
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── TrainingRecord ─────────────────────────────────────

class TrainingRecordCreate(BaseModel):
    record_no: str = Field(..., min_length=1)
    course_id: str = Field(..., min_length=1)
    employee_id: str = Field(..., min_length=1)
    employee_name: str = ""
    department: str = ""
    position: str = ""
    training_type: str = "classroom"
    trainer: str = ""
    training_date: date | None = None
    completed_date: date | None = None
    score: float = 0.0
    passed: bool = False
    certificate_no: str = ""
    expiry_date: date | None = None
    notes: str = ""


class TrainingRecordUpdate(BaseModel):
    employee_name: str | None = None
    department: str | None = None
    position: str | None = None
    training_type: str | None = None
    trainer: str | None = None
    training_date: date | None = None
    completed_date: date | None = None
    score: float | None = None
    passed: bool | None = None
    certificate_no: str | None = None
    expiry_date: date | None = None
    verified_by: str | None = None
    verified_at: datetime | None = None
    notes: str | None = None


class TrainingRecordOut(BaseModel):
    id: str
    record_no: str
    course_id: str
    employee_id: str
    employee_name: str
    department: str
    position: str
    training_type: str
    trainer: str
    training_date: date | None
    completed_date: date | None
    score: float
    passed: bool
    certificate_no: str
    expiry_date: date | None
    verified_by: str
    verified_at: datetime | None
    notes: str
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
