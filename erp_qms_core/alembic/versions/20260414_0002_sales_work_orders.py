"""Add sales orders, sales order items, and work orders

Revision ID: erp_0002
Revises: erp_0001
Create Date: 2026-04-14
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "erp_0002"
down_revision = "erp_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── erp_sales_orders ────────────────────────────────
    op.create_table(
        "erp_sales_orders",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("order_no", sa.Text(), nullable=False),
        sa.Column("customer_id", sa.Text(), sa.ForeignKey("erp_customers.id"), nullable=False),
        sa.Column("order_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("required_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("currency", sa.Text(), nullable=False, server_default="TWD"),
        sa.Column("total_amount", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("status", sa.Text(), nullable=False, server_default="draft"),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("updated_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_erp_sales_orders_order_no", "erp_sales_orders", ["order_no"], unique=True)
    op.create_index("ix_erp_sales_orders_customer_id", "erp_sales_orders", ["customer_id"])
    op.create_index("ix_erp_sales_orders_status", "erp_sales_orders", ["status"])

    # ── erp_sales_order_items ───────────────────────────
    op.create_table(
        "erp_sales_order_items",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("order_id", sa.Text(), sa.ForeignKey("erp_sales_orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.Text(), sa.ForeignKey("erp_products.id"), nullable=False),
        sa.Column("seq", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("quantity", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("unit_price", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("unit", sa.Text(), nullable=False, server_default="pcs"),
        sa.Column("line_amount", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("updated_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_erp_sales_order_items_order_id", "erp_sales_order_items", ["order_id"])
    op.create_index("ix_erp_sales_order_items_product_id", "erp_sales_order_items", ["product_id"])

    # ── erp_work_orders ─────────────────────────────────
    op.create_table(
        "erp_work_orders",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("wo_no", sa.Text(), nullable=False),
        sa.Column("sales_order_id", sa.Text(), sa.ForeignKey("erp_sales_orders.id"), nullable=True),
        sa.Column("sales_order_item_id", sa.Text(), sa.ForeignKey("erp_sales_order_items.id"), nullable=True),
        sa.Column("product_id", sa.Text(), sa.ForeignKey("erp_products.id"), nullable=False),
        sa.Column("route_id", sa.Text(), sa.ForeignKey("erp_process_routes.id"), nullable=True),
        # 追蹤欄位
        sa.Column("lot_no", sa.Text(), nullable=False, server_default=""),
        sa.Column("wafer_lot", sa.Text(), nullable=False, server_default=""),
        sa.Column("glass_id", sa.Text(), nullable=False, server_default=""),
        sa.Column("carrier_id", sa.Text(), nullable=False, server_default=""),
        # 數量
        sa.Column("planned_qty", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("completed_qty", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("scrap_qty", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("unit", sa.Text(), nullable=False, server_default="pcs"),
        # 排程
        sa.Column("planned_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("planned_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_end", sa.DateTime(timezone=True), nullable=True),
        # 責任
        sa.Column("priority", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("assigned_to", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.Text(), nullable=False, server_default="draft"),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("updated_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_erp_work_orders_wo_no", "erp_work_orders", ["wo_no"], unique=True)
    op.create_index("ix_erp_work_orders_sales_order_id", "erp_work_orders", ["sales_order_id"])
    op.create_index("ix_erp_work_orders_sales_order_item_id", "erp_work_orders", ["sales_order_item_id"])
    op.create_index("ix_erp_work_orders_product_id", "erp_work_orders", ["product_id"])
    op.create_index("ix_erp_work_orders_route_id", "erp_work_orders", ["route_id"])
    op.create_index("ix_erp_work_orders_lot_no", "erp_work_orders", ["lot_no"])
    op.create_index("ix_erp_work_orders_status", "erp_work_orders", ["status"])


def downgrade() -> None:
    op.drop_table("erp_work_orders")
    op.drop_table("erp_sales_order_items")
    op.drop_table("erp_sales_orders")
