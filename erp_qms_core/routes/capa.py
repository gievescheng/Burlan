from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import database
from ..schemas.capa import (
    CAPACreate, CAPAOut, CAPAUpdate,
    CustomerComplaintCreate, CustomerComplaintOut, CustomerComplaintUpdate,
)
from ..services import capa as svc

router = APIRouter()


# ── CustomerComplaint ──────────────────────────────────

@router.get("/complaints", response_model=list[CustomerComplaintOut])
def list_complaints(
    status: str | None = None,
    severity: str | None = None,
    complaint_type: str | None = None,
    customer_id: str | None = None,
    product_id: str | None = None,
    requires_capa: bool | None = None,
    lot_no: str | None = None,
):
    with database.session_scope() as s:
        return svc.list_complaints(
            s, status=status, severity=severity, complaint_type=complaint_type,
            customer_id=customer_id, product_id=product_id,
            requires_capa=requires_capa, lot_no=lot_no,
        )


@router.get("/complaints/{complaint_id}", response_model=CustomerComplaintOut)
def get_complaint(complaint_id: str):
    with database.session_scope() as s:
        row = svc.get_complaint(s, complaint_id)
    if not row:
        raise HTTPException(404, "Complaint not found")
    return row


@router.post("/complaints", response_model=CustomerComplaintOut, status_code=201)
def create_complaint(body: CustomerComplaintCreate):
    try:
        with database.session_scope() as s:
            return svc.create_complaint(s, body.model_dump())
    except ValueError as e:
        msg = str(e)
        if "already exists" in msg:
            raise HTTPException(409, msg)
        raise HTTPException(422, msg)


@router.patch("/complaints/{complaint_id}", response_model=CustomerComplaintOut)
def update_complaint(complaint_id: str, body: CustomerComplaintUpdate):
    try:
        with database.session_scope() as s:
            row = svc.update_complaint(s, complaint_id, body.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(422, str(e))
    if not row:
        raise HTTPException(404, "Complaint not found")
    return row


@router.delete("/complaints/{complaint_id}", status_code=204)
def delete_complaint(complaint_id: str):
    with database.session_scope() as s:
        if not svc.delete_complaint(s, complaint_id):
            raise HTTPException(404, "Complaint not found")


# ── CAPA ───────────────────────────────────────────────

@router.get("/capas", response_model=list[CAPAOut])
def list_capas(
    status: str | None = None,
    capa_type: str | None = None,
    source_type: str | None = None,
    severity: str | None = None,
    assigned_to: str | None = None,
    ncr_id: str | None = None,
    complaint_id: str | None = None,
    effectiveness_verified: bool | None = None,
):
    with database.session_scope() as s:
        return svc.list_capas(
            s, status=status, capa_type=capa_type, source_type=source_type,
            severity=severity, assigned_to=assigned_to,
            ncr_id=ncr_id, complaint_id=complaint_id,
            effectiveness_verified=effectiveness_verified,
        )


@router.get("/capas/{capa_id}", response_model=CAPAOut)
def get_capa(capa_id: str):
    with database.session_scope() as s:
        row = svc.get_capa(s, capa_id)
    if not row:
        raise HTTPException(404, "CAPA not found")
    return row


@router.post("/capas", response_model=CAPAOut, status_code=201)
def create_capa(body: CAPACreate):
    try:
        with database.session_scope() as s:
            return svc.create_capa(s, body.model_dump())
    except ValueError as e:
        msg = str(e)
        if "already exists" in msg:
            raise HTTPException(409, msg)
        raise HTTPException(422, msg)


@router.patch("/capas/{capa_id}", response_model=CAPAOut)
def update_capa(capa_id: str, body: CAPAUpdate):
    try:
        with database.session_scope() as s:
            row = svc.update_capa(s, capa_id, body.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(422, str(e))
    if not row:
        raise HTTPException(404, "CAPA not found")
    return row


@router.delete("/capas/{capa_id}", status_code=204)
def delete_capa(capa_id: str):
    with database.session_scope() as s:
        if not svc.delete_capa(s, capa_id):
            raise HTTPException(404, "CAPA not found")
