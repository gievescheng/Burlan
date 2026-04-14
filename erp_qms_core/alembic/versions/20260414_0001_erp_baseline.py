"""ERP-QMS core baseline: master data + process stations/routes

Revision ID: erp_0001
Revises:
Create Date: 2026-04-14
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "erp_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── erp_customers ───────────────────────────────────
    op.create_table(
        "erp_customers",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("customer_code", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("short_name", sa.Text(), nullable=False, server_default=""),
        sa.Column("contact_person", sa.Text(), nullable=False, server_default=""),
        sa.Column("phone", sa.Text(), nullable=False, server_default=""),
        sa.Column("email", sa.Text(), nullable=False, server_default=""),
        sa.Column("address", sa.Text(), nullable=False, server_default=""),
        sa.Column("tax_id", sa.Text(), nullable=False, server_default=""),
        sa.Column("payment_terms", sa.Text(), nullable=False, server_default=""),
        sa.Column("currency", sa.Text(), nullable=False, server_default="TWD"),
        sa.Column("status", sa.Text(), nullable=False, server_default="active"),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("updated_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_erp_customers_customer_code", "erp_customers", ["customer_code"], unique=True)
    op.create_index("ix_erp_customers_name", "erp_customers", ["name"])
    op.create_index("ix_erp_customers_status", "erp_customers", ["status"])

    # ── erp_suppliers ───────────────────────────────────
    op.create_table(
        "erp_suppliers",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("supplier_code", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("short_name", sa.Text(), nullable=False, server_default=""),
        sa.Column("contact_person", sa.Text(), nullable=False, server_default=""),
        sa.Column("phone", sa.Text(), nullable=False, server_default=""),
        sa.Column("email", sa.Text(), nullable=False, server_default=""),
        sa.Column("address", sa.Text(), nullable=False, server_default=""),
        sa.Column("tax_id", sa.Text(), nullable=False, server_default=""),
        sa.Column("category", sa.Text(), nullable=False, server_default=""),
        sa.Column("eval_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("eval_result", sa.Text(), nullable=False, server_default=""),
        sa.Column("lead_time_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.Text(), nullable=False, server_default="active"),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("updated_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_erp_suppliers_supplier_code", "erp_suppliers", ["supplier_code"], unique=True)
    op.create_index("ix_erp_suppliers_name", "erp_suppliers", ["name"])
    op.create_index("ix_erp_suppliers_status", "erp_suppliers", ["status"])

    # ── erp_products ────────────────────────────────────
    op.create_table(
        "erp_products",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("product_code", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("category", sa.Text(), nullable=False, server_default=""),
        sa.Column("unit", sa.Text(), nullable=False, server_default="pcs"),
        sa.Column("unit_price", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("currency", sa.Text(), nullable=False, server_default="TWD"),
        sa.Column("spec", sa.Text(), nullable=False, server_default=""),
        sa.Column("drawing_no", sa.Text(), nullable=False, server_default=""),
        sa.Column("customer_part_no", sa.Text(), nullable=False, server_default=""),
        sa.Column("default_route_id", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False, server_default="active"),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("updated_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_erp_products_product_code", "erp_products", ["product_code"], unique=True)
    op.create_index("ix_erp_products_name", "erp_products", ["name"])
    op.create_index("ix_erp_products_category", "erp_products", ["category"])
    op.create_index("ix_erp_products_status", "erp_products", ["status"])

    # ── erp_process_stations ────────────────────────────
    op.create_table(
        "erp_process_stations",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("station_code", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("department", sa.Text(), nullable=False, server_default=""),
        sa.Column("station_type", sa.Text(), nullable=False, server_default="production"),
        sa.Column("capacity_per_hour", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("requires_inspection", sa.Text(), nullable=False, server_default="no"),
        sa.Column("status", sa.Text(), nullable=False, server_default="active"),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("updated_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_erp_process_stations_station_code", "erp_process_stations", ["station_code"], unique=True)
    op.create_index("ix_erp_process_stations_name", "erp_process_stations", ["name"])
    op.create_index("ix_erp_process_stations_status", "erp_process_stations", ["status"])

    # ── erp_process_routes ──────────────────────────────
    op.create_table(
        "erp_process_routes",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("route_code", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("version", sa.Text(), nullable=False, server_default="1.0"),
        sa.Column("status", sa.Text(), nullable=False, server_default="active"),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("updated_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_erp_process_routes_route_code", "erp_process_routes", ["route_code"], unique=True)
    op.create_index("ix_erp_process_routes_name", "erp_process_routes", ["name"])
    op.create_index("ix_erp_process_routes_status", "erp_process_routes", ["status"])

    # ── erp_process_route_steps ─────────────────────────
    op.create_table(
        "erp_process_route_steps",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("route_id", sa.Text(), nullable=False),
        sa.Column("station_id", sa.Text(), nullable=False),
        sa.Column("seq", sa.Integer(), nullable=False),
        sa.Column("standard_time_min", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("setup_time_min", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("is_optional", sa.Text(), nullable=False, server_default="no"),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("updated_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("route_id", "seq", name="uq_route_step_seq"),
    )
    op.create_index("ix_erp_process_route_steps_route_id", "erp_process_route_steps", ["route_id"])
    op.create_index("ix_erp_process_route_steps_station_id", "erp_process_route_steps", ["station_id"])


def downgrade() -> None:
    op.drop_table("erp_process_route_steps")
    op.drop_table("erp_process_routes")
    op.drop_table("erp_process_stations")
    op.drop_table("erp_products")
    op.drop_table("erp_suppliers")
    op.drop_table("erp_customers")
