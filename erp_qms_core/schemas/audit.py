from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


# ── InternalAudit ──────────────────────────────────────

class InternalAuditCreate(BaseModel):
    audit_no: str = Field(..., min_length=1)
    audit_type: str = "planned"
    scope: str = "process"
    audit_criteria: str = ""
    scope_description: str = ""
    department: str = ""
    lead_auditor: str = ""
    auditors: str = ""
    planned_start_date: date | None = None
    planned_end_date: date | None = None
    actual_start_date: date | None = None
    actual_end_date: date | None = None
    report_summary: str = ""
    conclusion: str = ""
    notes: str = ""


class InternalAuditUpdate(BaseModel):
    audit_type: str | None = None
    scope: str | None = None
    audit_criteria: str | None = None
    scope_description: str | None = None
    department: str | None = None
    lead_auditor: str | None = None
    auditors: str | None = None
    planned_start_date: date | None = None
    planned_end_date: date | None = None
    actual_start_date: date | None = None
    actual_end_date: date | None = None
    status: str | None = None
    report_summary: str | None = None
    conclusion: str | None = None
    reported_to: str | None = None
    reported_at: datetime | None = None
    closed_by: str | None = None
    closed_at: datetime | None = None
    notes: str | None = None


class InternalAuditOut(BaseModel):
    id: str
    audit_no: str
    audit_type: str
    scope: str
    audit_criteria: str
    scope_description: str
    department: str
    lead_auditor: str
    auditors: str
    planned_start_date: date | None
    planned_end_date: date | None
    actual_start_date: date | None
    actual_end_date: date | None
    status: str
    report_summary: str
    conclusion: str
    reported_to: str
    reported_at: datetime | None
    total_findings: int
    major_findings_count: int
    minor_findings_count: int
    observation_count: int
    closed_by: str
    closed_at: datetime | None
    notes: str
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── AuditFinding ───────────────────────────────────────

class AuditFindingCreate(BaseModel):
    finding_no: str = Field(..., min_length=1)
    audit_id: str = Field(..., min_length=1)
    clause: str = ""
    finding_type: str = "observation"
    description: str = ""
    evidence: str = ""
    root_cause: str = ""
    requires_capa: bool = False
    capa_id: str | None = None
    responsible_dept: str = ""
    responsible_person: str = ""
    due_date: date | None = None
    response_text: str = ""
    notes: str = ""


class AuditFindingUpdate(BaseModel):
    clause: str | None = None
    finding_type: str | None = None
    description: str | None = None
    evidence: str | None = None
    root_cause: str | None = None
    requires_capa: bool | None = None
    capa_id: str | None = None
    responsible_dept: str | None = None
    responsible_person: str | None = None
    due_date: date | None = None
    response_text: str | None = None
    verified_by: str | None = None
    verified_at: datetime | None = None
    status: str | None = None
    closed_by: str | None = None
    closed_at: datetime | None = None
    notes: str | None = None


class AuditFindingOut(BaseModel):
    id: str
    finding_no: str
    audit_id: str
    clause: str
    finding_type: str
    description: str
    evidence: str
    root_cause: str
    requires_capa: bool
    capa_id: str | None
    responsible_dept: str
    responsible_person: str
    due_date: date | None
    response_text: str
    verified_by: str
    verified_at: datetime | None
    status: str
    closed_by: str
    closed_at: datetime | None
    notes: str
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
