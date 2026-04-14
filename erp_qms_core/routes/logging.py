from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import database
from ..schemas.logging import (
    ProductionLogCreate, ProductionLogOut, ProductionLogUpdate,
)
from ..services import logging as svc

router = APIRouter()


@router.get("/production-logs", response_model=list[ProductionLogOut])
def list_production_logs(
    status: str | None = None,
    work_order_id: str | None = None,
    station_id: str | None = None,
    lot_no: str | None = None,
):
    with database.session_scope() as s:
        return svc.list_production_logs(
            s, status=status, work_order_id=work_order_id,
            station_id=station_id, lot_no=lot_no,
        )


@router.get("/production-logs/{log_id}", response_model=ProductionLogOut)
def get_production_log(log_id: str):
    with database.session_scope() as s:
        row = svc.get_production_log(s, log_id)
    if not row:
        raise HTTPException(404, "Production log not found")
    return row


@router.post("/production-logs", response_model=ProductionLogOut, status_code=201)
def create_production_log(body: ProductionLogCreate):
    try:
        with database.session_scope() as s:
            return svc.create_production_log(s, body.model_dump())
    except ValueError as e:
        raise HTTPException(409, str(e))


@router.patch("/production-logs/{log_id}", response_model=ProductionLogOut)
def update_production_log(log_id: str, body: ProductionLogUpdate):
    try:
        with database.session_scope() as s:
            row = svc.update_production_log(s, log_id, body.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(422, str(e))
    if not row:
        raise HTTPException(404, "Production log not found")
    return row


@router.delete("/production-logs/{log_id}", status_code=204)
def delete_production_log(log_id: str):
    with database.session_scope() as s:
        if not svc.delete_production_log(s, log_id):
            raise HTTPException(404, "Production log not found")
