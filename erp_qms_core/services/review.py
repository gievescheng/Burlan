from __future__ import annotations

from sqlalchemy.orm import Session

from ..domain.transitions import validate_status_transition
from ..repositories import capa as capa_repo
from ..repositories import review as repo

VALID_MEETING_TYPES = {"regular", "emergency", "follow_up"}
VALID_ACTION_TYPES = {"improvement", "qms_change", "resource"}

# ISO §9.3.2 要求的輸入摘要欄位
REQUIRED_INPUT_FIELDS_FOR_CLOSE = [
    "qms_performance_summary",
    "audit_results_summary",
    "nc_and_ca_summary",
    "customer_satisfaction_summary",
]


# ── ManagementReview ───────────────────────────────────

def list_reviews(
    session: Session,
    status: str | None = None,
    meeting_type: str | None = None,
) -> list[dict]:
    rows = repo.list_reviews(session, status=status, meeting_type=meeting_type)
    return [_review_to_dict(r) for r in rows]


def get_review(session: Session, review_id: str) -> dict | None:
    row = repo.get_review(session, review_id)
    return _review_to_dict(row) if row else None


def create_review(session: Session, data: dict) -> dict:
    if repo.get_review_by_no(session, data["review_no"]):
        raise ValueError(f"Review '{data['review_no']}' already exists")
    if data.get("meeting_type") and data["meeting_type"] not in VALID_MEETING_TYPES:
        raise ValueError(
            f"Invalid meeting_type. Allowed: {sorted(VALID_MEETING_TYPES)}"
        )
    return _review_to_dict(repo.create_review(session, data))


def update_review(session: Session, review_id: str, data: dict) -> dict | None:
    current = repo.get_review(session, review_id)
    if not current:
        return None
    if "meeting_type" in data and data["meeting_type"] is not None:
        if data["meeting_type"] not in VALID_MEETING_TYPES:
            raise ValueError(
                f"Invalid meeting_type. Allowed: {sorted(VALID_MEETING_TYPES)}"
            )
    if "status" in data and data["status"] is not None:
        err = validate_status_transition(
            "management_review", current.status, data["status"],
        )
        if err:
            raise ValueError(err)
        # ISO §9.3.2 — 結案前必須完成核心輸入
        if data["status"] == "closed":
            missing = []
            for field in REQUIRED_INPUT_FIELDS_FOR_CLOSE:
                value = data.get(field, getattr(current, field))
                if not value or not str(value).strip():
                    missing.append(field)
            if missing:
                raise ValueError(
                    "Cannot close review: missing required §9.3.2 inputs: "
                    f"{missing}"
                )
    row = repo.update_review(session, review_id, data)
    return _review_to_dict(row) if row else None


def delete_review(session: Session, review_id: str) -> bool:
    return repo.delete_review(session, review_id)


# ── ManagementReviewAction ─────────────────────────────

def list_actions(
    session: Session,
    review_id: str | None = None,
    status: str | None = None,
    action_type: str | None = None,
    responsible_person: str | None = None,
) -> list[dict]:
    rows = repo.list_actions(
        session, review_id=review_id, status=status,
        action_type=action_type, responsible_person=responsible_person,
    )
    return [_action_to_dict(r) for r in rows]


def get_action(session: Session, action_id: str) -> dict | None:
    row = repo.get_action(session, action_id)
    return _action_to_dict(row) if row else None


def create_action(session: Session, data: dict) -> dict:
    if not repo.get_review(session, data["review_id"]):
        raise ValueError(f"Review '{data['review_id']}' not found")
    if repo.get_action_by_no(session, data["action_no"]):
        raise ValueError(f"Action '{data['action_no']}' already exists")
    if data.get("action_type") and data["action_type"] not in VALID_ACTION_TYPES:
        raise ValueError(
            f"Invalid action_type. Allowed: {sorted(VALID_ACTION_TYPES)}"
        )
    if data.get("capa_id"):
        if not capa_repo.get_capa(session, data["capa_id"]):
            raise ValueError(f"CAPA '{data['capa_id']}' not found")
    return _action_to_dict(repo.create_action(session, data))


def update_action(session: Session, action_id: str, data: dict) -> dict | None:
    current = repo.get_action(session, action_id)
    if not current:
        return None
    if "action_type" in data and data["action_type"] is not None:
        if data["action_type"] not in VALID_ACTION_TYPES:
            raise ValueError(
                f"Invalid action_type. Allowed: {sorted(VALID_ACTION_TYPES)}"
            )
    if data.get("capa_id"):
        if not capa_repo.get_capa(session, data["capa_id"]):
            raise ValueError(f"CAPA '{data['capa_id']}' not found")
    if "status" in data and data["status"] is not None:
        err = validate_status_transition(
            "review_action", current.status, data["status"],
        )
        if err:
            raise ValueError(err)
    row = repo.update_action(session, action_id, data)
    return _action_to_dict(row) if row else None


def delete_action(session: Session, action_id: str) -> bool:
    return repo.delete_action(session, action_id)


# ── helpers ────────────────────────────────────────────

def _review_to_dict(row) -> dict:
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}


def _action_to_dict(row) -> dict:
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}
