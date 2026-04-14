from __future__ import annotations

from sqlalchemy.orm import Session

from ..models.review import ManagementReview, ManagementReviewAction


# ── ManagementReview ───────────────────────────────────

def list_reviews(
    session: Session,
    *,
    status: str | None = None,
    meeting_type: str | None = None,
) -> list[ManagementReview]:
    q = session.query(ManagementReview)
    if status:
        q = q.filter(ManagementReview.status == status)
    if meeting_type:
        q = q.filter(ManagementReview.meeting_type == meeting_type)
    return q.order_by(ManagementReview.review_no.desc()).all()


def get_review(session: Session, review_id: str) -> ManagementReview | None:
    return session.get(ManagementReview, review_id)


def get_review_by_no(session: Session, review_no: str) -> ManagementReview | None:
    return session.query(ManagementReview).filter(
        ManagementReview.review_no == review_no,
    ).first()


def create_review(session: Session, data: dict) -> ManagementReview:
    obj = ManagementReview(**data)
    session.add(obj)
    session.flush()
    return obj


def update_review(
    session: Session, review_id: str, data: dict,
) -> ManagementReview | None:
    obj = session.get(ManagementReview, review_id)
    if not obj:
        return None
    for k, v in data.items():
        if v is not None:
            setattr(obj, k, v)
    session.flush()
    return obj


def delete_review(session: Session, review_id: str) -> bool:
    obj = session.get(ManagementReview, review_id)
    if not obj:
        return False
    session.delete(obj)
    session.flush()
    return True


# ── ManagementReviewAction ─────────────────────────────

def list_actions(
    session: Session,
    *,
    review_id: str | None = None,
    status: str | None = None,
    action_type: str | None = None,
    responsible_person: str | None = None,
) -> list[ManagementReviewAction]:
    q = session.query(ManagementReviewAction)
    if review_id:
        q = q.filter(ManagementReviewAction.review_id == review_id)
    if status:
        q = q.filter(ManagementReviewAction.status == status)
    if action_type:
        q = q.filter(ManagementReviewAction.action_type == action_type)
    if responsible_person:
        q = q.filter(ManagementReviewAction.responsible_person == responsible_person)
    return q.order_by(ManagementReviewAction.action_no.asc()).all()


def get_action(session: Session, action_id: str) -> ManagementReviewAction | None:
    return session.get(ManagementReviewAction, action_id)


def get_action_by_no(session: Session, action_no: str) -> ManagementReviewAction | None:
    return session.query(ManagementReviewAction).filter(
        ManagementReviewAction.action_no == action_no,
    ).first()


def create_action(session: Session, data: dict) -> ManagementReviewAction:
    obj = ManagementReviewAction(**data)
    session.add(obj)
    session.flush()
    return obj


def update_action(
    session: Session, action_id: str, data: dict,
) -> ManagementReviewAction | None:
    obj = session.get(ManagementReviewAction, action_id)
    if not obj:
        return None
    for k, v in data.items():
        if v is not None:
            setattr(obj, k, v)
    session.flush()
    return obj


def delete_action(session: Session, action_id: str) -> bool:
    obj = session.get(ManagementReviewAction, action_id)
    if not obj:
        return False
    session.delete(obj)
    session.flush()
    return True
