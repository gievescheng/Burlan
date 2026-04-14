from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import database
from ..schemas.review import (
    ManagementReviewCreate, ManagementReviewOut, ManagementReviewUpdate,
    ReviewActionCreate, ReviewActionOut, ReviewActionUpdate,
)
from ..services import review as svc

router = APIRouter()


# ── ManagementReview ───────────────────────────────────

@router.get("/management-reviews", response_model=list[ManagementReviewOut])
def list_reviews(status: str | None = None, meeting_type: str | None = None):
    with database.session_scope() as s:
        return svc.list_reviews(s, status=status, meeting_type=meeting_type)


@router.get("/management-reviews/{review_id}", response_model=ManagementReviewOut)
def get_review(review_id: str):
    with database.session_scope() as s:
        row = svc.get_review(s, review_id)
    if not row:
        raise HTTPException(404, "Review not found")
    return row


@router.post("/management-reviews", response_model=ManagementReviewOut, status_code=201)
def create_review(body: ManagementReviewCreate):
    try:
        with database.session_scope() as s:
            return svc.create_review(s, body.model_dump())
    except ValueError as e:
        msg = str(e)
        if "already exists" in msg:
            raise HTTPException(409, msg)
        raise HTTPException(422, msg)


@router.patch("/management-reviews/{review_id}", response_model=ManagementReviewOut)
def update_review(review_id: str, body: ManagementReviewUpdate):
    try:
        with database.session_scope() as s:
            row = svc.update_review(s, review_id, body.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(422, str(e))
    if not row:
        raise HTTPException(404, "Review not found")
    return row


@router.delete("/management-reviews/{review_id}", status_code=204)
def delete_review(review_id: str):
    with database.session_scope() as s:
        if not svc.delete_review(s, review_id):
            raise HTTPException(404, "Review not found")


# ── ManagementReviewAction ─────────────────────────────

@router.get("/review-actions", response_model=list[ReviewActionOut])
def list_actions(
    review_id: str | None = None,
    status: str | None = None,
    action_type: str | None = None,
    responsible_person: str | None = None,
):
    with database.session_scope() as s:
        return svc.list_actions(
            s, review_id=review_id, status=status,
            action_type=action_type, responsible_person=responsible_person,
        )


@router.get("/review-actions/{action_id}", response_model=ReviewActionOut)
def get_action(action_id: str):
    with database.session_scope() as s:
        row = svc.get_action(s, action_id)
    if not row:
        raise HTTPException(404, "Action not found")
    return row


@router.post("/review-actions", response_model=ReviewActionOut, status_code=201)
def create_action(body: ReviewActionCreate):
    try:
        with database.session_scope() as s:
            return svc.create_action(s, body.model_dump())
    except ValueError as e:
        msg = str(e)
        if "already exists" in msg:
            raise HTTPException(409, msg)
        raise HTTPException(422, msg)


@router.patch("/review-actions/{action_id}", response_model=ReviewActionOut)
def update_action(action_id: str, body: ReviewActionUpdate):
    try:
        with database.session_scope() as s:
            row = svc.update_action(s, action_id, body.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(422, str(e))
    if not row:
        raise HTTPException(404, "Action not found")
    return row


@router.delete("/review-actions/{action_id}", status_code=204)
def delete_action(action_id: str):
    with database.session_scope() as s:
        if not svc.delete_action(s, action_id):
            raise HTTPException(404, "Action not found")
