from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


# ── ManagementReview ───────────────────────────────────

class ManagementReviewCreate(BaseModel):
    review_no: str = Field(..., min_length=1)
    meeting_type: str = "regular"
    review_period_start: date | None = None
    review_period_end: date | None = None
    meeting_date: date | None = None
    chairperson: str = ""
    attendees: str = ""
    previous_actions_status: str = ""
    context_changes: str = ""
    qms_performance_summary: str = ""
    customer_satisfaction_summary: str = ""
    process_performance: str = ""
    nc_and_ca_summary: str = ""
    audit_results_summary: str = ""
    resources_adequacy: str = ""
    risks_opportunities_effectiveness: str = ""
    improvement_opportunities: str = ""
    improvement_decisions: str = ""
    qms_changes: str = ""
    resource_needs: str = ""
    meeting_minutes: str = ""
    conclusion: str = ""
    notes: str = ""


class ManagementReviewUpdate(BaseModel):
    meeting_type: str | None = None
    review_period_start: date | None = None
    review_period_end: date | None = None
    meeting_date: date | None = None
    chairperson: str | None = None
    attendees: str | None = None
    previous_actions_status: str | None = None
    context_changes: str | None = None
    qms_performance_summary: str | None = None
    customer_satisfaction_summary: str | None = None
    process_performance: str | None = None
    nc_and_ca_summary: str | None = None
    audit_results_summary: str | None = None
    resources_adequacy: str | None = None
    risks_opportunities_effectiveness: str | None = None
    improvement_opportunities: str | None = None
    improvement_decisions: str | None = None
    qms_changes: str | None = None
    resource_needs: str | None = None
    meeting_minutes: str | None = None
    conclusion: str | None = None
    status: str | None = None
    closed_by: str | None = None
    closed_at: datetime | None = None
    notes: str | None = None


class ManagementReviewOut(BaseModel):
    id: str
    review_no: str
    meeting_type: str
    review_period_start: date | None
    review_period_end: date | None
    meeting_date: date | None
    chairperson: str
    attendees: str
    previous_actions_status: str
    context_changes: str
    qms_performance_summary: str
    customer_satisfaction_summary: str
    process_performance: str
    nc_and_ca_summary: str
    audit_results_summary: str
    resources_adequacy: str
    risks_opportunities_effectiveness: str
    improvement_opportunities: str
    improvement_decisions: str
    qms_changes: str
    resource_needs: str
    meeting_minutes: str
    conclusion: str
    status: str
    closed_by: str
    closed_at: datetime | None
    notes: str
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── ManagementReviewAction ─────────────────────────────

class ReviewActionCreate(BaseModel):
    action_no: str = Field(..., min_length=1)
    review_id: str = Field(..., min_length=1)
    action_type: str = "improvement"
    description: str = ""
    responsible_dept: str = ""
    responsible_person: str = ""
    due_date: date | None = None
    capa_id: str | None = None
    notes: str = ""


class ReviewActionUpdate(BaseModel):
    action_type: str | None = None
    description: str | None = None
    responsible_dept: str | None = None
    responsible_person: str | None = None
    due_date: date | None = None
    completion_date: date | None = None
    effectiveness_check: str | None = None
    capa_id: str | None = None
    status: str | None = None
    notes: str | None = None


class ReviewActionOut(BaseModel):
    id: str
    action_no: str
    review_id: str
    action_type: str
    description: str
    responsible_dept: str
    responsible_person: str
    due_date: date | None
    completion_date: date | None
    effectiveness_check: str
    capa_id: str | None
    status: str
    notes: str
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
