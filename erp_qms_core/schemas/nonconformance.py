from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


# ── ReworkOrder ────────────────────────────────────────

class ReworkOrderInput(BaseModel):
    rework_no: str = Field(..., min_length=1)
    work_order_id: str = Field(..., min_length=1)
    product_id: str = Field(..., min_length=1)
    rework_qty: float = 0.0
    method: str = ""
    instructions: str = ""
    assigned_to: str = ""
    notes: str = ""


class ReworkOrderUpdate(BaseModel):
    rework_qty: float | None = None
    success_qty: float | None = None
    scrap_qty: float | None = None
    method: str | None = None
    instructions: str | None = None
    assigned_to: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    status: str | None = None
    result: str | None = None
    reinspection_lot_id: str | None = None
    notes: str | None = None


class ReworkOrderOut(BaseModel):
    id: str
    rework_no: str
    ncr_id: str
    work_order_id: str
    product_id: str
    rework_qty: float
    success_qty: float
    scrap_qty: float
    method: str
    instructions: str
    assigned_to: str
    started_at: datetime | None
    completed_at: datetime | None
    status: str
    result: str
    reinspection_lot_id: str | None
    notes: str
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── NCR ────────────────────────────────────────────────

class NCRCreate(BaseModel):
    ncr_no: str = Field(..., min_length=1)
    work_order_id: str = Field(..., min_length=1)
    product_id: str = Field(..., min_length=1)
    inspection_lot_id: str | None = None
    production_log_id: str | None = None
    station_id: str | None = None
    lot_no: str = ""
    wafer_lot: str = ""
    glass_id: str = ""
    carrier_id: str = ""
    defect_qty: float = 0.0
    total_qty: float = 0.0
    defect_code: str = ""
    defect_description: str = ""
    severity: str = "minor"
    category: str = "process"
    reported_by: str = ""
    reported_at: datetime | None = None
    assigned_to: str = ""
    requires_capa: bool = False
    notes: str = ""


class NCRUpdate(BaseModel):
    inspection_lot_id: str | None = None
    production_log_id: str | None = None
    station_id: str | None = None
    lot_no: str | None = None
    wafer_lot: str | None = None
    glass_id: str | None = None
    carrier_id: str | None = None
    defect_qty: float | None = None
    total_qty: float | None = None
    defect_code: str | None = None
    defect_description: str | None = None
    severity: str | None = None
    category: str | None = None
    disposition: str | None = None
    disposition_reason: str | None = None
    disposition_by: str | None = None
    disposition_at: datetime | None = None
    status: str | None = None
    reported_by: str | None = None
    reported_at: datetime | None = None
    assigned_to: str | None = None
    closed_by: str | None = None
    closed_at: datetime | None = None
    requires_capa: bool | None = None
    notes: str | None = None


class NCROut(BaseModel):
    id: str
    ncr_no: str
    work_order_id: str
    product_id: str
    inspection_lot_id: str | None
    production_log_id: str | None
    station_id: str | None
    lot_no: str
    wafer_lot: str
    glass_id: str
    carrier_id: str
    defect_qty: float
    total_qty: float
    defect_code: str
    defect_description: str
    severity: str
    category: str
    disposition: str
    disposition_reason: str
    disposition_by: str
    disposition_at: datetime | None
    status: str
    reported_by: str
    reported_at: datetime | None
    assigned_to: str
    closed_by: str
    closed_at: datetime | None
    requires_capa: bool
    notes: str
    rework_orders: list[ReworkOrderOut] = []
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
