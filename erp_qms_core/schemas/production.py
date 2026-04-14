from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


# ── ProductionPlan ──────────────────────────────────────

class ProductionPlanCreate(BaseModel):
    plan_no: str = Field(..., min_length=1)
    work_order_id: str = Field(..., min_length=1)
    product_id: str = Field(..., min_length=1)
    route_id: str | None = None
    planned_qty: float = Field(..., gt=0)
    unit: str = "pcs"
    planned_start: datetime | None = None
    planned_end: datetime | None = None
    shift: str = ""
    line_no: str = ""
    assigned_to: str = ""
    priority: int = 3
    notes: str = ""


class ProductionPlanUpdate(BaseModel):
    work_order_id: str | None = None
    product_id: str | None = None
    route_id: str | None = None
    planned_qty: float | None = None
    completed_qty: float | None = None
    unit: str | None = None
    planned_start: datetime | None = None
    planned_end: datetime | None = None
    actual_start: datetime | None = None
    actual_end: datetime | None = None
    shift: str | None = None
    line_no: str | None = None
    assigned_to: str | None = None
    priority: int | None = None
    status: str | None = None
    notes: str | None = None


class ProductionPlanOut(BaseModel):
    id: str
    plan_no: str
    work_order_id: str
    product_id: str
    route_id: str | None
    planned_qty: float
    completed_qty: float
    unit: str
    planned_start: datetime | None
    planned_end: datetime | None
    actual_start: datetime | None
    actual_end: datetime | None
    shift: str
    line_no: str
    assigned_to: str
    priority: int
    status: str
    notes: str
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── MaterialIssue ───────────────────────────────────────

class MaterialIssueItemInput(BaseModel):
    product_id: str = Field(..., min_length=1)
    seq: int = 1
    requested_qty: float = Field(..., gt=0)
    issued_qty: float = 0.0
    unit: str = "pcs"
    lot_no: str = ""
    warehouse: str = ""
    notes: str = ""


class MaterialIssueCreate(BaseModel):
    issue_no: str = Field(..., min_length=1)
    work_order_id: str | None = None
    production_plan_id: str | None = None
    issue_date: datetime | None = None
    issued_by: str = ""
    received_by: str = ""
    department: str = ""
    items: list[MaterialIssueItemInput] = []
    notes: str = ""


class MaterialIssueUpdate(BaseModel):
    work_order_id: str | None = None
    production_plan_id: str | None = None
    issue_date: datetime | None = None
    issued_by: str | None = None
    received_by: str | None = None
    department: str | None = None
    status: str | None = None
    items: list[MaterialIssueItemInput] | None = None
    notes: str | None = None


class MaterialIssueItemOut(BaseModel):
    id: str
    issue_id: str
    product_id: str
    seq: int
    requested_qty: float
    issued_qty: float
    unit: str
    lot_no: str
    warehouse: str
    notes: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MaterialIssueOut(BaseModel):
    id: str
    issue_no: str
    work_order_id: str | None
    production_plan_id: str | None
    issue_date: datetime
    issued_by: str
    received_by: str
    department: str
    status: str
    notes: str
    items: list[MaterialIssueItemOut] = []
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
