from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


# ── CustomerComplaint ──────────────────────────────────

class CustomerComplaintCreate(BaseModel):
    complaint_no: str = Field(..., min_length=1)
    customer_id: str = Field(..., min_length=1)
    product_id: str = Field(..., min_length=1)
    sales_order_id: str | None = None
    work_order_id: str | None = None
    lot_no: str = ""
    delivery_date: date | None = None
    claimed_qty: float = 0.0
    complaint_type: str = "quality"
    severity: str = "minor"
    subject: str = ""
    description: str = ""
    customer_contact: str = ""
    channel: str = "email"
    received_at: datetime | None = None
    received_by: str = ""
    requires_capa: bool = False
    notes: str = ""


class CustomerComplaintUpdate(BaseModel):
    sales_order_id: str | None = None
    work_order_id: str | None = None
    lot_no: str | None = None
    delivery_date: date | None = None
    claimed_qty: float | None = None
    complaint_type: str | None = None
    severity: str | None = None
    subject: str | None = None
    description: str | None = None
    customer_contact: str | None = None
    channel: str | None = None
    received_at: datetime | None = None
    received_by: str | None = None
    status: str | None = None
    response_text: str | None = None
    responded_by: str | None = None
    responded_at: datetime | None = None
    closed_by: str | None = None
    closed_at: datetime | None = None
    customer_satisfied: bool | None = None
    requires_capa: bool | None = None
    notes: str | None = None


class CustomerComplaintOut(BaseModel):
    id: str
    complaint_no: str
    customer_id: str
    product_id: str
    sales_order_id: str | None
    work_order_id: str | None
    lot_no: str
    delivery_date: date | None
    claimed_qty: float
    complaint_type: str
    severity: str
    subject: str
    description: str
    customer_contact: str
    channel: str
    received_at: datetime | None
    received_by: str
    status: str
    response_text: str
    responded_by: str
    responded_at: datetime | None
    closed_by: str
    closed_at: datetime | None
    customer_satisfied: bool | None
    requires_capa: bool
    notes: str
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── CAPA ───────────────────────────────────────────────

class CAPACreate(BaseModel):
    capa_no: str = Field(..., min_length=1)
    capa_type: str = "corrective"
    source_type: str = "ncr"
    ncr_id: str | None = None
    complaint_id: str | None = None
    source_ref: str = ""
    subject: str = Field(..., min_length=1)
    description: str = ""
    severity: str = "minor"
    root_cause_method: str = "5why"
    root_cause: str = ""
    similar_issues_check: str = ""
    containment_action: str = ""
    corrective_action: str = ""
    preventive_action: str = ""
    assigned_to: str = ""
    due_date: date | None = None
    notes: str = ""


class CAPAUpdate(BaseModel):
    capa_type: str | None = None
    source_type: str | None = None
    ncr_id: str | None = None
    complaint_id: str | None = None
    source_ref: str | None = None
    subject: str | None = None
    description: str | None = None
    severity: str | None = None
    root_cause_method: str | None = None
    root_cause: str | None = None
    similar_issues_check: str | None = None
    containment_action: str | None = None
    corrective_action: str | None = None
    preventive_action: str | None = None
    assigned_to: str | None = None
    due_date: date | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    effectiveness_check: str | None = None
    effectiveness_verified: bool | None = None
    verified_by: str | None = None
    verified_at: datetime | None = None
    risk_updated: bool | None = None
    qms_changes_required: bool | None = None
    status: str | None = None
    closed_by: str | None = None
    closed_at: datetime | None = None
    notes: str | None = None


class CAPAOut(BaseModel):
    id: str
    capa_no: str
    capa_type: str
    source_type: str
    ncr_id: str | None
    complaint_id: str | None
    source_ref: str
    subject: str
    description: str
    severity: str
    root_cause_method: str
    root_cause: str
    similar_issues_check: str
    containment_action: str
    corrective_action: str
    preventive_action: str
    assigned_to: str
    due_date: date | None
    started_at: datetime | None
    completed_at: datetime | None
    effectiveness_check: str
    effectiveness_verified: bool
    verified_by: str
    verified_at: datetime | None
    risk_updated: bool
    qms_changes_required: bool
    status: str
    closed_by: str
    closed_at: datetime | None
    notes: str
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
