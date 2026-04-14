from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import database
from ..schemas.document import (
    DocumentCreate, DocumentOut, DocumentUpdate,
    DocumentRevisionCreate, DocumentRevisionOut, DocumentRevisionUpdate,
)
from ..services import document as svc

router = APIRouter()


# ── Document ───────────────────────────────────────────

@router.get("/documents", response_model=list[DocumentOut])
def list_documents(
    status: str | None = None,
    category: str | None = None,
    classification: str | None = None,
    department: str | None = None,
):
    with database.session_scope() as s:
        return svc.list_documents(
            s, status=status, category=category,
            classification=classification, department=department,
        )


@router.get("/documents/{document_id}", response_model=DocumentOut)
def get_document(document_id: str):
    with database.session_scope() as s:
        row = svc.get_document(s, document_id)
    if not row:
        raise HTTPException(404, "Document not found")
    return row


@router.post("/documents", response_model=DocumentOut, status_code=201)
def create_document(body: DocumentCreate):
    try:
        with database.session_scope() as s:
            return svc.create_document(s, body.model_dump())
    except ValueError as e:
        msg = str(e)
        if "already exists" in msg:
            raise HTTPException(409, msg)
        raise HTTPException(422, msg)


@router.patch("/documents/{document_id}", response_model=DocumentOut)
def update_document(document_id: str, body: DocumentUpdate):
    try:
        with database.session_scope() as s:
            row = svc.update_document(s, document_id, body.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(422, str(e))
    if not row:
        raise HTTPException(404, "Document not found")
    return row


@router.delete("/documents/{document_id}", status_code=204)
def delete_document(document_id: str):
    with database.session_scope() as s:
        if not svc.delete_document(s, document_id):
            raise HTTPException(404, "Document not found")


# ── DocumentRevision ───────────────────────────────────

@router.get("/document-revisions", response_model=list[DocumentRevisionOut])
def list_revisions(
    document_id: str | None = None,
    status: str | None = None,
    is_current: bool | None = None,
):
    with database.session_scope() as s:
        return svc.list_revisions(
            s, document_id=document_id, status=status, is_current=is_current,
        )


@router.get("/document-revisions/{revision_id}", response_model=DocumentRevisionOut)
def get_revision(revision_id: str):
    with database.session_scope() as s:
        row = svc.get_revision(s, revision_id)
    if not row:
        raise HTTPException(404, "Revision not found")
    return row


@router.post("/document-revisions", response_model=DocumentRevisionOut, status_code=201)
def create_revision(body: DocumentRevisionCreate):
    try:
        with database.session_scope() as s:
            return svc.create_revision(s, body.model_dump())
    except ValueError as e:
        msg = str(e)
        if "already exists" in msg:
            raise HTTPException(409, msg)
        raise HTTPException(422, msg)


@router.patch("/document-revisions/{revision_id}", response_model=DocumentRevisionOut)
def update_revision(revision_id: str, body: DocumentRevisionUpdate):
    try:
        with database.session_scope() as s:
            row = svc.update_revision(s, revision_id, body.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(422, str(e))
    if not row:
        raise HTTPException(404, "Revision not found")
    return row


@router.delete("/document-revisions/{revision_id}", status_code=204)
def delete_revision(revision_id: str):
    with database.session_scope() as s:
        if not svc.delete_revision(s, revision_id):
            raise HTTPException(404, "Revision not found")
