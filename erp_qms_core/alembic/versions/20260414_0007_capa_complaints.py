"""Add CAPA and Customer Complaints (ISO 9001:2015 §10.2 + §9.1.2)

Revision ID: erp_0007
Revises: erp_0006
Create Date: 2026-04-14
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "erp_0007"
down_revision = "erp_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── erp_customer_complaints ─────────────────────────
    op.create_table(
        "erp_customer_complaints",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("complaint_no", sa.Text(), nullable=False),
        sa.Column("customer_id", sa.Text(), sa.ForeignKey("erp_customers.id"), nullable=False),
        sa.Column("product_id", sa.Text(), sa.ForeignKey("erp_products.id"), nullable=False),
        sa.Column("sales_order_id", sa.Text(), sa.ForeignKey("erp_sales_orders.id"), nullable=True),
        sa.Column("work_order_id", sa.Text(), sa.ForeignKey("erp_work_orders.id"), nullable=True),
        sa.Column("lot_no", sa.Text(), nullable=False, server_default=""),
        sa.Column("delivery_date", sa.Date(), nullable=True),
        sa.Column("claimed_qty", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("complaint_type", sa.Text(), nullable=False, server_default="quality"),
        sa.Column("severity", sa.Text(), nullable=False, server_default="minor"),
        sa.Column("subject", sa.Text(), nullable=False, server_default=""),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("customer_contact", sa.Text(), nullable=False, server_default=""),
        sa.Column("channel", sa.Text(), nullable=False, server_default="email"),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("received_by", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.Text(), nullable=False, server_default="received"),
        sa.Column("response_text", sa.Text(), nullable=False, server_default=""),
        sa.Column("responded_by", sa.Text(), nullable=False, server_default=""),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_by", sa.Text(), nullable=False, server_default=""),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("customer_satisfied", sa.Boolean(), nullable=True),
        sa.Column("requires_capa", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("updated_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_erp_customer_complaints_complaint_no", "erp_customer_complaints", ["complaint_no"], unique=True)
    op.create_index("ix_erp_customer_complaints_customer_id", "erp_customer_complaints", ["customer_id"])
    op.create_index("ix_erp_customer_complaints_product_id", "erp_customer_complaints", ["product_id"])
    op.create_index("ix_erp_customer_complaints_sales_order_id", "erp_customer_complaints", ["sales_order_id"])
    op.create_index("ix_erp_customer_complaints_work_order_id", "erp_customer_complaints", ["work_order_id"])
    op.create_index("ix_erp_customer_complaints_lot_no", "erp_customer_complaints", ["lot_no"])
    op.create_index("ix_erp_customer_complaints_complaint_type", "erp_customer_complaints", ["complaint_type"])
    op.create_index("ix_erp_customer_complaints_severity", "erp_customer_complaints", ["severity"])
    op.create_index("ix_erp_customer_complaints_status", "erp_customer_complaints", ["status"])
    op.create_index("ix_erp_customer_complaints_requires_capa", "erp_customer_complaints", ["requires_capa"])

    # ── erp_capas ───────────────────────────────────────
    op.create_table(
        "erp_capas",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("capa_no", sa.Text(), nullable=False),
        sa.Column("capa_type", sa.Text(), nullable=False, server_default="corrective"),
        sa.Column("source_type", sa.Text(), nullable=False, server_default="ncr"),
        sa.Column("ncr_id", sa.Text(), sa.ForeignKey("erp_ncrs.id"), nullable=True),
        sa.Column("complaint_id", sa.Text(), sa.ForeignKey("erp_customer_complaints.id"), nullable=True),
        sa.Column("source_ref", sa.Text(), nullable=False, server_default=""),
        sa.Column("subject", sa.Text(), nullable=False, server_default=""),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("severity", sa.Text(), nullable=False, server_default="minor"),
        sa.Column("root_cause_method", sa.Text(), nullable=False, server_default="5why"),
        sa.Column("root_cause", sa.Text(), nullable=False, server_default=""),
        sa.Column("similar_issues_check", sa.Text(), nullable=False, server_default=""),
        sa.Column("containment_action", sa.Text(), nullable=False, server_default=""),
        sa.Column("corrective_action", sa.Text(), nullable=False, server_default=""),
        sa.Column("preventive_action", sa.Text(), nullable=False, server_default=""),
        sa.Column("assigned_to", sa.Text(), nullable=False, server_default=""),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("effectiveness_check", sa.Text(), nullable=False, server_default=""),
        sa.Column("effectiveness_verified", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("verified_by", sa.Text(), nullable=False, server_default=""),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("risk_updated", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("qms_changes_required", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("status", sa.Text(), nullable=False, server_default="open"),
        sa.Column("closed_by", sa.Text(), nullable=False, server_default=""),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("updated_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_erp_capas_capa_no", "erp_capas", ["capa_no"], unique=True)
    op.create_index("ix_erp_capas_capa_type", "erp_capas", ["capa_type"])
    op.create_index("ix_erp_capas_source_type", "erp_capas", ["source_type"])
    op.create_index("ix_erp_capas_ncr_id", "erp_capas", ["ncr_id"])
    op.create_index("ix_erp_capas_complaint_id", "erp_capas", ["complaint_id"])
    op.create_index("ix_erp_capas_severity", "erp_capas", ["severity"])
    op.create_index("ix_erp_capas_due_date", "erp_capas", ["due_date"])
    op.create_index("ix_erp_capas_status", "erp_capas", ["status"])


def downgrade() -> None:
    op.drop_table("erp_capas")
    op.drop_table("erp_customer_complaints")
