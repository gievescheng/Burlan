"""Add production logs and process parameter checks

Revision ID: erp_0004
Revises: erp_0003
Create Date: 2026-04-14
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "erp_0004"
down_revision = "erp_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── erp_production_logs ─────────────────────────────
    op.create_table(
        "erp_production_logs",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("log_no", sa.Text(), nullable=False),
        sa.Column("work_order_id", sa.Text(), sa.ForeignKey("erp_work_orders.id"), nullable=False),
        sa.Column("production_plan_id", sa.Text(), sa.ForeignKey("erp_production_plans.id"), nullable=True),
        sa.Column("station_id", sa.Text(), sa.ForeignKey("erp_process_stations.id"), nullable=True),
        sa.Column("product_id", sa.Text(), sa.ForeignKey("erp_products.id"), nullable=False),
        # 追蹤
        sa.Column("lot_no", sa.Text(), nullable=False, server_default=""),
        sa.Column("wafer_lot", sa.Text(), nullable=False, server_default=""),
        sa.Column("glass_id", sa.Text(), nullable=False, server_default=""),
        sa.Column("carrier_id", sa.Text(), nullable=False, server_default=""),
        # 產量
        sa.Column("input_qty", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("output_qty", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("defect_qty", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("scrap_qty", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("unit", sa.Text(), nullable=False, server_default="pcs"),
        # 時間
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("shift", sa.Text(), nullable=False, server_default=""),
        # 人員 / 設備
        sa.Column("operator", sa.Text(), nullable=False, server_default=""),
        sa.Column("equipment_id", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.Text(), nullable=False, server_default="recorded"),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("updated_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_erp_production_logs_log_no", "erp_production_logs", ["log_no"], unique=True)
    op.create_index("ix_erp_production_logs_work_order_id", "erp_production_logs", ["work_order_id"])
    op.create_index("ix_erp_production_logs_production_plan_id", "erp_production_logs", ["production_plan_id"])
    op.create_index("ix_erp_production_logs_station_id", "erp_production_logs", ["station_id"])
    op.create_index("ix_erp_production_logs_product_id", "erp_production_logs", ["product_id"])
    op.create_index("ix_erp_production_logs_lot_no", "erp_production_logs", ["lot_no"])
    op.create_index("ix_erp_production_logs_status", "erp_production_logs", ["status"])

    # ── erp_process_param_checks ────────────────────────
    op.create_table(
        "erp_process_param_checks",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("production_log_id", sa.Text(), sa.ForeignKey("erp_production_logs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("seq", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("param_name", sa.Text(), nullable=False),
        sa.Column("param_value", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("unit", sa.Text(), nullable=False, server_default=""),
        sa.Column("lsl", sa.Float(), nullable=True),
        sa.Column("usl", sa.Float(), nullable=True),
        sa.Column("target", sa.Float(), nullable=True),
        sa.Column("result", sa.Text(), nullable=False, server_default="pass"),
        sa.Column("measured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("measured_by", sa.Text(), nullable=False, server_default=""),
        sa.Column("equipment_id", sa.Text(), nullable=False, server_default=""),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("updated_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_erp_process_param_checks_production_log_id", "erp_process_param_checks", ["production_log_id"])
    op.create_index("ix_erp_process_param_checks_param_name", "erp_process_param_checks", ["param_name"])
    op.create_index("ix_erp_process_param_checks_result", "erp_process_param_checks", ["result"])


def downgrade() -> None:
    op.drop_table("erp_process_param_checks")
    op.drop_table("erp_production_logs")
