from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import database
from ..schemas.inspection import (
    InspectionLotCreate, InspectionLotOut, InspectionLotUpdate,
)
from ..services import inspection as svc

router = APIRouter()


@router.get("/inspection-lots", response_model=list[InspectionLotOut])
def list_inspection_lots(
    status: str | None = None,
    disposition: str | None = None,
    inspection_type: str | None = None,
    work_order_id: str | None = None,
    product_id: str | None = None,
    source_lot_no: str | None = None,
):
    with database.session_scope() as s:
        return svc.list_inspection_lots(
            s,
            status=status,
            disposition=disposition,
            inspection_type=inspection_type,
            work_order_id=work_order_id,
            product_id=product_id,
            source_lot_no=source_lot_no,
        )


@router.get("/inspection-lots/{lot_id}", response_model=InspectionLotOut)
def get_inspection_lot(lot_id: str):
    with database.session_scope() as s:
        row = svc.get_inspection_lot(s, lot_id)
    if not row:
        raise HTTPException(404, "Inspection lot not found")
    return row


@router.post("/inspection-lots", response_model=InspectionLotOut, status_code=201)
def create_inspection_lot(body: InspectionLotCreate):
    try:
        with database.session_scope() as s:
            return svc.create_inspection_lot(s, body.model_dump())
    except ValueError as e:
        msg = str(e)
        if "already exists" in msg:
            raise HTTPException(409, msg)
        raise HTTPException(422, msg)


@router.patch("/inspection-lots/{lot_id}", response_model=InspectionLotOut)
def update_inspection_lot(lot_id: str, body: InspectionLotUpdate):
    try:
        with database.session_scope() as s:
            row = svc.update_inspection_lot(s, lot_id, body.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(422, str(e))
    if not row:
        raise HTTPException(404, "Inspection lot not found")
    return row


@router.delete("/inspection-lots/{lot_id}", status_code=204)
def delete_inspection_lot(lot_id: str):
    with database.session_scope() as s:
        if not svc.delete_inspection_lot(s, lot_id):
            raise HTTPException(404, "Inspection lot not found")
