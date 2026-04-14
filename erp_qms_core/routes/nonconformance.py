from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import database
from ..schemas.nonconformance import (
    NCRCreate, NCROut, NCRUpdate,
    ReworkOrderInput, ReworkOrderOut, ReworkOrderUpdate,
)
from ..services import nonconformance as svc

router = APIRouter()


# ── NCR ────────────────────────────────────────────────

@router.get("/ncrs", response_model=list[NCROut])
def list_ncrs(
    status: str | None = None,
    severity: str | None = None,
    category: str | None = None,
    disposition: str | None = None,
    work_order_id: str | None = None,
    product_id: str | None = None,
    inspection_lot_id: str | None = None,
    requires_capa: bool | None = None,
    lot_no: str | None = None,
):
    with database.session_scope() as s:
        return svc.list_ncrs(
            s, status=status, severity=severity, category=category,
            disposition=disposition, work_order_id=work_order_id,
            product_id=product_id, inspection_lot_id=inspection_lot_id,
            requires_capa=requires_capa, lot_no=lot_no,
        )


@router.get("/ncrs/{ncr_id}", response_model=NCROut)
def get_ncr(ncr_id: str):
    with database.session_scope() as s:
        row = svc.get_ncr(s, ncr_id)
    if not row:
        raise HTTPException(404, "NCR not found")
    return row


@router.post("/ncrs", response_model=NCROut, status_code=201)
def create_ncr(body: NCRCreate):
    try:
        with database.session_scope() as s:
            return svc.create_ncr(s, body.model_dump())
    except ValueError as e:
        msg = str(e)
        if "already exists" in msg:
            raise HTTPException(409, msg)
        raise HTTPException(422, msg)


@router.patch("/ncrs/{ncr_id}", response_model=NCROut)
def update_ncr(ncr_id: str, body: NCRUpdate):
    try:
        with database.session_scope() as s:
            row = svc.update_ncr(s, ncr_id, body.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(422, str(e))
    if not row:
        raise HTTPException(404, "NCR not found")
    return row


@router.delete("/ncrs/{ncr_id}", status_code=204)
def delete_ncr(ncr_id: str):
    with database.session_scope() as s:
        if not svc.delete_ncr(s, ncr_id):
            raise HTTPException(404, "NCR not found")


# ── ReworkOrder ────────────────────────────────────────

@router.get("/rework-orders", response_model=list[ReworkOrderOut])
def list_rework_orders(
    ncr_id: str | None = None,
    work_order_id: str | None = None,
    status: str | None = None,
    result: str | None = None,
):
    with database.session_scope() as s:
        return svc.list_rework_orders(
            s, ncr_id=ncr_id, work_order_id=work_order_id,
            status=status, result=result,
        )


@router.get("/rework-orders/{rework_id}", response_model=ReworkOrderOut)
def get_rework_order(rework_id: str):
    with database.session_scope() as s:
        row = svc.get_rework_order(s, rework_id)
    if not row:
        raise HTTPException(404, "Rework order not found")
    return row


@router.post("/ncrs/{ncr_id}/rework-orders", response_model=ReworkOrderOut, status_code=201)
def create_rework_order(ncr_id: str, body: ReworkOrderInput):
    try:
        with database.session_scope() as s:
            return svc.create_rework_order(s, ncr_id, body.model_dump())
    except LookupError as e:
        raise HTTPException(404, str(e))
    except ValueError as e:
        msg = str(e)
        if "already exists" in msg:
            raise HTTPException(409, msg)
        raise HTTPException(422, msg)


@router.patch("/rework-orders/{rework_id}", response_model=ReworkOrderOut)
def update_rework_order(rework_id: str, body: ReworkOrderUpdate):
    try:
        with database.session_scope() as s:
            row = svc.update_rework_order(s, rework_id, body.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(422, str(e))
    if not row:
        raise HTTPException(404, "Rework order not found")
    return row


@router.delete("/rework-orders/{rework_id}", status_code=204)
def delete_rework_order(rework_id: str):
    with database.session_scope() as s:
        if not svc.delete_rework_order(s, rework_id):
            raise HTTPException(404, "Rework order not found")
