from __future__ import annotations

from sqlalchemy.orm import Session

from ..models.document import Document, DocumentRevision


# ── Document ───────────────────────────────────────────

def list_documents(
    session: Session,
    *,
    status: str | None = None,
    category: str | None = None,
    classification: str | None = None,
    department: str | None = None,
) -> list[Document]:
    q = session.query(Document)
    if status:
        q = q.filter(Document.status == status)
    if category:
        q = q.filter(Document.category == category)
    if classification:
        q = q.filter(Document.classification == classification)
    if department:
        q = q.filter(Document.department == department)
    return q.order_by(Document.document_no.asc()).all()


def get_document(session: Session, document_id: str) -> Document | None:
    return session.get(Document, document_id)


def get_document_by_no(session: Session, document_no: str) -> Document | None:
    return session.query(Document).filter(Document.document_no == document_no).first()


def create_document(session: Session, data: dict) -> Document:
    obj = Document(**data)
    session.add(obj)
    session.flush()
    return obj


def update_document(session: Session, document_id: str, data: dict) -> Document | None:
    obj = session.get(Document, document_id)
    if not obj:
        return None
    for k, v in data.items():
        if v is not None:
            setattr(obj, k, v)
    session.flush()
    return obj


def delete_document(session: Session, document_id: str) -> bool:
    obj = session.get(Document, document_id)
    if not obj:
        return False
    session.delete(obj)
    session.flush()
    return True


# ── DocumentRevision ───────────────────────────────────

def list_revisions(
    session: Session,
    *,
    document_id: str | None = None,
    status: str | None = None,
    is_current: bool | None = None,
) -> list[DocumentRevision]:
    q = session.query(DocumentRevision)
    if document_id:
        q = q.filter(DocumentRevision.document_id == document_id)
    if status:
        q = q.filter(DocumentRevision.status == status)
    if is_current is not None:
        q = q.filter(DocumentRevision.is_current == is_current)
    return q.order_by(
        DocumentRevision.document_id.asc(), DocumentRevision.revision.asc(),
    ).all()


def get_revision(session: Session, revision_id: str) -> DocumentRevision | None:
    return session.get(DocumentRevision, revision_id)


def get_revision_by_doc_rev(
    session: Session, document_id: str, revision: str,
) -> DocumentRevision | None:
    return session.query(DocumentRevision).filter(
        DocumentRevision.document_id == document_id,
        DocumentRevision.revision == revision,
    ).first()


def create_revision(session: Session, data: dict) -> DocumentRevision:
    obj = DocumentRevision(**data)
    session.add(obj)
    session.flush()
    return obj


def update_revision(
    session: Session, revision_id: str, data: dict,
) -> DocumentRevision | None:
    obj = session.get(DocumentRevision, revision_id)
    if not obj:
        return None
    for k, v in data.items():
        if v is not None:
            setattr(obj, k, v)
    session.flush()
    return obj


def delete_revision(session: Session, revision_id: str) -> bool:
    obj = session.get(DocumentRevision, revision_id)
    if not obj:
        return False
    session.delete(obj)
    session.flush()
    return True


def clear_current_flag(session: Session, document_id: str) -> None:
    """將某文件所有版本的 is_current 清為 False（用於切換 current）"""
    session.query(DocumentRevision).filter(
        DocumentRevision.document_id == document_id,
    ).update({"is_current": False})
    session.flush()
