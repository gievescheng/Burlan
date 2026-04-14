"""Add Internal Audits and Management Reviews (ISO 9001:2015 §9.2 + §9.3)

Revision ID: erp_0009
Revises: erp_0008
Create Date: 2026-04-14
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "erp_0009"
down_revision = "erp_0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── erp_internal_audits ─────────────────────────────
    op.create_table(
        "erp_internal_audits",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("audit_no", sa.Text(), nullable=False),
        sa.Column("audit_type", sa.Text(), nullable=False, server_default="planned"),
        sa.Column("scope", sa.Text(), nullable=False, server_default="process"),
        sa.Column("audit_criteria", sa.Text(), nullable=False, server_default=""),
        sa.Column("scope_description", sa.Text(), nullable=False, server_default=""),
        sa.Column("department", sa.Text(), nullable=False, server_default=""),
        sa.Column("lead_auditor", sa.Text(), nullable=False, server_default=""),
        sa.Column("auditors", sa.Text(), nullable=False, server_default=""),
        sa.Column("planned_start_date", sa.Date(), nullable=True),
        sa.Column("planned_end_date", sa.Date(), nullable=True),
        sa.Column("actual_start_date", sa.Date(), nullable=True),
        sa.Column("actual_end_date", sa.Date(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False, server_default="planned"),
        sa.Column("report_summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("conclusion", sa.Text(), nullable=False, server_default=""),
        sa.Column("reported_to", sa.Text(), nullable=False, server_default=""),
        sa.Column("reported_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("total_findings", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("major_findings_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("minor_findings_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("observation_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("closed_by", sa.Text(), nullable=False, server_default=""),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("updated_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_erp_internal_audits_audit_no", "erp_internal_audits", ["audit_no"], unique=True)
    op.create_index("ix_erp_internal_audits_audit_type", "erp_internal_audits", ["audit_type"])
    op.create_index("ix_erp_internal_audits_scope", "erp_internal_audits", ["scope"])
    op.create_index("ix_erp_internal_audits_department", "erp_internal_audits", ["department"])
    op.create_index("ix_erp_internal_audits_status", "erp_internal_audits", ["status"])
    op.create_index("ix_erp_internal_audits_planned_start_date", "erp_internal_audits", ["planned_start_date"])

    # ── erp_audit_findings ──────────────────────────────
    op.create_table(
        "erp_audit_findings",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("finding_no", sa.Text(), nullable=False),
        sa.Column(
            "audit_id",
            sa.Text(),
            sa.ForeignKey("erp_internal_audits.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("clause", sa.Text(), nullable=False, server_default=""),
        sa.Column("finding_type", sa.Text(), nullable=False, server_default="observation"),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("evidence", sa.Text(), nullable=False, server_default=""),
        sa.Column("root_cause", sa.Text(), nullable=False, server_default=""),
        sa.Column("requires_capa", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("capa_id", sa.Text(), sa.ForeignKey("erp_capas.id"), nullable=True),
        sa.Column("responsible_dept", sa.Text(), nullable=False, server_default=""),
        sa.Column("responsible_person", sa.Text(), nullable=False, server_default=""),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("response_text", sa.Text(), nullable=False, server_default=""),
        sa.Column("verified_by", sa.Text(), nullable=False, server_default=""),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.Text(), nullable=False, server_default="open"),
        sa.Column("closed_by", sa.Text(), nullable=False, server_default=""),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("updated_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_erp_audit_findings_finding_no", "erp_audit_findings", ["finding_no"], unique=True)
    op.create_index("ix_erp_audit_findings_audit_id", "erp_audit_findings", ["audit_id"])
    op.create_index("ix_erp_audit_findings_clause", "erp_audit_findings", ["clause"])
    op.create_index("ix_erp_audit_findings_finding_type", "erp_audit_findings", ["finding_type"])
    op.create_index("ix_erp_audit_findings_requires_capa", "erp_audit_findings", ["requires_capa"])
    op.create_index("ix_erp_audit_findings_capa_id", "erp_audit_findings", ["capa_id"])
    op.create_index("ix_erp_audit_findings_due_date", "erp_audit_findings", ["due_date"])
    op.create_index("ix_erp_audit_findings_status", "erp_audit_findings", ["status"])

    # ── erp_management_reviews ──────────────────────────
    op.create_table(
        "erp_management_reviews",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("review_no", sa.Text(), nullable=False),
        sa.Column("meeting_type", sa.Text(), nullable=False, server_default="regular"),
        sa.Column("review_period_start", sa.Date(), nullable=True),
        sa.Column("review_period_end", sa.Date(), nullable=True),
        sa.Column("meeting_date", sa.Date(), nullable=True),
        sa.Column("chairperson", sa.Text(), nullable=False, server_default=""),
        sa.Column("attendees", sa.Text(), nullable=False, server_default=""),
        sa.Column("previous_actions_status", sa.Text(), nullable=False, server_default=""),
        sa.Column("context_changes", sa.Text(), nullable=False, server_default=""),
        sa.Column("qms_performance_summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("customer_satisfaction_summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("process_performance", sa.Text(), nullable=False, server_default=""),
        sa.Column("nc_and_ca_summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("audit_results_summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("resources_adequacy", sa.Text(), nullable=False, server_default=""),
        sa.Column("risks_opportunities_effectiveness", sa.Text(), nullable=False, server_default=""),
        sa.Column("improvement_opportunities", sa.Text(), nullable=False, server_default=""),
        sa.Column("improvement_decisions", sa.Text(), nullable=False, server_default=""),
        sa.Column("qms_changes", sa.Text(), nullable=False, server_default=""),
        sa.Column("resource_needs", sa.Text(), nullable=False, server_default=""),
        sa.Column("meeting_minutes", sa.Text(), nullable=False, server_default=""),
        sa.Column("conclusion", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.Text(), nullable=False, server_default="planned"),
        sa.Column("closed_by", sa.Text(), nullable=False, server_default=""),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("updated_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_erp_management_reviews_review_no", "erp_management_reviews", ["review_no"], unique=True)
    op.create_index("ix_erp_management_reviews_meeting_type", "erp_management_reviews", ["meeting_type"])
    op.create_index("ix_erp_management_reviews_meeting_date", "erp_management_reviews", ["meeting_date"])
    op.create_index("ix_erp_management_reviews_status", "erp_management_reviews", ["status"])

    # ── erp_management_review_actions ───────────────────
    op.create_table(
        "erp_management_review_actions",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("action_no", sa.Text(), nullable=False),
        sa.Column(
            "review_id",
            sa.Text(),
            sa.ForeignKey("erp_management_reviews.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("action_type", sa.Text(), nullable=False, server_default="improvement"),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("responsible_dept", sa.Text(), nullable=False, server_default=""),
        sa.Column("responsible_person", sa.Text(), nullable=False, server_default=""),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("completion_date", sa.Date(), nullable=True),
        sa.Column("effectiveness_check", sa.Text(), nullable=False, server_default=""),
        sa.Column("capa_id", sa.Text(), sa.ForeignKey("erp_capas.id"), nullable=True),
        sa.Column("status", sa.Text(), nullable=False, server_default="open"),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("updated_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_erp_management_review_actions_action_no", "erp_management_review_actions", ["action_no"], unique=True)
    op.create_index("ix_erp_management_review_actions_review_id", "erp_management_review_actions", ["review_id"])
    op.create_index("ix_erp_management_review_actions_action_type", "erp_management_review_actions", ["action_type"])
    op.create_index("ix_erp_management_review_actions_due_date", "erp_management_review_actions", ["due_date"])
    op.create_index("ix_erp_management_review_actions_capa_id", "erp_management_review_actions", ["capa_id"])
    op.create_index("ix_erp_management_review_actions_status", "erp_management_review_actions", ["status"])


def downgrade() -> None:
    op.drop_table("erp_management_review_actions")
    op.drop_table("erp_management_reviews")
    op.drop_table("erp_audit_findings")
    op.drop_table("erp_internal_audits")
