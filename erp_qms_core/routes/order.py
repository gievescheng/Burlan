from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import database
from ..schemas.order import (
    SalesOrderCreate, SalesOrderOut, SalesOrderUpdate,
    WorkOrderCreate, WorkOrderOut, WorkOrderUpdate,
)
from ..services import order as svc

router = APIRouter()


# ── SalesOrder ──────────────────────────────────────────

@router.get("/sales-orders", response_model=list[SalesOrderOut])
def list_sales_orders(status: str | None = None, customer_id: str | None = None):
    with database.session_scope() as s:
        return svc.list_sales_orders(s, status=status, customer_id=customer_id)


@router.get("/sales-orders/{order_id}", response_model=SalesOrderOut)
def get_sales_order(order_id: str):
    with database.session_scope() as s:
        row = svc.get_sales_order(s, order_id)
    if not row:
        raise HTTPException(404, "Sales order not found")
    return row


@router.post("/sales-orders", response_model=SalesOrderOut, status_code=201)
def create_sales_order(body: SalesOrderCreate):
    try:
        with database.session_scope() as s:
            return svc.create_sales_order(s, body.model_dump())
    except ValueError as e:
        raise HTTPException(409, str(e))


@router.patch("/sales-orders/{order_id}", response_model=SalesOrderOut)
def update_sales_order(order_id: str, body: SalesOrderUpdate):
    try:
        with database.session_scope() as s:
            row = svc.update_sales_order(s, order_id, body.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(422, str(e))
    if not row:
        raise HTTPException(404, "Sales order not found")
    return row


@router.delete("/sales-orders/{order_id}", status_code=204)
def delete_sales_order(order_id: str):
    with database.session_scope() as s:
        if not svc.delete_sales_order(s, order_id):
            raise HTTPException(404, "Sales order not found")


# ── WorkOrder ───────────────────────────────────────────

@router.get("/work-orders", response_model=list[WorkOrderOut])
def list_work_orders(
    status: str | None = None,
    sales_order_id: str | None = None,
    product_id: str | None = None,
    lot_no: str | None = None,
):
    with database.session_scope() as s:
        return svc.list_work_orders(
            s, status=status, sales_order_id=sales_order_id,
            product_id=product_id, lot_no=lot_no,
        )


@router.get("/work-orders/{wo_id}", response_model=WorkOrderOut)
def get_work_order(wo_id: str):
    with database.session_scope() as s:
        row = svc.get_work_order(s, wo_id)
    if not row:
        raise HTTPException(404, "Work order not found")
    return row


@router.post("/work-orders", response_model=WorkOrderOut, status_code=201)
def create_work_order(body: WorkOrderCreate):
    try:
        with database.session_scope() as s:
            return svc.create_work_order(s, body.model_dump())
    except ValueError as e:
        raise HTTPException(409, str(e))


@router.patch("/work-orders/{wo_id}", response_model=WorkOrderOut)
def update_work_order(wo_id: str, body: WorkOrderUpdate):
    try:
        with database.session_scope() as s:
            row = svc.update_work_order(s, wo_id, body.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(422, str(e))
    if not row:
        raise HTTPException(404, "Work order not found")
    return row


@router.delete("/work-orders/{wo_id}", status_code=204)
def delete_work_order(wo_id: str):
    with database.session_scope() as s:
        if not svc.delete_work_order(s, wo_id):
            raise HTTPException(404, "Work order not found")
