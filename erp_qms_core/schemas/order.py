from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


# ── SalesOrder ──────────────────────────────────────────

class SalesOrderItemInput(BaseModel):
    product_id: str = Field(..., min_length=1)
    seq: int = 1
    quantity: float = Field(..., gt=0)
    unit_price: float = 0.0
    unit: str = "pcs"
    notes: str = ""


class SalesOrderCreate(BaseModel):
    order_no: str = Field(..., min_length=1)
    customer_id: str = Field(..., min_length=1)
    order_date: datetime | None = None
    required_date: datetime | None = None
    currency: str = "TWD"
    items: list[SalesOrderItemInput] = []
    notes: str = ""


class SalesOrderUpdate(BaseModel):
    customer_id: str | None = None
    order_date: datetime | None = None
    required_date: datetime | None = None
    currency: str | None = None
    status: str | None = None
    items: list[SalesOrderItemInput] | None = None
    notes: str | None = None


class SalesOrderItemOut(BaseModel):
    id: str
    order_id: str
    product_id: str
    seq: int
    quantity: float
    unit_price: float
    unit: str
    line_amount: float
    notes: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SalesOrderOut(BaseModel):
    id: str
    order_no: str
    customer_id: str
    order_date: datetime
    required_date: datetime | None
    currency: str
    total_amount: float
    status: str
    notes: str
    items: list[SalesOrderItemOut] = []
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── WorkOrder ───────────────────────────────────────────

class WorkOrderCreate(BaseModel):
    wo_no: str = Field(..., min_length=1)
    product_id: str = Field(..., min_length=1)
    sales_order_id: str | None = None
    sales_order_item_id: str | None = None
    route_id: str | None = None
    lot_no: str = ""
    wafer_lot: str = ""
    glass_id: str = ""
    carrier_id: str = ""
    planned_qty: float = Field(..., gt=0)
    unit: str = "pcs"
    planned_start: datetime | None = None
    planned_end: datetime | None = None
    priority: int = 3
    assigned_to: str = ""
    notes: str = ""


class WorkOrderUpdate(BaseModel):
    product_id: str | None = None
    sales_order_id: str | None = None
    sales_order_item_id: str | None = None
    route_id: str | None = None
    lot_no: str | None = None
    wafer_lot: str | None = None
    glass_id: str | None = None
    carrier_id: str | None = None
    planned_qty: float | None = None
    completed_qty: float | None = None
    scrap_qty: float | None = None
    unit: str | None = None
    planned_start: datetime | None = None
    planned_end: datetime | None = None
    actual_start: datetime | None = None
    actual_end: datetime | None = None
    priority: int | None = None
    assigned_to: str | None = None
    status: str | None = None
    notes: str | None = None


class WorkOrderOut(BaseModel):
    id: str
    wo_no: str
    sales_order_id: str | None
    sales_order_item_id: str | None
    product_id: str
    route_id: str | None
    lot_no: str
    wafer_lot: str
    glass_id: str
    carrier_id: str
    planned_qty: float
    completed_qty: float
    scrap_qty: float
    unit: str
    planned_start: datetime | None
    planned_end: datetime | None
    actual_start: datetime | None
    actual_end: datetime | None
    priority: int
    assigned_to: str
    status: str
    notes: str
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
