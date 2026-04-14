"""Add inspection lots and inspection results

Revision ID: erp_0005
Revises: erp_0004
Create Date: 2026-04-14
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "erp_0005"
down_revision = "erp_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── erp_inspection_lots ─────────────────────────────
    op.create_table(
        "erp_inspection_lots",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("lot_no", sa.Text(), nullable=False),
        sa.Column("work_order_id", sa.Text(), sa.ForeignKey("erp_work_orders.id"), nullable=False),
        sa.Column("production_log_id", sa.Text(), sa.ForeignKey("erp_production_logs.id"), nullable=True),
        sa.Column("product_id", sa.Text(), sa.ForeignKey("erp_products.id"), nullable=False),
        sa.Column("station_id", sa.Text(), sa.ForeignKey("erp_process_stations.id"), nullable=True),
        # 追蹤
        sa.Column("source_lot_no", sa.Text(), nullable=False, server_default=""),
        sa.Column("wafer_lot", sa.Text(), nullable=False, server_default=""),
        sa.Column("glass_id", sa.Text(), nullable=False, server_default=""),
        sa.Column("carrier_id", sa.Text(), nullable=False, server_default=""),
        # 抽樣
        sa.Column("inspection_type", sa.Text(), nullable=False, server_default="in_process"),
        sa.Column("sample_plan", sa.Text(), nullable=False, server_default=""),
        sa.Column("total_qty", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("sample_size", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("accept_qty", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("reject_qty", sa.Float(), nullable=False, server_default="0.0"),
        # 狀態與處置
        sa.Column("status", sa.Text(), nullable=False, server_default="pending"),
        sa.Column("disposition", sa.Text(), nullable=False, server_default=""),
        # 人員時間
        sa.Column("inspector", sa.Text(), nullable=False, server_default=""),
        sa.Column("inspected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by", sa.Text(), nullable=False, server_default=""),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("updated_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_erp_inspection_lots_lot_no", "erp_inspection_lots", ["lot_no"], unique=True)
    op.create_index("ix_erp_inspection_lots_work_order_id", "erp_inspection_lots", ["work_order_id"])
    op.create_index("ix_erp_inspection_lots_production_log_id", "erp_inspection_lots", ["production_log_id"])
    op.create_index("ix_erp_inspection_lots_product_id", "erp_inspection_lots", ["product_id"])
    op.create_index("ix_erp_inspection_lots_station_id", "erp_inspection_lots", ["station_id"])
    op.create_index("ix_erp_inspection_lots_source_lot_no", "erp_inspection_lots", ["source_lot_no"])
    op.create_index("ix_erp_inspection_lots_inspection_type", "erp_inspection_lots", ["inspection_type"])
    op.create_index("ix_erp_inspection_lots_status", "erp_inspection_lots", ["status"])
    op.create_index("ix_erp_inspection_lots_disposition", "erp_inspection_lots", ["disposition"])

    # ── erp_inspection_results ──────────────────────────
    op.create_table(
        "erp_inspection_results",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("inspection_lot_id", sa.Text(), sa.ForeignKey("erp_inspection_lots.id", ondelete="CASCADE"), nullable=False),
        sa.Column("seq", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("item_name", sa.Text(), nullable=False),
        sa.Column("spec_value", sa.Text(), nullable=False, server_default=""),
        sa.Column("lsl", sa.Float(), nullable=True),
        sa.Column("usl", sa.Float(), nullable=True),
        sa.Column("target", sa.Float(), nullable=True),
        sa.Column("actual_value", sa.Float(), nullable=True),
        sa.Column("actual_text", sa.Text(), nullable=False, server_default=""),
        sa.Column("unit", sa.Text(), nullable=False, server_default=""),
        sa.Column("equipment_id", sa.Text(), nullable=False, server_default=""),
        sa.Column("result", sa.Text(), nullable=False, server_default="pass"),
        sa.Column("defect_code", sa.Text(), nullable=False, server_default=""),
        sa.Column("defect_qty", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("measured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("measured_by", sa.Text(), nullable=False, server_default=""),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("updated_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_erp_inspection_results_inspection_lot_id", "erp_inspection_results", ["inspection_lot_id"])
    op.create_index("ix_erp_inspection_results_item_name", "erp_inspection_results", ["item_name"])
    op.create_index("ix_erp_inspection_results_result", "erp_inspection_results", ["result"])


def downgrade() -> None:
    op.drop_table("erp_inspection_results")
    op.drop_table("erp_inspection_lots")
