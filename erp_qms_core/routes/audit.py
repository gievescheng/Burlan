from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import database
from ..schemas.audit import (
    AuditFindingCreate, AuditFindingOut, AuditFindingUpdate,
    InternalAuditCreate, InternalAuditOut, InternalAuditUpdate,
)
from ..services import audit as svc

router = APIRouter()


# ── InternalAudit ──────────────────────────────────────

@router.get("/audits", response_model=list[InternalAuditOut])
def list_audits(
    status: str | None = None,
    audit_type: str | None = None,
    scope: str | None = None,
    department: str | None = None,
):
    with database.session_scope() as s:
        return svc.list_audits(
            s, status=status, audit_type=audit_type,
            scope=scope, department=department,
        )


@router.get("/audits/{audit_id}", response_model=InternalAuditOut)
def get_audit(audit_id: str):
    with database.session_scope() as s:
        row = svc.get_audit(s, audit_id)
    if not row:
        raise HTTPException(404, "Audit not found")
    return row


@router.post("/audits", response_model=InternalAuditOut, status_code=201)
def create_audit(body: InternalAuditCreate):
    try:
        with database.session_scope() as s:
            return svc.create_audit(s, body.model_dump())
    except ValueError as e:
        msg = str(e)
        if "already exists" in msg:
            raise HTTPException(409, msg)
        raise HTTPException(422, msg)


@router.patch("/audits/{audit_id}", response_model=InternalAuditOut)
def update_audit(audit_id: str, body: InternalAuditUpdate):
    try:
        with database.session_scope() as s:
            row = svc.update_audit(s, audit_id, body.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(422, str(e))
    if not row:
        raise HTTPException(404, "Audit not found")
    return row


@router.delete("/audits/{audit_id}", status_code=204)
def delete_audit(audit_id: str):
    with database.session_scope() as s:
        if not svc.delete_audit(s, audit_id):
            raise HTTPException(404, "Audit not found")


# ── AuditFinding ───────────────────────────────────────

@router.get("/audit-findings", response_model=list[AuditFindingOut])
def list_findings(
    audit_id: str | None = None,
    status: str | None = None,
    finding_type: str | None = None,
    requires_capa: bool | None = None,
    clause: str | None = None,
):
    with database.session_scope() as s:
        return svc.list_findings(
            s, audit_id=audit_id, status=status,
            finding_type=finding_type, requires_capa=requires_capa, clause=clause,
        )


@router.get("/audit-findings/{finding_id}", response_model=AuditFindingOut)
def get_finding(finding_id: str):
    with database.session_scope() as s:
        row = svc.get_finding(s, finding_id)
    if not row:
        raise HTTPException(404, "Finding not found")
    return row


@router.post("/audit-findings", response_model=AuditFindingOut, status_code=201)
def create_finding(body: AuditFindingCreate):
    try:
        with database.session_scope() as s:
            return svc.create_finding(s, body.model_dump())
    except ValueError as e:
        msg = str(e)
        if "already exists" in msg:
            raise HTTPException(409, msg)
        raise HTTPException(422, msg)


@router.patch("/audit-findings/{finding_id}", response_model=AuditFindingOut)
def update_finding(finding_id: str, body: AuditFindingUpdate):
    try:
        with database.session_scope() as s:
            row = svc.update_finding(s, finding_id, body.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(422, str(e))
    if not row:
        raise HTTPException(404, "Finding not found")
    return row


@router.delete("/audit-findings/{finding_id}", status_code=204)
def delete_finding(finding_id: str):
    with database.session_scope() as s:
        if not svc.delete_finding(s, finding_id):
            raise HTTPException(404, "Finding not found")
