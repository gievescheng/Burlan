from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..domain.transitions import validate_status_transition
from ..repositories import document as repo

VALID_DOCUMENT_CATEGORIES = {
    "manual", "policy", "procedure", "work_instruction",
    "form", "record", "specification", "drawing",
}
VALID_CLASSIFICATIONS = {"controlled", "uncontrolled", "confidential"}
VALID_DOCUMENT_STATUSES = {"active", "inactive", "archived"}


# ── Document ───────────────────────────────────────────

def list_documents(
    session: Session,
    status: str | None = None,
    category: str | None = None,
    classification: str | None = None,
    department: str | None = None,
) -> list[dict]:
    rows = repo.list_documents(
        session, status=status, category=category,
        classification=classification, department=department,
    )
    return [_doc_to_dict(r) for r in rows]


def get_document(session: Session, document_id: str) -> dict | None:
    row = repo.get_document(session, document_id)
    return _doc_to_dict(row) if row else None


def create_document(session: Session, data: dict) -> dict:
    if repo.get_document_by_no(session, data["document_no"]):
        raise ValueError(f"Document '{data['document_no']}' already exists")
    _validate_document_enums(data)
    return _doc_to_dict(repo.create_document(session, data))


def update_document(session: Session, document_id: str, data: dict) -> dict | None:
    current = repo.get_document(session, document_id)
    if not current:
        return None
    _validate_document_enums(data)
    row = repo.update_document(session, document_id, data)
    return _doc_to_dict(row) if row else None


def delete_document(session: Session, document_id: str) -> bool:
    return repo.delete_document(session, document_id)


# ── DocumentRevision ───────────────────────────────────

def list_revisions(
    session: Session,
    document_id: str | None = None,
    status: str | None = None,
    is_current: bool | None = None,
) -> list[dict]:
    rows = repo.list_revisions(
        session, document_id=document_id, status=status, is_current=is_current,
    )
    return [_rev_to_dict(r) for r in rows]


def get_revision(session: Session, revision_id: str) -> dict | None:
    row = repo.get_revision(session, revision_id)
    return _rev_to_dict(row) if row else None


def create_revision(session: Session, data: dict) -> dict:
    doc = repo.get_document(session, data["document_id"])
    if not doc:
        raise ValueError(f"Document '{data['document_id']}' not found")
    if repo.get_revision_by_doc_rev(session, data["document_id"], data["revision"]):
        raise ValueError(
            f"Revision '{data['revision']}' already exists for document"
        )
    return _rev_to_dict(repo.create_revision(session, data))


def update_revision(session: Session, revision_id: str, data: dict) -> dict | None:
    current = repo.get_revision(session, revision_id)
    if not current:
        return None

    target_status = data.get("status") if "status" in data else None
    if target_status is not None:
        err = validate_status_transition(
            "document_revision", current.status, target_status,
        )
        if err:
            raise ValueError(err)
        # ISO §7.5.2 b) approved 必須有審查與核准紀錄
        if target_status == "approved":
            reviewed_by = data.get("reviewed_by", current.reviewed_by)
            approved_by = data.get("approved_by", current.approved_by)
            if not reviewed_by or not approved_by:
                raise ValueError(
                    "Cannot approve revision: reviewed_by and approved_by "
                    "must both be set (ISO 9001 §7.5.2 b)"
                )
            if "approved_at" not in data or data["approved_at"] is None:
                data["approved_at"] = datetime.now(timezone.utc)
        # effective — 此版本成為 current，取代同文件舊版本
        if target_status == "effective":
            repo.clear_current_flag(session, current.document_id)
            data["is_current"] = True
            doc = repo.get_document(session, current.document_id)
            if doc:
                repo.update_document(
                    session, doc.id,
                    {"current_revision": data.get("revision", current.revision)},
                )
            # 舊有效版自動轉為 superseded
            old_effective = [
                r for r in repo.list_revisions(
                    session, document_id=current.document_id, status="effective",
                )
                if r.id != revision_id
            ]
            for r in old_effective:
                repo.update_revision(session, r.id, {
                    "status": "superseded",
                    "is_current": False,
                    "obsolete_date": data.get("effective_date", current.effective_date),
                })
        # obsolete / superseded — 清除 is_current
        if target_status in {"superseded", "obsolete"}:
            data["is_current"] = False

    row = repo.update_revision(session, revision_id, data)
    return _rev_to_dict(row) if row else None


def delete_revision(session: Session, revision_id: str) -> bool:
    return repo.delete_revision(session, revision_id)


# ── helpers ────────────────────────────────────────────

def _validate_document_enums(data: dict) -> None:
    if "category" in data and data["category"] is not None:
        if data["category"] not in VALID_DOCUMENT_CATEGORIES:
            raise ValueError(
                f"Invalid category. Allowed: {sorted(VALID_DOCUMENT_CATEGORIES)}"
            )
    if "classification" in data and data["classification"] is not None:
        if data["classification"] not in VALID_CLASSIFICATIONS:
            raise ValueError(
                f"Invalid classification. Allowed: {sorted(VALID_CLASSIFICATIONS)}"
            )
    if "status" in data and data["status"] is not None:
        if data["status"] not in VALID_DOCUMENT_STATUSES:
            raise ValueError(
                f"Invalid status. Allowed: {sorted(VALID_DOCUMENT_STATUSES)}"
            )


def _doc_to_dict(row) -> dict:
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}


def _rev_to_dict(row) -> dict:
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}
