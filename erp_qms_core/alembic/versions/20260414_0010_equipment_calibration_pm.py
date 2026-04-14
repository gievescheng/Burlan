"""Add Equipment, Calibration Records, and Preventive Maintenance (ISO 9001:2015 §7.1.5)

Revision ID: erp_0010
Revises: erp_0009
Create Date: 2026-04-14
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "erp_0010"
down_revision = "erp_0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── erp_equipments ──────────────────────────────────
    op.create_table(
        "erp_equipments",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("equipment_no", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False, server_default=""),
        sa.Column("equipment_type", sa.Text(), nullable=False, server_default="measurement"),
        sa.Column("category", sa.Text(), nullable=False, server_default=""),
        sa.Column("model", sa.Text(), nullable=False, server_default=""),
        sa.Column("manufacturer", sa.Text(), nullable=False, server_default=""),
        sa.Column("serial_no", sa.Text(), nullable=False, server_default=""),
        sa.Column("location", sa.Text(), nullable=False, server_default=""),
        sa.Column("department", sa.Text(), nullable=False, server_default=""),
        sa.Column("responsible_person", sa.Text(), nullable=False, server_default=""),
        sa.Column("acquired_date", sa.Date(), nullable=True),
        sa.Column("requires_calibration", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("calibration_interval_months", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_calibration_date", sa.Date(), nullable=True),
        sa.Column("next_calibration_due", sa.Date(), nullable=True),
        sa.Column("requires_pm", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("pm_interval_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_pm_date", sa.Date(), nullable=True),
        sa.Column("next_pm_due", sa.Date(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False, server_default="active"),
        sa.Column("hold_reason", sa.Text(), nullable=False, server_default=""),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("updated_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_erp_equipments_equipment_no", "erp_equipments", ["equipment_no"], unique=True)
    op.create_index("ix_erp_equipments_equipment_type", "erp_equipments", ["equipment_type"])
    op.create_index("ix_erp_equipments_category", "erp_equipments", ["category"])
    op.create_index("ix_erp_equipments_serial_no", "erp_equipments", ["serial_no"])
    op.create_index("ix_erp_equipments_department", "erp_equipments", ["department"])
    op.create_index("ix_erp_equipments_requires_calibration", "erp_equipments", ["requires_calibration"])
    op.create_index("ix_erp_equipments_next_calibration_due", "erp_equipments", ["next_calibration_due"])
    op.create_index("ix_erp_equipments_requires_pm", "erp_equipments", ["requires_pm"])
    op.create_index("ix_erp_equipments_next_pm_due", "erp_equipments", ["next_pm_due"])
    op.create_index("ix_erp_equipments_status", "erp_equipments", ["status"])

    # ── erp_calibration_records ─────────────────────────
    op.create_table(
        "erp_calibration_records",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("calibration_no", sa.Text(), nullable=False),
        sa.Column(
            "equipment_id",
            sa.Text(),
            sa.ForeignKey("erp_equipments.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("calibration_type", sa.Text(), nullable=False, server_default="external"),
        sa.Column("calibration_date", sa.Date(), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("next_due_date", sa.Date(), nullable=True),
        sa.Column("calibrator", sa.Text(), nullable=False, server_default=""),
        sa.Column("vendor", sa.Text(), nullable=False, server_default=""),
        sa.Column("certificate_no", sa.Text(), nullable=False, server_default=""),
        sa.Column("standard_used", sa.Text(), nullable=False, server_default=""),
        sa.Column("reading_before", sa.Float(), nullable=True),
        sa.Column("reading_after", sa.Float(), nullable=True),
        sa.Column("deviation", sa.Float(), nullable=True),
        sa.Column("tolerance", sa.Float(), nullable=True),
        sa.Column("adjustment_made", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("result", sa.Text(), nullable=False, server_default=""),
        sa.Column("affected_lots", sa.Text(), nullable=False, server_default=""),
        sa.Column("impact_assessment", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.Text(), nullable=False, server_default="planned"),
        sa.Column("verified_by", sa.Text(), nullable=False, server_default=""),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("updated_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_erp_calibration_records_calibration_no", "erp_calibration_records", ["calibration_no"], unique=True)
    op.create_index("ix_erp_calibration_records_equipment_id", "erp_calibration_records", ["equipment_id"])
    op.create_index("ix_erp_calibration_records_calibration_type", "erp_calibration_records", ["calibration_type"])
    op.create_index("ix_erp_calibration_records_calibration_date", "erp_calibration_records", ["calibration_date"])
    op.create_index("ix_erp_calibration_records_due_date", "erp_calibration_records", ["due_date"])
    op.create_index("ix_erp_calibration_records_certificate_no", "erp_calibration_records", ["certificate_no"])
    op.create_index("ix_erp_calibration_records_result", "erp_calibration_records", ["result"])
    op.create_index("ix_erp_calibration_records_status", "erp_calibration_records", ["status"])

    # ── erp_equipment_pm_plans ──────────────────────────
    op.create_table(
        "erp_equipment_pm_plans",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("plan_no", sa.Text(), nullable=False),
        sa.Column(
            "equipment_id",
            sa.Text(),
            sa.ForeignKey("erp_equipments.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.Text(), nullable=False, server_default=""),
        sa.Column("plan_type", sa.Text(), nullable=False, server_default="monthly"),
        sa.Column("interval_days", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("tasks", sa.Text(), nullable=False, server_default=""),
        sa.Column("responsible_dept", sa.Text(), nullable=False, server_default=""),
        sa.Column("responsible_person", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.Text(), nullable=False, server_default="active"),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("updated_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_erp_equipment_pm_plans_plan_no", "erp_equipment_pm_plans", ["plan_no"], unique=True)
    op.create_index("ix_erp_equipment_pm_plans_equipment_id", "erp_equipment_pm_plans", ["equipment_id"])
    op.create_index("ix_erp_equipment_pm_plans_plan_type", "erp_equipment_pm_plans", ["plan_type"])
    op.create_index("ix_erp_equipment_pm_plans_status", "erp_equipment_pm_plans", ["status"])

    # ── erp_equipment_pm_records ────────────────────────
    op.create_table(
        "erp_equipment_pm_records",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("pm_no", sa.Text(), nullable=False),
        sa.Column(
            "equipment_id",
            sa.Text(),
            sa.ForeignKey("erp_equipments.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "plan_id",
            sa.Text(),
            sa.ForeignKey("erp_equipment_pm_plans.id"),
            nullable=True,
        ),
        sa.Column("pm_type", sa.Text(), nullable=False, server_default="preventive"),
        sa.Column("scheduled_date", sa.Date(), nullable=True),
        sa.Column("executed_date", sa.Date(), nullable=True),
        sa.Column("performed_by", sa.Text(), nullable=False, server_default=""),
        sa.Column("supervisor", sa.Text(), nullable=False, server_default=""),
        sa.Column("tasks_performed", sa.Text(), nullable=False, server_default=""),
        sa.Column("result", sa.Text(), nullable=False, server_default=""),
        sa.Column("findings", sa.Text(), nullable=False, server_default=""),
        sa.Column("parts_replaced", sa.Text(), nullable=False, server_default=""),
        sa.Column("downtime_hours", sa.Float(), nullable=False, server_default="0"),
        sa.Column("status", sa.Text(), nullable=False, server_default="planned"),
        sa.Column("next_due_date", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("updated_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_erp_equipment_pm_records_pm_no", "erp_equipment_pm_records", ["pm_no"], unique=True)
    op.create_index("ix_erp_equipment_pm_records_equipment_id", "erp_equipment_pm_records", ["equipment_id"])
    op.create_index("ix_erp_equipment_pm_records_plan_id", "erp_equipment_pm_records", ["plan_id"])
    op.create_index("ix_erp_equipment_pm_records_pm_type", "erp_equipment_pm_records", ["pm_type"])
    op.create_index("ix_erp_equipment_pm_records_scheduled_date", "erp_equipment_pm_records", ["scheduled_date"])
    op.create_index("ix_erp_equipment_pm_records_result", "erp_equipment_pm_records", ["result"])
    op.create_index("ix_erp_equipment_pm_records_status", "erp_equipment_pm_records", ["status"])


def downgrade() -> None:
    op.drop_table("erp_equipment_pm_records")
    op.drop_table("erp_equipment_pm_plans")
    op.drop_table("erp_calibration_records")
    op.drop_table("erp_equipments")
