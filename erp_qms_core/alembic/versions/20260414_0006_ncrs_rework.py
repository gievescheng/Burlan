"""Add NCRs and Rework Orders (ISO 9001:2015 §8.7)

Revision ID: erp_0006
Revises: erp_0005
Create Date: 2026-04-14
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "erp_0006"
down_revision = "erp_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── erp_ncrs ────────────────────────────────────────
    op.create_table(
        "erp_ncrs",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("ncr_no", sa.Text(), nullable=False),
        sa.Column("work_order_id", sa.Text(), sa.ForeignKey("erp_work_orders.id"), nullable=False),
        sa.Column("product_id", sa.Text(), sa.ForeignKey("erp_products.id"), nullable=False),
        sa.Column("inspection_lot_id", sa.Text(), sa.ForeignKey("erp_inspection_lots.id"), nullable=True),
        sa.Column("production_log_id", sa.Text(), sa.ForeignKey("erp_production_logs.id"), nullable=True),
        sa.Column("station_id", sa.Text(), sa.ForeignKey("erp_process_stations.id"), nullable=True),
        # 追蹤
        sa.Column("lot_no", sa.Text(), nullable=False, server_default=""),
        sa.Column("wafer_lot", sa.Text(), nullable=False, server_default=""),
        sa.Column("glass_id", sa.Text(), nullable=False, server_default=""),
        sa.Column("carrier_id", sa.Text(), nullable=False, server_default=""),
        # 數量
        sa.Column("defect_qty", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("total_qty", sa.Float(), nullable=False, server_default="0.0"),
        # 缺陷描述
        sa.Column("defect_code", sa.Text(), nullable=False, server_default=""),
        sa.Column("defect_description", sa.Text(), nullable=False, server_default=""),
        sa.Column("severity", sa.Text(), nullable=False, server_default="minor"),
        sa.Column("category", sa.Text(), nullable=False, server_default="process"),
        # 處置
        sa.Column("disposition", sa.Text(), nullable=False, server_default=""),
        sa.Column("disposition_reason", sa.Text(), nullable=False, server_default=""),
        sa.Column("disposition_by", sa.Text(), nullable=False, server_default=""),
        sa.Column("disposition_at", sa.DateTime(timezone=True), nullable=True),
        # 狀態
        sa.Column("status", sa.Text(), nullable=False, server_default="open"),
        # 人員時間
        sa.Column("reported_by", sa.Text(), nullable=False, server_default=""),
        sa.Column("reported_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("assigned_to", sa.Text(), nullable=False, server_default=""),
        sa.Column("closed_by", sa.Text(), nullable=False, server_default=""),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        # 後續
        sa.Column("requires_capa", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("updated_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_erp_ncrs_ncr_no", "erp_ncrs", ["ncr_no"], unique=True)
    op.create_index("ix_erp_ncrs_work_order_id", "erp_ncrs", ["work_order_id"])
    op.create_index("ix_erp_ncrs_product_id", "erp_ncrs", ["product_id"])
    op.create_index("ix_erp_ncrs_inspection_lot_id", "erp_ncrs", ["inspection_lot_id"])
    op.create_index("ix_erp_ncrs_production_log_id", "erp_ncrs", ["production_log_id"])
    op.create_index("ix_erp_ncrs_station_id", "erp_ncrs", ["station_id"])
    op.create_index("ix_erp_ncrs_lot_no", "erp_ncrs", ["lot_no"])
    op.create_index("ix_erp_ncrs_defect_code", "erp_ncrs", ["defect_code"])
    op.create_index("ix_erp_ncrs_severity", "erp_ncrs", ["severity"])
    op.create_index("ix_erp_ncrs_category", "erp_ncrs", ["category"])
    op.create_index("ix_erp_ncrs_disposition", "erp_ncrs", ["disposition"])
    op.create_index("ix_erp_ncrs_status", "erp_ncrs", ["status"])
    op.create_index("ix_erp_ncrs_requires_capa", "erp_ncrs", ["requires_capa"])

    # ── erp_rework_orders ───────────────────────────────
    op.create_table(
        "erp_rework_orders",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("rework_no", sa.Text(), nullable=False),
        sa.Column("ncr_id", sa.Text(), sa.ForeignKey("erp_ncrs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("work_order_id", sa.Text(), sa.ForeignKey("erp_work_orders.id"), nullable=False),
        sa.Column("product_id", sa.Text(), sa.ForeignKey("erp_products.id"), nullable=False),
        # 數量
        sa.Column("rework_qty", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("success_qty", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("scrap_qty", sa.Float(), nullable=False, server_default="0.0"),
        # 重工方法
        sa.Column("method", sa.Text(), nullable=False, server_default=""),
        sa.Column("instructions", sa.Text(), nullable=False, server_default=""),
        # 執行
        sa.Column("assigned_to", sa.Text(), nullable=False, server_default=""),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        # 狀態
        sa.Column("status", sa.Text(), nullable=False, server_default="planned"),
        sa.Column("result", sa.Text(), nullable=False, server_default=""),
        # 後續檢驗
        sa.Column("reinspection_lot_id", sa.Text(), sa.ForeignKey("erp_inspection_lots.id"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("updated_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_erp_rework_orders_rework_no", "erp_rework_orders", ["rework_no"], unique=True)
    op.create_index("ix_erp_rework_orders_ncr_id", "erp_rework_orders", ["ncr_id"])
    op.create_index("ix_erp_rework_orders_work_order_id", "erp_rework_orders", ["work_order_id"])
    op.create_index("ix_erp_rework_orders_product_id", "erp_rework_orders", ["product_id"])
    op.create_index("ix_erp_rework_orders_status", "erp_rework_orders", ["status"])
    op.create_index("ix_erp_rework_orders_result", "erp_rework_orders", ["result"])
    op.create_index("ix_erp_rework_orders_reinspection_lot_id", "erp_rework_orders", ["reinspection_lot_id"])


def downgrade() -> None:
    op.drop_table("erp_rework_orders")
    op.drop_table("erp_ncrs")
