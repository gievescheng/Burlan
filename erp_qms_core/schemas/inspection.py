from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


# ── InspectionResult ───────────────────────────────────

class InspectionResultInput(BaseModel):
    seq: int = 1
    item_name: str = Field(..., min_length=1)
    spec_value: str = ""
    lsl: float | None = None
    usl: float | None = None
    target: float | None = None
    actual_value: float | None = None
    actual_text: str = ""
    unit: str = ""
    equipment_id: str = ""
    result: str = "pass"
    defect_code: str = ""
    defect_qty: float = 0.0
    measured_at: datetime | None = None
    measured_by: str = ""
    notes: str = ""


class InspectionResultOut(BaseModel):
    id: str
    inspection_lot_id: str
    seq: int
    item_name: str
    spec_value: str
    lsl: float | None
    usl: float | None
    target: float | None
    actual_value: float | None
    actual_text: str
    unit: str
    equipment_id: str
    result: str
    defect_code: str
    defect_qty: float
    measured_at: datetime
    measured_by: str
    notes: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── InspectionLot ──────────────────────────────────────

class InspectionLotCreate(BaseModel):
    lot_no: str = Field(..., min_length=1)
    work_order_id: str = Field(..., min_length=1)
    product_id: str = Field(..., min_length=1)
    production_log_id: str | None = None
    station_id: str | None = None
    source_lot_no: str = ""
    wafer_lot: str = ""
    glass_id: str = ""
    carrier_id: str = ""
    inspection_type: str = "in_process"
    sample_plan: str = ""
    total_qty: float = 0.0
    sample_size: float = 0.0
    accept_qty: float = 0.0
    reject_qty: float = 0.0
    inspector: str = ""
    inspected_at: datetime | None = None
    notes: str = ""
    results: list[InspectionResultInput] = []


class InspectionLotUpdate(BaseModel):
    production_log_id: str | None = None
    station_id: str | None = None
    source_lot_no: str | None = None
    wafer_lot: str | None = None
    glass_id: str | None = None
    carrier_id: str | None = None
    inspection_type: str | None = None
    sample_plan: str | None = None
    total_qty: float | None = None
    sample_size: float | None = None
    accept_qty: float | None = None
    reject_qty: float | None = None
    status: str | None = None
    disposition: str | None = None
    inspector: str | None = None
    inspected_at: datetime | None = None
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    notes: str | None = None
    results: list[InspectionResultInput] | None = None


class InspectionLotOut(BaseModel):
    id: str
    lot_no: str
    work_order_id: str
    production_log_id: str | None
    product_id: str
    station_id: str | None
    source_lot_no: str
    wafer_lot: str
    glass_id: str
    carrier_id: str
    inspection_type: str
    sample_plan: str
    total_qty: float
    sample_size: float
    accept_qty: float
    reject_qty: float
    status: str
    disposition: str
    inspector: str
    inspected_at: datetime | None
    reviewed_by: str
    reviewed_at: datetime | None
    notes: str
    results: list[InspectionResultOut] = []
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
