from __future__ import annotations

from datetime import date
from dateutil.relativedelta import relativedelta

from sqlalchemy.orm import Session

from ..repositories import training as repo
from ..repositories import document as doc_repo

VALID_COURSE_CATEGORIES = {
    "orientation", "technical", "safety", "quality",
    "iso_awareness", "compliance", "other",
}
VALID_COURSE_STATUSES = {"active", "inactive", "archived"}
VALID_TRAINING_TYPES = {
    "classroom", "on_the_job", "e_learning", "external", "self_study",
}


# ── TrainingCourse ─────────────────────────────────────

def list_courses(
    session: Session,
    status: str | None = None,
    category: str | None = None,
) -> list[dict]:
    rows = repo.list_courses(session, status=status, category=category)
    return [_course_to_dict(r) for r in rows]


def get_course(session: Session, course_id: str) -> dict | None:
    row = repo.get_course(session, course_id)
    return _course_to_dict(row) if row else None


def create_course(session: Session, data: dict) -> dict:
    if repo.get_course_by_no(session, data["course_no"]):
        raise ValueError(f"Course '{data['course_no']}' already exists")
    _validate_course_enums(data)
    if data.get("related_document_id"):
        if not doc_repo.get_document(session, data["related_document_id"]):
            raise ValueError(
                f"Related document '{data['related_document_id']}' not found"
            )
    return _course_to_dict(repo.create_course(session, data))


def update_course(session: Session, course_id: str, data: dict) -> dict | None:
    current = repo.get_course(session, course_id)
    if not current:
        return None
    _validate_course_enums(data)
    if data.get("related_document_id"):
        if not doc_repo.get_document(session, data["related_document_id"]):
            raise ValueError(
                f"Related document '{data['related_document_id']}' not found"
            )
    row = repo.update_course(session, course_id, data)
    return _course_to_dict(row) if row else None


def delete_course(session: Session, course_id: str) -> bool:
    return repo.delete_course(session, course_id)


# ── TrainingRecord ─────────────────────────────────────

def list_records(
    session: Session,
    course_id: str | None = None,
    employee_id: str | None = None,
    department: str | None = None,
    training_type: str | None = None,
    passed: bool | None = None,
) -> list[dict]:
    rows = repo.list_records(
        session, course_id=course_id, employee_id=employee_id,
        department=department, training_type=training_type, passed=passed,
    )
    return [_record_to_dict(r) for r in rows]


def get_record(session: Session, record_id: str) -> dict | None:
    row = repo.get_record(session, record_id)
    return _record_to_dict(row) if row else None


def create_record(session: Session, data: dict) -> dict:
    course = repo.get_course(session, data["course_id"])
    if not course:
        raise ValueError(f"Course '{data['course_id']}' not found")
    if repo.get_record_by_no(session, data["record_no"]):
        raise ValueError(f"Record '{data['record_no']}' already exists")
    if data.get("training_type") and data["training_type"] not in VALID_TRAINING_TYPES:
        raise ValueError(
            f"Invalid training_type. Allowed: {sorted(VALID_TRAINING_TYPES)}"
        )
    _auto_judge_and_expire(data, course)
    return _record_to_dict(repo.create_record(session, data))


def update_record(session: Session, record_id: str, data: dict) -> dict | None:
    current = repo.get_record(session, record_id)
    if not current:
        return None
    if "training_type" in data and data["training_type"] is not None:
        if data["training_type"] not in VALID_TRAINING_TYPES:
            raise ValueError(
                f"Invalid training_type. Allowed: {sorted(VALID_TRAINING_TYPES)}"
            )
    course = repo.get_course(session, current.course_id)
    if course is not None:
        # 若分數或完成日期被更新則重新判定
        score_in = "score" in data and data["score"] is not None
        completed_in = "completed_date" in data and data["completed_date"] is not None
        if score_in or completed_in:
            merged = dict(data)
            merged.setdefault("score", current.score)
            merged.setdefault("completed_date", current.completed_date)
            _auto_judge_and_expire(merged, course, preserve_explicit_passed="passed" in data)
            data["passed"] = merged["passed"]
            if "expiry_date" in merged:
                data["expiry_date"] = merged["expiry_date"]
    row = repo.update_record(session, record_id, data)
    return _record_to_dict(row) if row else None


def delete_record(session: Session, record_id: str) -> bool:
    return repo.delete_record(session, record_id)


# ── helpers ────────────────────────────────────────────

def _validate_course_enums(data: dict) -> None:
    if "category" in data and data["category"] is not None:
        if data["category"] not in VALID_COURSE_CATEGORIES:
            raise ValueError(
                f"Invalid category. Allowed: {sorted(VALID_COURSE_CATEGORIES)}"
            )
    if "status" in data and data["status"] is not None:
        if data["status"] not in VALID_COURSE_STATUSES:
            raise ValueError(
                f"Invalid status. Allowed: {sorted(VALID_COURSE_STATUSES)}"
            )


def _auto_judge_and_expire(
    data: dict, course, *, preserve_explicit_passed: bool = False,
) -> None:
    """依課程 passing_score 自動判定 passed，依 validity_months 自動算 expiry_date"""
    score = data.get("score", 0.0) or 0.0
    if not preserve_explicit_passed:
        if course.passing_score > 0:
            data["passed"] = score >= course.passing_score
        else:
            data.setdefault("passed", data.get("passed", False))
    # 自動計算到期日（僅 validity_months > 0 且有 completed_date 且通過）
    completed: date | None = data.get("completed_date")
    if (
        course.validity_months
        and course.validity_months > 0
        and completed
        and data.get("passed", False)
        and not data.get("expiry_date")
    ):
        data["expiry_date"] = completed + relativedelta(months=course.validity_months)


def _course_to_dict(row) -> dict:
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}


def _record_to_dict(row) -> dict:
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}
