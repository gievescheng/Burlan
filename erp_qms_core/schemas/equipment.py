from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


# ── Equipment ──────────────────────────────────────────

class EquipmentCreate(BaseModel):
    equipment_no: str = Field(..., min_length=1)
    name: str = ""
    equipment_type: str = "measurement"
    category: str = ""
    model: str = ""
    manufacturer: str = ""
    serial_no: str = ""
    location: str = ""
    department: str = ""
    responsible_person: str = ""
    acquired_date: date | None = None
    requires_calibration: bool = False
    calibration_interval_months: int = 0
    requires_pm: bool = False
    pm_interval_days: int = 0
    status: str = "active"
    notes: str = ""


class EquipmentUpdate(BaseModel):
    name: str | None = None
    equipment_type: str | None = None
    category: str | None = None
    model: str | None = None
    manufacturer: str | None = None
    serial_no: str | None = None
    location: str | None = None
    department: str | None = None
    responsible_person: str | None = None
    acquired_date: date | None = None
    requires_calibration: bool | None = None
    calibration_interval_months: int | None = None
    last_calibration_date: date | None = None
    next_calibration_due: date | None = None
    requires_pm: bool | None = None
    pm_interval_days: int | None = None
    last_pm_date: date | None = None
    next_pm_due: date | None = None
    status: str | None = None
    hold_reason: str | None = None
    notes: str | None = None


class EquipmentOut(BaseModel):
    id: str
    equipment_no: str
    name: str
    equipment_type: str
    category: str
    model: str
    manufacturer: str
    serial_no: str
    location: str
    department: str
    responsible_person: str
    acquired_date: date | None
    requires_calibration: bool
    calibration_interval_months: int
    last_calibration_date: date | None
    next_calibration_due: date | None
    requires_pm: bool
    pm_interval_days: int
    last_pm_date: date | None
    next_pm_due: date | None
    status: str
    hold_reason: str
    notes: str
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── CalibrationRecord ──────────────────────────────────

class CalibrationCreate(BaseModel):
    calibration_no: str = Field(..., min_length=1)
    equipment_id: str = Field(..., min_length=1)
    calibration_type: str = "external"
    calibration_date: date | None = None
    due_date: date | None = None
    next_due_date: date | None = None
    calibrator: str = ""
    vendor: str = ""
    certificate_no: str = ""
    standard_used: str = ""
    reading_before: float | None = None
    reading_after: float | None = None
    deviation: float | None = None
    tolerance: float | None = None
    adjustment_made: bool = False
    result: str = ""
    affected_lots: str = ""
    impact_assessment: str = ""
    status: str = "planned"
    notes: str = ""


class CalibrationUpdate(BaseModel):
    calibration_type: str | None = None
    calibration_date: date | None = None
    due_date: date | None = None
    next_due_date: date | None = None
    calibrator: str | None = None
    vendor: str | None = None
    certificate_no: str | None = None
    standard_used: str | None = None
    reading_before: float | None = None
    reading_after: float | None = None
    deviation: float | None = None
    tolerance: float | None = None
    adjustment_made: bool | None = None
    result: str | None = None
    affected_lots: str | None = None
    impact_assessment: str | None = None
    status: str | None = None
    verified_by: str | None = None
    verified_at: datetime | None = None
    notes: str | None = None


class CalibrationOut(BaseModel):
    id: str
    calibration_no: str
    equipment_id: str
    calibration_type: str
    calibration_date: date | None
    due_date: date | None
    next_due_date: date | None
    calibrator: str
    vendor: str
    certificate_no: str
    standard_used: str
    reading_before: float | None
    reading_after: float | None
    deviation: float | None
    tolerance: float | None
    adjustment_made: bool
    result: str
    affected_lots: str
    impact_assessment: str
    status: str
    verified_by: str
    verified_at: datetime | None
    notes: str
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── EquipmentPMPlan ────────────────────────────────────

class PMPlanCreate(BaseModel):
    plan_no: str = Field(..., min_length=1)
    equipment_id: str = Field(..., min_length=1)
    title: str = ""
    plan_type: str = "monthly"
    interval_days: int = 30
    tasks: str = ""
    responsible_dept: str = ""
    responsible_person: str = ""
    status: str = "active"
    notes: str = ""


class PMPlanUpdate(BaseModel):
    title: str | None = None
    plan_type: str | None = None
    interval_days: int | None = None
    tasks: str | None = None
    responsible_dept: str | None = None
    responsible_person: str | None = None
    status: str | None = None
    notes: str | None = None


class PMPlanOut(BaseModel):
    id: str
    plan_no: str
    equipment_id: str
    title: str
    plan_type: str
    interval_days: int
    tasks: str
    responsible_dept: str
    responsible_person: str
    status: str
    notes: str
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── EquipmentPMRecord ──────────────────────────────────

class PMRecordCreate(BaseModel):
    pm_no: str = Field(..., min_length=1)
    equipment_id: str = Field(..., min_length=1)
    plan_id: str | None = None
    pm_type: str = "preventive"
    scheduled_date: date | None = None
    executed_date: date | None = None
    performed_by: str = ""
    supervisor: str = ""
    tasks_performed: str = ""
    result: str = ""
    findings: str = ""
    parts_replaced: str = ""
    downtime_hours: float = 0.0
    status: str = "planned"
    next_due_date: date | None = None
    notes: str = ""


class PMRecordUpdate(BaseModel):
    plan_id: str | None = None
    pm_type: str | None = None
    scheduled_date: date | None = None
    executed_date: date | None = None
    performed_by: str | None = None
    supervisor: str | None = None
    tasks_performed: str | None = None
    result: str | None = None
    findings: str | None = None
    parts_replaced: str | None = None
    downtime_hours: float | None = None
    status: str | None = None
    next_due_date: date | None = None
    notes: str | None = None


class PMRecordOut(BaseModel):
    id: str
    pm_no: str
    equipment_id: str
    plan_id: str | None
    pm_type: str
    scheduled_date: date | None
    executed_date: date | None
    performed_by: str
    supervisor: str
    tasks_performed: str
    result: str
    findings: str
    parts_replaced: str
    downtime_hours: float
    status: str
    next_due_date: date | None
    notes: str
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
