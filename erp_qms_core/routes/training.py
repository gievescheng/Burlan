from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import database
from ..schemas.training import (
    TrainingCourseCreate, TrainingCourseOut, TrainingCourseUpdate,
    TrainingRecordCreate, TrainingRecordOut, TrainingRecordUpdate,
)
from ..services import training as svc

router = APIRouter()


# ── TrainingCourse ─────────────────────────────────────

@router.get("/training-courses", response_model=list[TrainingCourseOut])
def list_courses(status: str | None = None, category: str | None = None):
    with database.session_scope() as s:
        return svc.list_courses(s, status=status, category=category)


@router.get("/training-courses/{course_id}", response_model=TrainingCourseOut)
def get_course(course_id: str):
    with database.session_scope() as s:
        row = svc.get_course(s, course_id)
    if not row:
        raise HTTPException(404, "Course not found")
    return row


@router.post("/training-courses", response_model=TrainingCourseOut, status_code=201)
def create_course(body: TrainingCourseCreate):
    try:
        with database.session_scope() as s:
            return svc.create_course(s, body.model_dump())
    except ValueError as e:
        msg = str(e)
        if "already exists" in msg:
            raise HTTPException(409, msg)
        raise HTTPException(422, msg)


@router.patch("/training-courses/{course_id}", response_model=TrainingCourseOut)
def update_course(course_id: str, body: TrainingCourseUpdate):
    try:
        with database.session_scope() as s:
            row = svc.update_course(s, course_id, body.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(422, str(e))
    if not row:
        raise HTTPException(404, "Course not found")
    return row


@router.delete("/training-courses/{course_id}", status_code=204)
def delete_course(course_id: str):
    with database.session_scope() as s:
        if not svc.delete_course(s, course_id):
            raise HTTPException(404, "Course not found")


# ── TrainingRecord ─────────────────────────────────────

@router.get("/training-records", response_model=list[TrainingRecordOut])
def list_records(
    course_id: str | None = None,
    employee_id: str | None = None,
    department: str | None = None,
    training_type: str | None = None,
    passed: bool | None = None,
):
    with database.session_scope() as s:
        return svc.list_records(
            s, course_id=course_id, employee_id=employee_id,
            department=department, training_type=training_type, passed=passed,
        )


@router.get("/training-records/{record_id}", response_model=TrainingRecordOut)
def get_record(record_id: str):
    with database.session_scope() as s:
        row = svc.get_record(s, record_id)
    if not row:
        raise HTTPException(404, "Record not found")
    return row


@router.post("/training-records", response_model=TrainingRecordOut, status_code=201)
def create_record(body: TrainingRecordCreate):
    try:
        with database.session_scope() as s:
            return svc.create_record(s, body.model_dump())
    except ValueError as e:
        msg = str(e)
        if "already exists" in msg:
            raise HTTPException(409, msg)
        raise HTTPException(422, msg)


@router.patch("/training-records/{record_id}", response_model=TrainingRecordOut)
def update_record(record_id: str, body: TrainingRecordUpdate):
    try:
        with database.session_scope() as s:
            row = svc.update_record(s, record_id, body.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(422, str(e))
    if not row:
        raise HTTPException(404, "Record not found")
    return row


@router.delete("/training-records/{record_id}", status_code=204)
def delete_record(record_id: str):
    with database.session_scope() as s:
        if not svc.delete_record(s, record_id):
            raise HTTPException(404, "Record not found")
