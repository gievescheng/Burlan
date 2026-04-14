"""Add production plans, material issues, and material issue items

Revision ID: erp_0003
Revises: erp_0002
Create Date: 2026-04-14
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "erp_0003"
down_revision = "erp_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── erp_production_plans ────────────────────────────
    op.create_table(
        "erp_production_plans",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("plan_no", sa.Text(), nullable=False),
        sa.Column("work_order_id", sa.Text(), sa.ForeignKey("erp_work_orders.id"), nullable=False),
        sa.Column("product_id", sa.Text(), sa.ForeignKey("erp_products.id"), nullable=False),
        sa.Column("route_id", sa.Text(), sa.ForeignKey("erp_process_routes.id"), nullable=True),
        sa.Column("planned_qty", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("completed_qty", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("unit", sa.Text(), nullable=False, server_default="pcs"),
        sa.Column("planned_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("planned_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("shift", sa.Text(), nullable=False, server_default=""),
        sa.Column("line_no", sa.Text(), nullable=False, server_default=""),
        sa.Column("assigned_to", sa.Text(), nullable=False, server_default=""),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("status", sa.Text(), nullable=False, server_default="draft"),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("updated_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_erp_production_plans_plan_no", "erp_production_plans", ["plan_no"], unique=True)
    op.create_index("ix_erp_production_plans_work_order_id", "erp_production_plans", ["work_order_id"])
    op.create_index("ix_erp_production_plans_product_id", "erp_production_plans", ["product_id"])
    op.create_index("ix_erp_production_plans_route_id", "erp_production_plans", ["route_id"])
    op.create_index("ix_erp_production_plans_status", "erp_production_plans", ["status"])

    # ── erp_material_issues ─────────────────────────────
    op.create_table(
        "erp_material_issues",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("issue_no", sa.Text(), nullable=False),
        sa.Column("work_order_id", sa.Text(), sa.ForeignKey("erp_work_orders.id"), nullable=True),
        sa.Column("production_plan_id", sa.Text(), sa.ForeignKey("erp_production_plans.id"), nullable=True),
        sa.Column("issue_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("issued_by", sa.Text(), nullable=False, server_default=""),
        sa.Column("received_by", sa.Text(), nullable=False, server_default=""),
        sa.Column("department", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.Text(), nullable=False, server_default="draft"),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("updated_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_erp_material_issues_issue_no", "erp_material_issues", ["issue_no"], unique=True)
    op.create_index("ix_erp_material_issues_work_order_id", "erp_material_issues", ["work_order_id"])
    op.create_index("ix_erp_material_issues_production_plan_id", "erp_material_issues", ["production_plan_id"])
    op.create_index("ix_erp_material_issues_status", "erp_material_issues", ["status"])

    # ── erp_material_issue_items ────────────────────────
    op.create_table(
        "erp_material_issue_items",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("issue_id", sa.Text(), sa.ForeignKey("erp_material_issues.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.Text(), sa.ForeignKey("erp_products.id"), nullable=False),
        sa.Column("seq", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("requested_qty", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("issued_qty", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("unit", sa.Text(), nullable=False, server_default="pcs"),
        sa.Column("lot_no", sa.Text(), nullable=False, server_default=""),
        sa.Column("warehouse", sa.Text(), nullable=False, server_default=""),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("updated_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_erp_material_issue_items_issue_id", "erp_material_issue_items", ["issue_id"])
    op.create_index("ix_erp_material_issue_items_product_id", "erp_material_issue_items", ["product_id"])


def downgrade() -> None:
    op.drop_table("erp_material_issue_items")
    op.drop_table("erp_material_issues")
    op.drop_table("erp_production_plans")
