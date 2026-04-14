from __future__ import annotations

from sqlalchemy.orm import Session

from ..models.training import TrainingCourse, TrainingRecord


# ── TrainingCourse ─────────────────────────────────────

def list_courses(
    session: Session,
    *,
    status: str | None = None,
    category: str | None = None,
) -> list[TrainingCourse]:
    q = session.query(TrainingCourse)
    if status:
        q = q.filter(TrainingCourse.status == status)
    if category:
        q = q.filter(TrainingCourse.category == category)
    return q.order_by(TrainingCourse.course_no.asc()).all()


def get_course(session: Session, course_id: str) -> TrainingCourse | None:
    return session.get(TrainingCourse, course_id)


def get_course_by_no(session: Session, course_no: str) -> TrainingCourse | None:
    return session.query(TrainingCourse).filter(
        TrainingCourse.course_no == course_no,
    ).first()


def create_course(session: Session, data: dict) -> TrainingCourse:
    obj = TrainingCourse(**data)
    session.add(obj)
    session.flush()
    return obj


def update_course(session: Session, course_id: str, data: dict) -> TrainingCourse | None:
    obj = session.get(TrainingCourse, course_id)
    if not obj:
        return None
    for k, v in data.items():
        if v is not None:
            setattr(obj, k, v)
    session.flush()
    return obj


def delete_course(session: Session, course_id: str) -> bool:
    obj = session.get(TrainingCourse, course_id)
    if not obj:
        return False
    session.delete(obj)
    session.flush()
    return True


# ── TrainingRecord ─────────────────────────────────────

def list_records(
    session: Session,
    *,
    course_id: str | None = None,
    employee_id: str | None = None,
    department: str | None = None,
    training_type: str | None = None,
    passed: bool | None = None,
) -> list[TrainingRecord]:
    q = session.query(TrainingRecord)
    if course_id:
        q = q.filter(TrainingRecord.course_id == course_id)
    if employee_id:
        q = q.filter(TrainingRecord.employee_id == employee_id)
    if department:
        q = q.filter(TrainingRecord.department == department)
    if training_type:
        q = q.filter(TrainingRecord.training_type == training_type)
    if passed is not None:
        q = q.filter(TrainingRecord.passed == passed)
    return q.order_by(TrainingRecord.record_no.desc()).all()


def get_record(session: Session, record_id: str) -> TrainingRecord | None:
    return session.get(TrainingRecord, record_id)


def get_record_by_no(session: Session, record_no: str) -> TrainingRecord | None:
    return session.query(TrainingRecord).filter(
        TrainingRecord.record_no == record_no,
    ).first()


def create_record(session: Session, data: dict) -> TrainingRecord:
    obj = TrainingRecord(**data)
    session.add(obj)
    session.flush()
    return obj


def update_record(
    session: Session, record_id: str, data: dict,
) -> TrainingRecord | None:
    obj = session.get(TrainingRecord, record_id)
    if not obj:
        return None
    for k, v in data.items():
        if v is not None:
            setattr(obj, k, v)
    session.flush()
    return obj


def delete_record(session: Session, record_id: str) -> bool:
    obj = session.get(TrainingRecord, record_id)
    if not obj:
        return False
    session.delete(obj)
    session.flush()
    return True
