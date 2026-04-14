from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


# ── ProcessParamCheck ───────────────────────────────────

class ParamCheckInput(BaseModel):
    seq: int = 1
    param_name: str = Field(..., min_length=1)
    param_value: float = 0.0
    unit: str = ""
    lsl: float | None = None
    usl: float | None = None
    target: float | None = None
    result: str = "pass"
    measured_at: datetime | None = None
    measured_by: str = ""
    equipment_id: str = ""
    notes: str = ""


class ParamCheckOut(BaseModel):
    id: str
    production_log_id: str
    seq: int
    param_name: str
    param_value: float
    unit: str
    lsl: float | None
    usl: float | None
    target: float | None
    result: str
    measured_at: datetime
    measured_by: str
    equipment_id: str
    notes: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── ProductionLog ───────────────────────────────────────

class ProductionLogCreate(BaseModel):
    log_no: str = Field(..., min_length=1)
    work_order_id: str = Field(..., min_length=1)
    product_id: str = Field(..., min_length=1)
    production_plan_id: str | None = None
    station_id: str | None = None
    lot_no: str = ""
    wafer_lot: str = ""
    glass_id: str = ""
    carrier_id: str = ""
    input_qty: float = 0.0
    output_qty: float = 0.0
    defect_qty: float = 0.0
    scrap_qty: float = 0.0
    unit: str = "pcs"
    start_time: datetime | None = None
    end_time: datetime | None = None
    shift: str = ""
    operator: str = ""
    equipment_id: str = ""
    param_checks: list[ParamCheckInput] = []
    notes: str = ""


class ProductionLogUpdate(BaseModel):
    production_plan_id: str | None = None
    station_id: str | None = None
    lot_no: str | None = None
    wafer_lot: str | None = None
    glass_id: str | None = None
    carrier_id: str | None = None
    input_qty: float | None = None
    output_qty: float | None = None
    defect_qty: float | None = None
    scrap_qty: float | None = None
    unit: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    shift: str | None = None
    operator: str | None = None
    equipment_id: str | None = None
    status: str | None = None
    param_checks: list[ParamCheckInput] | None = None
    notes: str | None = None


class ProductionLogOut(BaseModel):
    id: str
    log_no: str
    work_order_id: str
    production_plan_id: str | None
    station_id: str | None
    product_id: str
    lot_no: str
    wafer_lot: str
    glass_id: str
    carrier_id: str
    input_qty: float
    output_qty: float
    defect_qty: float
    scrap_qty: float
    unit: str
    start_time: datetime | None
    end_time: datetime | None
    shift: str
    operator: str
    equipment_id: str
    status: str
    notes: str
    param_checks: list[ParamCheckOut] = []
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
